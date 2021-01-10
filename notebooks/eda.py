#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

demo_data = pd.read_csv('../auxiliary_data/regioni_istat_2020_01.csv').drop(
    ['Tipo di indicatore demografico', 'Sesso', 'Età', 'Flags', 'Seleziona periodo'], axis=1)
demo_data = demo_data[demo_data['Stato civile']=='totale']


demo_data.at[24,'Territorio'] = 'P.A. Bolzano'
demo_data.at[29,'Territorio'] = 'P.A. Trento'

regional_data = pd.read_csv('../dati-regioni/dpc-covid19-ita-regioni.csv')
regional_data['data'] = pd.to_datetime(regional_data['data'])


mapping_regioni = dict(zip(sorted(demo_data.Territorio.unique()),sorted(regional_data.denominazione_regione.unique())))


demo_data['denominazione_regione']=demo_data['Territorio'].map(mapping_regioni)

demo_data.rename(columns={'Value':'population'},inplace=True)


regional_data = regional_data.merge(demo_data,on='denominazione_regione')

metrics = ('terapia_intensiva','totale_ospedalizzati', 'totale_positivi','nuovi_positivi', 
                'deceduti', 'tamponi','ingressi_terapia_intensiva')
metrics_to_plot = []
for metric in metrics:
    label = metric + '_su_popolazione'
    metrics_to_plot.append(metric)
    metrics_to_plot.append(label)
    regional_data[label] = regional_data[metric]/regional_data['population']


st.title('COVID-19: Italian regional data')

# Only a subset of options make sense
y_options = sorted(metrics_to_plot)
# Allow use to choose
y_axis = st.sidebar.selectbox('Which metric do you want to explore?', y_options)
fig = px.line(regional_data,
                x= 'data',
                y= y_axis ,
                color = 'denominazione_regione',
                title=f'y_axis')

st.plotly_chart(fig)