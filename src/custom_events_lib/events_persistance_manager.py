from custom_events_lib.context import Context
from custom_exceptions_lib.exceptions import DeltaTableWriteException
from datetime import datetime
import pytz
from pyspark.sql.types import StructType, StructField, StringType, MapType, TimestampType
from pyspark.sql.functions import current_timestamp, lit, create_map, col
from pyspark.sql import DataFrame, Row, SparkSession

# Constants for schema field names
EVENT = "event"
CUSTOM_PROPERTIES = "custom_properties"
TIMESTAMP = "utc_timestamp"
ACTIVITY_NAME = "activity_name"
USER_NAME = "user_name"
ENVIRONMENT = "environment"

# Constants for event names
MISSING_DATA_EVENT = "MissingData"
EXCEPTION_EVENT = "Exception"


class EventsPersistenceManager:
    def __init__(self):
        self.event_schema = StructType([
                StructField(EVENT, StringType(), nullable=False),
                StructField(CUSTOM_PROPERTIES, MapType(StringType(), StringType()), nullable=True),
                StructField(TIMESTAMP, TimestampType(), nullable=False),
        ])
        self.context_schema = StructType([
                StructField(ACTIVITY_NAME, StringType(), nullable=False),
                StructField(USER_NAME, StringType(), nullable=False),
                StructField(ENVIRONMENT, MapType(StringType(), StringType(), False), nullable=False),
            ])

    def _write_with_schema(self, df: DataFrame, table_name: str) -> None:
        """
        Writes a DataFrame to a Delta table with a specified schema.

        Parameters:
        - df (DataFrame): The DataFrame to write.
        - table_name (str): The name of the Delta table.

        Raises:
        - ValueError: If the DataFrame schema does not match the expected schema.
        - DeltaTableWriteException: If the DataFrame cannot be written to the Delta table.
        """

        merged_schema = StructType(self.event_schema.fields + self.context_schema.fields)
        if (len(df.columns) != len(merged_schema.fields)):
            raise ValueError(f"DataFrame doesn't match the expected columns, \ngot: {df.columns}, \nexpected {merged_schema.fields}")

        # reorder columns to match the schema
        df_to_save = df.select(*merged_schema.fieldNames())

        if str(df_to_save.schema) != str(merged_schema):
            raise ValueError(f"DataFrame schema doesn't match the expected table schema, \ngot: {df_to_save.schema}, \nexpected {merged_schema}")

        try:
            df_to_save.write.format("delta").mode("append").saveAsTable(table_name)
        except Exception as e:
            raise DeltaTableWriteException(f"Failed to write DataFrame to Delta table {table_name}: {e}") from e

    def _decorate_with_context(self, df: DataFrame, context: Context) -> DataFrame:
        """
        Decorates a DataFrame with additional context columns.

        Parameters:
        - df (DataFrame): The DataFrame to decorate.
        - context (Context): The context to use for decoration.

        Returns:
        - DataFrame: The decorated DataFrame.
        """
        environment_map_columns = []
        for k, v in context.environment.items():
            environment_map_columns.extend([lit(k), lit(v)])

        return df.withColumn(ACTIVITY_NAME, lit(context.activity_name))\
            .withColumn(USER_NAME, lit(context.user_name))\
            .withColumn(ENVIRONMENT, create_map(*environment_map_columns))

    def save_events(self, df: DataFrame, context: Context, table_name: str) -> None:
        """
        Saves events to a Delta table with context decoration.

        Parameters:
        - df (DataFrame): The DataFrame of custom events.
        - context (Context): The context to decorate the events with.
        - table_name (str): The name of the Delta table to save events to.

        Returns:
            None
        """
        decorated_df = self._decorate_with_context(df, context)
        self._write_with_schema(decorated_df, table_name)

    def save_missing_data_events(self, spark: SparkSession, df: DataFrame, context: Context, table_name: str) -> None:
        """
        Saves missing data events to the specified table.

        Parameters:
        - spark (SparkSession): The Spark session.
        - df (DataFrame): The DataFrame containing the missing data identifiers.
        - context (Context): The context to decorate the events with.
        - table_name (str): The name of the Delta table to save the events to.

        Returns:
            None
        """
        columns = df.columns
        map_expr = create_map(*[item for sublist in [[lit(col_name), col(col_name)] for col_name in columns] for item in sublist])

        missing_data_events_df = df.select(map_expr.alias(CUSTOM_PROPERTIES))\
            .withColumn(EVENT, lit(MISSING_DATA_EVENT))\
            .withColumn(TIMESTAMP, current_timestamp())

        # reorder columns to match the event schema
        missing_data_events_df = missing_data_events_df.select(*self.event_schema.fieldNames())

        missing_data_events_df = spark.createDataFrame(missing_data_events_df.rdd, schema=self.event_schema)

        self.save_events(missing_data_events_df, context, table_name)

    def save_exception_event(self, spark: SparkSession, exception: Exception, context: Context, table_name: str) -> None:
        """
        Saves an exception event to the specified table.

        Parameters:
        - spark (SparkSession): The Spark session.
        - exception (Exception): The exception object to be saved.
        - context (Context): The context to decorate the event with.
        - table_name (str): The name of the Delta table to save the event to.

        Raises:
        - Exception: The original exception is re-raised after saving the exception event.
        """
        exception_type = str(type(exception).__name__)
        exception_message = str(exception)

        data = [Row(
            EVENT=EXCEPTION_EVENT,
            CUSTOM_PROPERTIES={"exception_type": exception_type, "exception_message": exception_message},
            TIMESTAMP=datetime.now(pytz.utc)
        )]
        exception_event_df = spark.createDataFrame(data, schema=self.event_schema)

        self.save_events(exception_event_df, context, table_name)

        # raise original exception to be visible in the notebook
        raise exception
