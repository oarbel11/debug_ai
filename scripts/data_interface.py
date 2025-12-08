# data_interface.py

# Assumes get_db_connection returns a suitable connection object (DuckDB, Spark, Cursor etc.)
# You need to develop get_db_connection to return the correct connection object.

def execute_generic_query(query: str, params: list = None):
    """
    Executes a generic query and returns the results as a DataFrame.
    Works for DuckDB, Spark, or any other platform.
    """
    con = get_db_connection()  # Get generic connection

    # Generic execution logic (platform specific):
    if DB_CONFIGURATION.get("type") == "duckdb":
        # DuckDB: Uses fetchdf
        return con.execute(query, params).fetchdf()

    elif DB_CONFIGURATION.get("type") == "databricks":
        # Databricks: Uses Spark/ODBC connection
        # Requires Databricks Connect or Driver
        # return spark.sql(query).toPandas()
        pass

    else:
        raise NotImplementedError("Execution logic for this platform is missing.")