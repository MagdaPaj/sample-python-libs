from pyspark.sql import DataFrame
from pyspark.sql.functions import col
import pkg_resources

def find_missing_values(df: DataFrame, column_name: str, *identifiers) -> DataFrame:
    null_values_df = df.filter(col(column_name).isNull())

    # Select columns that should be included in the result DataFrame
    result_df = null_values_df.select(*identifiers)

    return result_df


def get_package_version(package_name):
    try:
        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        return "Package not found"
