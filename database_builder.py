import pandas as pd
import transform_data
import sqlite3

def main():
    db_name = 'transactions.db'
    transactions_table = 'transactions'
    stations_table = 'stations'

    build_transactions_table(db_name, transactions_table)

    build_stations_table(db_name, transactions_table, stations_table)

def build_transactions_table(db_name, transactions_table):
    # Load and clean the data
    df = pd.read_csv("data.csv", sep=";")
    df = transform_data.clean_data(df)
    
    # Place data into SQLite database
    pandas_to_sqlite(df, transactions_table, db_name)

def build_stations_table(db_name,transactions_table='transactions', stations_table='stations'):
    
    # Add stations table
    create_stations_table(transactions_table, db_name, stations_table)

    # Add chreck-ins and check-outs to stations table
    add_check_ins_and_outs(db_name, transactions_table ,stations_table)

    #add transaction count
    add_transaction_numbers_to_stations_table(db_name, stations_table)

def add_transaction_numbers_to_stations_table(db_file, stations_table):
    """
    Add transaction numbers to the stations table.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f"""
        ALTER TABLE [{stations_table}]
        ADD COLUMN transaction_count INTEGER DEFAULT 0;
            """)
    cursor.execute(f"""
        ALTER TABLE [{stations_table}]
        ADD COLUMN passenger_count INTEGER DEFAULT 0;
            """)
    cursor.execute(f"""
                   UPDATE [{stations_table}] SET transaction_count = check_ins + check_outs;
                   """)
    cursor.execute(f"""
                   UPDATE [{stations_table}] SET passenger_count = passengers_in + passengers_out;
                   """)
    conn.commit()
    conn.close()
    print("Transaction counts updated in stations table.")

def add_check_ins_and_outs(db_file, source_table, target_table):
    """
    Count the number of occurrences of each station in the transactions table.
    """
    conn = sqlite3.connect(db_file)

    query = f"""
        SELECT station,
            (
                SELECT COUNT(station) FROM {source_table} t2
                WHERE richting='paid' AND t2.station = t1.station
                ) AS check_ins,
            (
                SELECT COUNT(station) FROM {source_table} t3
                WHERE richting='unpaid' AND t3.station = t1.station
                ) AS check_outs,
            (
                SELECT COUNT(station) * [aantal passagiers] FROM {source_table} t2
                WHERE richting='paid' AND t2.station = t1.station AND [aantal passagiers] IS NOT NULL
                ) AS passengers_in,
            (
                SELECT COUNT(station) * [aantal passagiers] FROM {source_table} t3
                WHERE richting='unpaid' AND t3.station = t1.station AND [aantal passagiers] IS NOT NULL
                ) AS passengers_out
        FROM {target_table} t1
        WHERE station IS NOT NULL
        AND station != '0'
        GROUP BY station
    """
    result_df = pd.read_sql_query(query, conn)
    conn.close()

    # Save the result to the stations table
    pandas_to_sqlite(result_df, target_table, db_file)

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

if __name__ == "__main__":
    main()