from pyspark.sql import DataFrame
from pyspark.sql.functions import col


def find_missing_values(df: DataFrame, column_name: str, *identifiers) -> DataFrame:
    null_values_df = df.filter(col(column_name).isNull())

    # Select columns that should be included in the result DataFrame
    result_df = null_values_df.select(*identifiers)

    return result_df
