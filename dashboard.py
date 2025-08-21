import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


    
db_file = 'transactions.db'
#Create header and subheader
st.title("Kritieke prestatie indicatoren 2025")
st.write("Gebaseerd op barcode scans op 24 maart 2020")
conn = sqlite3.connect(db_file)

# Haal het aantal reizen op
query = f"""
    SELECT * FROM stations
"""
stations_df = pd.read_sql_query(query, conn)

# Haal de journeys op
query = f"""
    SELECT * FROM journeys
"""
journeys_df = pd.read_sql_query(query, conn)

# Haal de transacties op
transactions_df = pd.read_sql_query("SELECT * FROM transactions", conn)
conn.close()

# Filter stations buiten NL eruit
stations_buiten_nl =  ['frankfurt(m)flugh.','frankfurt(main)','köln','mariënberg','praha']
stations_nl_df = stations_df.query(f"STATION != '0' and STATION not in {stations_buiten_nl}")

## Toon reizen in Nederland
# aantal_check_ins = int(stations_nl_df['passengers_in'].sum())
# aantal_check_outs = int(stations_nl_df['passengers_out'].sum())
# aantal_reizen = max(aantal_check_ins, aantal_check_outs)
# st.subheader("0. Reizen in Nederland")
# reizen, reis_in, reis_uit = st.columns(3)
# reizen.metric(label="Aantal reizen", value=aantal_reizen, delta=None, delta_color="normal")
# reis_in.metric(label="Aantal check-ins", value=aantal_check_ins, delta=None, delta_color="normal")
# reis_uit.metric(label="Aantal check-uits", value=aantal_check_outs, delta=(aantal_check_outs-aantal_check_ins), delta_color="normal")

## Toon reizen in Nederland 2
#Totaal aantal reizen
aantal_reizen = journeys_df.shape[0]

# Aantal reizen volledig binnen Nederland
query = f"check_in not in {stations_buiten_nl} and check_uit not in {stations_buiten_nl}"
aantal_reizen_NL = journeys_df.query(query).shape[0]

# Aantal grensoverschrijdende reizen
query = f"(check_in in {stations_buiten_nl} or check_uit in {stations_buiten_nl})"
aantal_reizen_grensoverschrijdend = journeys_df.query(query).shape[0]


st.subheader("1. Reizen in Nederland en internationaal")

reizen, reis_in, reis_uit = st.columns(3)
reizen.metric(label="Aantal reizen", value=aantal_reizen, delta=None, delta_color="normal")
reis_in.metric(label="Waarvan binnenland", value=aantal_reizen_NL, delta=None, delta_color="normal")
reis_uit.metric(label="Waarvan internationaal", value=aantal_reizen_grensoverschrijdend, delta=None, delta_color="normal")
reisnummer, reisweergave = st.columns(2)

values = [aantal_reizen_NL, aantal_reizen_grensoverschrijdend]
labels = ['Binnenland', 'Internationaal']
colors = [ '#FFB347','#87CEEB']

reisnummer.write(f"Van de {aantal_reizen} reizen zijn er {aantal_reizen_NL} reizen volledig binnen Nederland en {aantal_reizen_grensoverschrijdend} internationale reizen.")

fig, ax = plt.subplots()
ax.pie(values, labels=labels, colors=colors, startangle=90, wedgeprops={'width':0.4},autopct='%1.0f')
ax.set(aspect="equal")

plt.title("Verdeling reizen")

reisweergave.pyplot(fig)

# # Toon de lopers
st.subheader("2. Gebruik stations als looproute")
no_journey = journeys_df.query("check_in == check_uit").shape[0]

#Toon het totaal aantal reizen en lopers in een bar chart
display, text = st.columns(2)
text.write(f"Van de {aantal_reizen} reizen zijn die er worden gemaakt zijn er {no_journey} reizen waarbij de check-in en check-out hetzelfde station is. Dit zijn passanten, die gebruiken het station als looproute.")
text.write("De overige reizen zijn reizen waarbij de check-in en check-out op verschillende stations zijn.")

reizigers, passanten = display.columns(2)
reizigers.metric(label="reizigers", value=aantal_reizen-no_journey, delta=None, delta_color="normal")
passanten.metric(label="passanten", value=no_journey, delta=None, delta_color="normal")
reizigers.metric(label="van alle poortscans zijn", value=f"{round((aantal_reizen-no_journey)/aantal_reizen * 100,3)}%", delta=None, delta_color="normal")
passanten.metric(label="en zijn", value=f"{round(no_journey/aantal_reizen*100,3)}%", delta=None, delta_color="normal")
reizigers.write("van reizigers")
passanten.write("van passanten")

# # Toon top 10 drukste stations in Nederland
st.subheader("3. De drukste stations in Nederland")
topx = st.slider("Aantal stations", 1, 100, 10, on_change=None)
st.write(f"De {topx} drukste stations in Nederland gebaseerd op het aantal reizigers op het aantal check-ins en check-outs.")
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

st.subheader("4. Verdeling type tickets")
# splits de ticket types uit.
transactions_b = transactions_df.query("`TICKET TYPE` == 'B'").shape[0]
transactions_e = transactions_df.query("`TICKET TYPE` == 'E' or `TICKET TYPE` == 'Enkel'").shape[0]
transactions_r = transactions_df.query("`TICKET TYPE` == 'R' or `TICKET TYPE` == 'Retour'").shape[0]

e, r, b, = st.columns(3)
e.metric(label="Enkele reis", value=transactions_e, delta=None, delta_color="normal")
r.metric(label="Retour", value=transactions_r, delta=None, delta_color="normal")
b.metric(label="Generiek", value=transactions_b, delta=None, delta_color="normal")

ep, rp, bp, = st.columns(3)
totaal_tickets = transactions_e + transactions_r + transactions_b
ep.metric(label="Enkele reis %", value=f"{round(transactions_e / totaal_tickets * 100,2)}%", delta=None, delta_color="normal")
rp.metric(label="Retour %", value=f"{round(transactions_r / totaal_tickets * 100, 2)}%", delta=None, delta_color="normal")
bp.metric(label="Generiek %", value=f"{round(transactions_b / totaal_tickets * 100, 2)}%", delta=None, delta_color="normal")


values = [transactions_e, transactions_r, transactions_b]
labels = ['Enkel', 'Retour', 'Generiek']
colors = [ '#7ef291','#7ec8f2','#f27e99']

fig, ax = plt.subplots()
ax.pie(values, labels=labels, colors=colors, startangle=90, wedgeprops={'width':0.4})
ax.set(aspect="equal")

plt.title("Verdeling ticket types")

st.pyplot(fig)


