from custom_events_lib.notebook_context import NotebookContext
from pyspark.sql.types import StructType, StructField, StringType, BooleanType, MapType, TimestampType
from pyspark.sql.functions import lit
from pyspark.sql import DataFrame

# Constants for schema field names
NOTEBOOK_NAME = "notebook_name"
ACTIVITY_ID = "activity_id"
IS_FOR_PIPELINE = "is_for_pipeline"
USER_NAME = "user_name"


class EventsPersistenceManager:
    def __init__(self):
        self.event_schema = StructType([
                StructField("event", StringType(), nullable=False),
                StructField("custom_properties", MapType(StringType(), StringType()), nullable=True),
                StructField("timestamp", TimestampType(), nullable=False),
            ])

        self.context_schema = StructType([
                StructField(NOTEBOOK_NAME, StringType(), nullable=False),
                StructField(ACTIVITY_ID, StringType(), nullable=False),
                StructField(IS_FOR_PIPELINE, BooleanType(), nullable=False),
                StructField(USER_NAME, StringType(), nullable=False),
            ])

    def _write_with_schema(self, df: DataFrame, table_name: str) -> None:
        """
        Writes a DataFrame to a Delta table with a specified schema.

        Parameters:
        - df (DataFrame): The DataFrame to write.
        - table_name (str): The name of the Delta table.

        Raises:
        - ValueError: If the DataFrame schema does not match the expected schema.
        """
        merged_schema = StructType(self.event_schema.fields + self.context_schema.fields)

        if str(df.schema) != str(merged_schema):
            raise ValueError(f"DataFrame schema doesn't match the expected table schema, got: {df.schema}, expected {merged_schema}")

        df.write.format("delta").mode("append").saveAsTable(table_name)

    @staticmethod
    def _decorate_with_context(df: DataFrame, notebook_context: NotebookContext) -> DataFrame:
        """
        Decorates a DataFrame with additional context columns.

        Parameters:
        - df (DataFrame): The DataFrame to decorate.

        Returns:
        - DataFrame: The decorated DataFrame.
        """
        return df.withColumn(NOTEBOOK_NAME, lit(notebook_context.notebook_name))\
                    .withColumn(ACTIVITY_ID, lit(notebook_context.activity_id))\
                    .withColumn(IS_FOR_PIPELINE, lit(notebook_context.is_for_pipeline))\
                    .withColumn(USER_NAME, lit(notebook_context.user_name))

    def save_events(self, df: DataFrame, notebook_context: NotebookContext, table_name: str) -> None:
        """
        Saves events to a Delta table with context decoration.

        Parameters:
        - df (DataFrame): The DataFrame of custom events.
        - table_name (str): The name of the Delta table to save events to.
        """
        decorated_df = EventsPersistenceManager._decorate_with_context(df, notebook_context)
        self._write_with_schema(decorated_df, table_name)
