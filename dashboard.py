import streamlit as st
import sqlite3
import pandas as pd


    
db_file = 'transactions.db'
#Create header and subheader
st.title("Kritieke prestatie indicatoren 2025")
st.subheader("Gebaseerd op barcode scans op 24 maart 2020")
conn = sqlite3.connect(db_file)

# Haal het aantal reizen op
query = f"""
    SELECT * FROM stations
"""
stations_df = pd.read_sql_query(query, conn)
conn.close()

# Filter stations buiten NL eruit
stations_buiten_nl =  ['frankfurt(m)flugh.','frankfurt(main)','köln','mariënberg','praha']
stations_nl_df = stations_df.query(f"STATION != '0' and STATION not in {stations_buiten_nl}")

## Toon reizen in Nederland
aantal_check_ins = int(stations_nl_df['passengers_in'].sum())
aantal_check_outs = int(stations_nl_df['passengers_out'].sum())
aantal_reizen = max(aantal_check_ins, aantal_check_outs)
st.subheader("1. Reizen in Nederland")
reizen, reis_in, reis_uit = st.columns(3)
reizen.metric(label="Aantal reizen", value=aantal_reizen, delta=None, delta_color="normal")
reis_in.metric(label="Aantal check-ins", value=aantal_check_ins, delta=None, delta_color="normal")
reis_uit.metric(label="Aantal check-outs", value=aantal_check_outs, delta=(aantal_check_outs-aantal_check_ins), delta_color="normal")
    

# # Toon top 10 drukste stations in Nederland
st.subheader("2. Top drukste stations in Nederland")
topx = st.slider("Aantal stations", 1, 100, 10, on_change=None)
st.write(f"Top {topx} drukste stations in Nederland gebaseerd op het aantal reizigers op het aantal check-ins en check-outs.")
stations_nl_df.sort_values(by='passenger_count', ascending=False, inplace=True)

station_table_data = []

for i in range(len(stations_nl_df)):
    if not stations_nl_df.iloc[i]['passenger_count'] > 0:
        continue

    # Voeg station data toe aan de lijst
    station_table_data.append(
        {
            "#": i + 1,
            "Station": stations_nl_df.iloc[i]['STATION'].capitalize(),
            "Reizigers": int(stations_nl_df.iloc[i]['passenger_count']),
            "Check-ins": int(stations_nl_df.iloc[i]['passengers_in']),
            "Check-uits": int(stations_nl_df.iloc[i]['passengers_out'])
        }
    )
st.data_editor(data=station_table_data[:topx])


