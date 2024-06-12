from custom_events_lib.event_type import EventType
from custom_events_lib.notebook_context import NotebookContext
from custom_exceptions_lib.exceptions import DeltaTableWriteException
from pyspark.sql.types import StructType, StructField, StringType, BooleanType, MapType, TimestampType
from pyspark.sql.functions import current_timestamp, lit, create_map, col
from pyspark.sql import DataFrame, Row, SparkSession

# Constants for schema field names
NOTEBOOK_NAME = "notebook_name"
ACTIVITY_ID = "activity_id"
ACTIVITY_NAME = "activity_name"
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
                StructField(ACTIVITY_NAME, StringType(), nullable=False),
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

        try:
            df.write.format("delta").mode("append").saveAsTable(table_name)
        except Exception as e:
            raise DeltaTableWriteException(f"Failed to write DataFrame to Delta table {table_name}: {e}") from e

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
                    .withColumn(ACTIVITY_NAME, lit(notebook_context.activity_name))\
                    .withColumn(IS_FOR_PIPELINE, lit(notebook_context.is_for_pipeline))\
                    .withColumn(USER_NAME, lit(notebook_context.user_name))

    def save_events(self, df: DataFrame, notebook_context: NotebookContext, table_name: str) -> None:
        """
        Saves events to a Delta table with context decoration.

        Parameters:
        - df (DataFrame): The DataFrame of custom events.
        - notebook_context (NotebookContext): The notebook context.
        - table_name (str): The name of the Delta table to save events to.
        """
        decorated_df = EventsPersistenceManager._decorate_with_context(df, notebook_context)
        self._write_with_schema(decorated_df, table_name)

    def save_missing_data_events(self, spark: SparkSession, df: DataFrame, notebook_context: NotebookContext, table_name: str) -> None:
        """
        Saves missing data events to the specified table.

        Parameters:
        - spark (SparkSession): The Spark session.
        - df (DataFrame): The DataFrame containing the missing data identifiers.
        - notebook_context (NotebookContext): The notebook context.
        - table_name (str): The name of the Delta table to save the events to.

        Returns:
            None
        """
        columns = df.columns
        map_expr = create_map(*[item for sublist in [[lit(col_name), col(col_name)] for col_name in columns] for item in sublist])

        missing_data_events_df = df.select(map_expr.alias("custom_properties"))\
            .withColumn("event", lit(EventType.MISSING_DATA.value))\
            .withColumn("timestamp", current_timestamp())

        # reorder columns to match the schema
        missing_data_events_df = missing_data_events_df.select(
            "event",
            "custom_properties",
            "timestamp"
        )
        missing_data_events_df = spark.createDataFrame(missing_data_events_df.rdd, schema=self.event_schema)
        self.save_events(missing_data_events_df, notebook_context, table_name)

    def save_exception_event(self, spark: SparkSession, exception: Exception, notebook_context: NotebookContext, table_name: str) -> None:
        """
        Saves an exception event to the specified table.

        Parameters:
        - spark (SparkSession): The Spark session.
        - exception (Exception): The exception object to be saved.
        - notebook_context (NotebookContext): The context of the notebook where the exception occurred.
        - table_name (str): The name of the Delta table to save the event to.

        Returns:
            None
        """
        exception_type = str(type(exception).__name__)
        exception_message = str(exception)

        exception_row = Row(custom_properties={"exception_type": exception_type, "exception_message": exception_message})

        exception_event_df = spark.createDataFrame([exception_row])\
            .withColumn("event", lit(EventType.EXCEPTION.value))\
            .withColumn("timestamp", current_timestamp())

        # reorder columns to match the schema
        exception_event_df = exception_event_df.select(
            "event",
            "custom_properties",
            "timestamp"
        )
        exception_event_df = spark.createDataFrame(exception_event_df.rdd, schema=self.event_schema)

        self.save_events(exception_event_df, notebook_context, table_name)
