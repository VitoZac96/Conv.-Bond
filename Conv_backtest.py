import streamlit as st

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import plotly.express as px

import pandas as pd
import numpy as np

import datetime
import time

from dateutil.relativedelta import relativedelta

#st.pyplot(fig)
st.title("Confronto Storico tra Portafogli")

st.subheader('Portafoglio 1')

st.markdown("20% Bloomberg Euro Aggregate 1-3 anni")
st.markdown("30% Bloomberg Euro")
st.markdown("50% MSCI Daily Net Total Return Word Euro")

st.subheader('Portafoglio 2')

st.markdown("20% Bloomberg Euro Aggregate 1-3 anni")
st.markdown("20% Bloomberg Euro")
st.markdown("40% MSCI Daily Net Total Return Word Euro")
st.markdown("10% Refinitiv Glob Hedged CB (EUR)")

st.subheader('Rebalancing Semestrale')

st.divider()


st.subheader('Seleziona le date per il confronto')


dati = pd.read_excel("dati_convert.xlsx", index_col = 0, engine="openpyxl")
percentage_pf = dati.pct_change()[1:]
percentage_pf_no_conv = percentage_pf.iloc[:,:-1]

inizio = st.date_input(
        "Data Inizio",
        datetime.date(2003, 1, 31),
        min_value = datetime.date(2003, 1, 31),
        max_value = datetime.date(2021, 12, 31))
    #st.write('Hai selezionato:', inizio)

fine = st.date_input(
    "Data Fine",
    datetime.date(2023, 4, 10),
    min_value = datetime.date(2003, 1, 1),
    max_value = datetime.date(2023, 6, 30)
    )
    #st.write('Hai selezionato:', fine)
st.divider()


percentage_pf_selezionato = percentage_pf["{}".format(inizio):  "{}".format(fine) ]
percentage_pf_no_conv_selezionato = percentage_pf_no_conv["{}".format(inizio):  "{}".format(fine) ]



rebalancing_date = np.arange(6,len(percentage_pf),6)

lista_ritorni_drift_weights = []
pesi = np.array([0.2,0.2,0.4,0.2])

for i in range(len(percentage_pf_selezionato)):

    if i == 0:
        lista_ritorni_drift_weights.append((percentage_pf_selezionato.iloc[i,:]*pesi).sum())

    else:

        if i in rebalancing_date:

            pesi = np.array([0.2,0.2,0.4,0.2])

        
            moltiplic = (1+percentage_pf_selezionato.iloc[i,:])#*0.02#/(drit.iloc[1,:]*0.02).sum()
            pesi_moltiplic = moltiplic * pesi

            nuovi_pesi = (pesi_moltiplic/ pesi_moltiplic.sum())
        
            lista_ritorni_drift_weights.append((percentage_pf_selezionato.iloc[i,:]*nuovi_pesi).sum())

        else:
            moltiplic = (1+percentage_pf_selezionato.iloc[i,:])#*0.02#/(drit.iloc[1,:]*0.02).sum()
            pesi_moltiplic = moltiplic * pesi

            nuovi_pesi = (pesi_moltiplic/ pesi_moltiplic.sum())
        
            lista_ritorni_drift_weights.append((percentage_pf_selezionato.iloc[i,:]*nuovi_pesi).sum())


pesi_no_conv  = np.array([0.2,0.3,0.5])
lista_ritorni_drift_weights_no_conv = []

for i in range(len(percentage_pf_no_conv_selezionato)):

    if i == 0:
        lista_ritorni_drift_weights_no_conv.append((percentage_pf_no_conv_selezionato.iloc[i,:]*pesi_no_conv).sum())

    else:

        if i in rebalancing_date:

            pesi_no_conv = np.array([0.2,0.3,0.5])

        
            moltiplic = (1+percentage_pf_no_conv_selezionato.iloc[i,:])#*0.02#/(drit.iloc[1,:]*0.02).sum()
            pesi_moltiplic = moltiplic * pesi_no_conv

            nuovi_pesi = (pesi_moltiplic/ pesi_moltiplic.sum())
        
            lista_ritorni_drift_weights_no_conv.append((percentage_pf_no_conv_selezionato.iloc[i,:]*nuovi_pesi).sum())

        else:
            moltiplic = (1+percentage_pf_no_conv_selezionato.iloc[i,:])#*0.02#/(drit.iloc[1,:]*0.02).sum()
            pesi_moltiplic = moltiplic * pesi_no_conv

            nuovi_pesi = (pesi_moltiplic/ pesi_moltiplic.sum())
        
            lista_ritorni_drift_weights_no_conv.append((percentage_pf_no_conv_selezionato.iloc[i,:]*nuovi_pesi).sum())


cum_ret = np.array([1])
cum_ret = np.append(cum_ret,np.array(np.cumprod(1+np.array(lista_ritorni_drift_weights))))

cum_ret_no_conv = np.array([1])
cum_ret_no_conv = np.append(cum_ret_no_conv,np.array(np.cumprod(1+np.array(lista_ritorni_drift_weights_no_conv))))


indice_date = [inizio]

start_date = inizio 
end_date = fine

while start_date <= end_date:

    start_date = start_date + relativedelta(months=1)

    indice_date.append(start_date)



