import duckdb

def set_connection():
    return duckdb.connect('my.db')