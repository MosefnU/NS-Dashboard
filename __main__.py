import pandas as pd

def main():

    df = pd.read_csv("Poordata_case_DE.csv", sep=";")
    print(df.head())

if __name__ == "__main__":
    main()