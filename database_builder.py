import pandas as pd
import transform_data
import database_builder

def main():

    # Load and clean the data
    df = pd.read_csv("data.csv", sep=";")
    df = transform_data.clean_data(df)

    print(df.tail())
    
    # Place data into SQLite database
    database_builder.pandas_to_sqlite(df, 'transactions', 'transactions.db')

    # Add stations table
    database_builder.create_stations_table('transactions', 'transactions.db')

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

def create_stations_table(source_table, db_file, stations_table='stations'):
    """
    Create a stations table with unique station_id and station_name from transactions.
    """
    conn = sqlite3.connect(db_file)

    # Extract unique stations
    query = f"SELECT DISTINCT [station id], station FROM {source_table}"
    stations_df = pd.read_sql_query(query, conn)
    # Save to new table
    stations_df.to_sql(stations_table, conn, if_exists='replace', index=False)
    conn.close()
    print(f"Stations table '{stations_table}' created in {db_file}.")

# Example usage:
# create_stations_table('transactions', 'your_database.db')

if __name__ == "__main__":
    main()