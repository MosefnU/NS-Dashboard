import sqlite3
import pandas as pd

def main():
    pass

def new_sqlite_db(db_file):
    """
    Create a new SQLite database file.
    
    :param db_file: The name of the SQLite database file to create.
    """
    conn = sqlite3.connect(db_file)
    conn.close()
    print(f"Database {db_file} created successfully.")

def pandas_to_sqlite(df, table_name, db_file):
    """
    Save a pandas DataFrame to a SQLite database table.
    
    :param df: The pandas DataFrame to save.
    :param table_name: The name of the table in the SQLite database.
    :param db_file: The SQLite database file.
    """
    conn = sqlite3.connect(db_file)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print(f"DataFrame saved to {table_name} in {db_file}.")

if __name__ == "__main__":
    main()