df = pd.DataFrame(cum_ret)
df["Portafoglio Senza Conv. Bond"] = cum_ret_no_conv
df.index = indice_date

df.columns = ["Portafoglio Con Conv. Bond", "Portafoglio Senza Conv. Bond"]

fig = px.line(df,title="Confronto tra Portafogli", 
              labels={
                  "value": "Valore di 1€ investito",
                  "index": "Data",
                  "variable": "Tipo di Pf."}, height = 800)

fig.update_layout({
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'paper_bgcolor': 'rgba(0,0,0,0)'}, title_x=0.5, legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))
#fig.show()

st.plotly_chart(fig, use_container_width=True)



previous_peak_no_conv = df["Portafoglio Senza Conv. Bond"].cummax()
drawdown_no_conv = (df["Portafoglio Senza Conv. Bond"] - previous_peak_no_conv) / previous_peak_no_conv

previous_peak_conv = df["Portafoglio Con Conv. Bond"].cummax()
drawdown_conv = (df["Portafoglio Con Conv. Bond"] - previous_peak_conv) / previous_peak_conv


dd_df = pd.DataFrame(drawdown_conv)
dd_df["a"] = drawdown_no_conv

dd_df.columns = ["DD Portafoglio Con Conv. Bond", "DD Portafoglio Senza Conv. Bond"]

fig1 = px.line(dd_df,title="Confronto tra i Draw Down cumulati dei Portafogli", 
              labels={
                  "value": "Valore di 1€ investito",
                  "index": "Data",
                  "variable": "Tipo di Pf."}, height = 800)

fig1.update_layout({
    
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'paper_bgcolor': 'rgba(0,0,0,0)'}, title_x=0.5, 
    legend=dict(yanchor="bottom",y=0.99,xanchor="left",x=0.01))
#fig.show()
fig1.layout.yaxis.tickformat = ',.0%'

st.plotly_chart(fig1, use_container_width=True)

st.divider()

st.subheader('Statistiche Annuali')

stat = pd.read_excel("statistiche.xlsx", index_col = 0, engine="openpyxl")

#anni = np.arange(2003,2024)
#statistiche = ["Ritorno Conv", "Ritorno no Conv", "Volatilità Conv","Volatilità no Conv" , "Max DD Conv","Max DD No Conv" ,"Sharpe Ratio Conv", "Sharpe Ratio no Conv"]
#to_display = pd.DataFrame(index = statistiche, columns = anni)

st.dataframe(stat)

st.subheader('Statistiche Aggregate per il Pf. con Conv. Bond rispetto a Pf. senza Conv. Bond')

col1, col2, col3,col4 = st.columns(4)
col1.metric("Ritorno Annuale Maggiore", "7 Anni", "su 21 (33%)")
col2.metric("Volatilità Annuale Minore", "12 Anni", "Su 21 (57%)")
col3.metric("Draw Down Minore", "15 Anni", "Su 21 (71%)")
col4.metric("Sharpe Ratio Maggiore", "11 Anni", "su 21 (52%)")


#diff = dd_df.iloc[:,1]-dd_df.iloc[:,0]

st.divider()

st.subheader('Conclusioni')

st.markdown("Includendo i Convertible Bond nell'asset allocation, nel lungo periodo, si beneficia degli effetti positivi della diversificazione.")

st.markdown("In particolare, come mostrano i dati, l'asset class aiuta a ridurre i draw down. Infatti, in 15 anni su 20 si sono registrati massimi Draw Down meno pesanti, con particolari benefici (fino al 3%) nei momenti più difficili come il 2008, il covid e il 2022 (vedi grafico sotto).")           

st.markdown("Questo però, avviene a discapito dei ritorni assoluti. Infatti, un portafoglio che include i Conv. Bond, avrebbe battuto (in termini di ritorno annuale) solo 7 anni su 21 un portafoglio senza Conv. Bond.")

st.markdown("Tuttavia, la minor volatilità realizzata e i minori Draw Down, fanno registrare uno Sharpe Ratio maggiore al portavoglio con Conv. Bond il 52% delle volte (11 anni su 21).")

st.markdown("In definitiva, nel lungo periodo, gli effetti positivi di includere i Conv. Bond superano quelli negativi. L'inclusione dell'asset class aiuta a creare portafogli con un rapporto rischio-rendimento migliore.")


diff_dd_df = pd.read_excel("statistiche.xlsx", sheet_name = "Sheet2", index_col = 0, engine="openpyxl")


fig2 = px.line(diff_dd_df,title="Di quanto il Max DD del Portafoglio senza Conv. Bond è stato maggiore rispetto al Pf. con Conv. Bond?", 
              labels={
                  "value": "Differenza Tra Massimi Draw Down Annuali",
                  "index": "Data",
                  "variable": ""}, height = 800)

fig2.update_layout({
    
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'paper_bgcolor': 'rgba(0,0,0,0)'}, title_x=0.5, 
    legend=dict(yanchor="bottom",y=0.99,xanchor="left",x=0.01))
#fig.show()
fig2.layout.yaxis.tickformat = ',.2%'

st.plotly_chart(fig2, use_container_width=True)