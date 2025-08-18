import pandas as pd
import transform_data

def main():

    df = pd.read_csv("data.csv", sep=";")
    df = transform_data.clean_data(df)
    print(df.head())
    print(df.columns)
    counts = df.value_counts("STATION")
    print(counts)

def top_ten_stations(df):
    """
    Returns the top ten stations based on the number of ticketscans.
    
    :param df: DataFrame containing the data.
    :return: Series with the top ten stations and their counts.
    """
    return df['STATION '].value_counts().head(10)

if __name__ == "__main__":
    main()