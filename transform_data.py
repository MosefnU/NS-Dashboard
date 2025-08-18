import pandas as pd

def main():

    df = get_data('data.csv')
    df = clean_data(df)
    counts = df.value_counts("STATION")
    print(counts.head(10))

def clean_data(df):
    """
    Cleans the DataFrame by cleaning to column names and converting '~STATION' values to lowercase.
    
    :param df: DataFrame containing the data.
    :return: Cleaned DataFrame with '~STATION' columns in lowercase.
    """
    df = clean_column_names(df)
    df = stations_to_lowercase(df)
    return df

def clean_column_names(df):
    """
    Cleans the column names by removing leading and trailing spaces.
    
    :param df: DataFrame containing the data.
    :return: DataFrame with cleaned column names.
    """
    df.columns = df.columns.str.strip()
    return df

def stations_to_lowercase(df):
    """
    Converts the '~STATION' columns to lowercase.
    
    :param df: DataFrame containing the data.
    :return: DataFrame with the '~STATION' columns in lowercase.
    """
    df['STATION '] = df['STATION'].str.lower()
    df['HEENREIS VERTREKSTATION'] = df['HEENREIS VERTREKSTATION'].str.lower()
    df['TERUGREIS VERTREKSTATION'] = df['TERUGREIS VERTREKSTATION'].str.lower()
    df['HEENREIS AANKOMSTSTATION'] = df['HEENREIS AANKOMSTSTATION'].str.lower()
    df['TERUGREIS AANKOMSTSTATION'] = df['TERUGREIS AANKOMSTSTATION'].str.lower()
    return df

def get_data(path_to_csv):
    """
    Reads a CSV file and returns a DataFrame.
    
    :param path_to_csv: Path to the CSV file.
    :return: DataFrame containing the data from the CSV file.
    """
    return pd.read_csv(path_to_csv, sep=";")

if __name__ == "__main__":
    main()