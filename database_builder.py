import pandas as pd
import transform_data
import sqlite3

def main():
    db_name = 'transactions.db'
    transactions_table = 'transactions'
    stations_table = 'stations'
    journeys_table = 'journeys'

    #build_transactions_table(db_name, transactions_table)

    #build_stations_table(db_name, transactions_table, stations_table)

    build_journeys_table(db_name, journeys_table)

def build_journeys_table(db_name, journeys_table='journeys'):
    """
    Build a journeys table from the transactions data.
    This function is currently a placeholder and does not implement any logic.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    # --FULL JOINS zijn niet ondersteund in SQLite, dus we gebruiken LEFT JOIN
    # --Dit betekent dat journeys met alleen een check-out worden opgeslagen
    # -- als journey met alleen een check-in.
    query = f"""
    SELECT 
        A.[ticket id] AS TicketID,
        A.station AS check_in,
        B.station AS check_uit,
        A.[HEENREIS VERTREKSTATION],
        A.[HEENREIS AANKOMSTSTATION],
        A.[TERUGREIS VERTREKSTATION],
        A.[TERUGREIS AANKOMSTSTATION],
        A.[Ticket type] AS ticket_type
    FROM transactions A
    LEFT JOIN transactions B
        ON A.[ticket id] = B.[ticket id]
        AND A.richting <> B.richting
        AND B.[Ticket type] <> 'B'
    WHERE A.richting = 'unpaid'
        OR NOT EXISTS (
            SELECT 1
            FROM transactions C
            WHERE C.[ticket id] = A.[ticket id] AND C.richting = 'unpaid'
        )
    ORDER BY A.[ticket id], A.[HEENREIS VERTREKSTATION] ASC;
            """
    journeys_df = pd.read_sql_query(query, conn)
    
   # Voeg een kolom toe om aan te geven of de reis compleet is
    journeys_df['comlpete journey'] = ((
        # De reis is compleet als de check-in en check-out overeenkomen met de heenreis of terugreis
        # Dwz de check in is gelijk aan het vertrekstation van de heenreis of terugreis
        # en de check out is gelijk aan het aankomststation van de heenreis of terugreis.
            (journeys_df['check_in'] == journeys_df['HEENREIS VERTREKSTATION'])
        & (journeys_df['check_uit'] == journeys_df['HEENREIS AANKOMSTSTATION'])
        ) | (
            (journeys_df['check_in'] == journeys_df['TERUGREIS VERTREKSTATION'])
        & (journeys_df['check_uit'] == journeys_df['TERUGREIS AANKOMSTSTATION'])
        ))
        
    conn.close()
    
    pandas_to_sqlite(journeys_df, journeys_table, db_name)
    print(f"Building {journeys_table} table in {db_name} completed.")
    

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