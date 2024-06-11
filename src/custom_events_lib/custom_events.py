from pyspark.sql.types import StructType, StructField, StringType, BooleanType, MapType, TimestampType
from pyspark.sql.functions import lit
from pyspark.sql import DataFrame


NOTEBOOK_NAME = "notebook_name"
ACTIVITY_ID = "activity_id"
IS_FOR_PIPELINE = "is_for_pipeline"
USER_NAME = "user_name"

event_schema = StructType([
        StructField("event", StringType(), False),
        StructField("custom_properties", MapType(StringType(), StringType()), True),
        StructField("timestamp", TimestampType(), False),
    ])

context_schema = StructType([
        StructField(NOTEBOOK_NAME, StringType(), False),
        StructField(ACTIVITY_ID, StringType(), False),
        StructField(IS_FOR_PIPELINE, BooleanType(), False),
        StructField(USER_NAME, StringType(), False),
    ])


def _write_with_schema(df: DataFrame, table_name: str) -> None:
    merged_schema = StructType(event_schema.fields + context_schema.fields)

    if str(df.schema) != str(merged_schema):
        raise ValueError(f"DataFrame schema doesn't match the expected table schema, got: {df.schema}, expected {merged_schema}")

    df.write.format("delta").mode("append").saveAsTable(table_name)


def _decorate_with_context(df: DataFrame) -> DataFrame:
    return df.withColumn(NOTEBOOK_NAME, lit(mssparkutils.runtime.context['currentNotebookName']))\
                .withColumn(ACTIVITY_ID, lit(mssparkutils.runtime.context['activityId']))\
                .withColumn(IS_FOR_PIPELINE, lit(mssparkutils.runtime.context['isForPipeline']))\
                .withColumn(USER_NAME, lit(mssparkutils.env.getUserName()))


def save_custom_events(df: DataFrame, table_name: str) -> None:
    decorated_df = _decorate_with_context(df)
    _write_with_schema(decorated_df, table_name)
