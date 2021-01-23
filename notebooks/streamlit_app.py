#!/usr/bin/env python
# coding: utf-8

# # Exploratory data analysis - Italy

# In[40]:


import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from datetime import datetime

st.set_page_config(layout="wide")


# ## Data Extraction and Loading

# In[41]:


demo_data = pd.read_csv('https://raw.githubusercontent.com/ChiaraMasiero/COVID-19/master/auxiliary_data/regioni_istat_2020_01.csv').drop(
    ['Tipo di indicatore demografico', 'Sesso', 'Età', 'Flags', 'Seleziona periodo'], axis=1)
demo_data = demo_data[demo_data['Stato civile']=='totale']


# In[42]:


demo_data.at[24,'Territorio'] = 'P.A. Bolzano'
demo_data.at[29,'Territorio'] = 'P.A. Trento'


# In[4]:


#regional_data = pd.read_csv('../dati-regioni/dpc-covid19-ita-regioni.csv')
regional_data = pd.read_csv('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv')
regional_data['data'] = pd.to_datetime(regional_data['data'])


# In[5]:


mapping_regioni = dict(zip(sorted(demo_data.Territorio.unique()),sorted(regional_data.denominazione_regione.unique())))


# In[6]:


demo_data['denominazione_regione']=demo_data['Territorio'].map(mapping_regioni)


# In[7]:


demo_data.rename(columns={'Value':'population'},inplace=True)


# In[8]:


macro_regions = pd.read_csv('https://raw.githubusercontent.com/ChiaraMasiero/COVID-19/master/auxiliary_data/macro_regioni.csv', sep=';')


# In[9]:


regional_data = regional_data.merge(demo_data,on='denominazione_regione').merge(macro_regions, on='denominazione_regione')


# In[10]:


#vaccine_data = pd.read_csv('https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-latest.csv')


# In[11]:


#world_data = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')


# ## Data analysis
# 
# ### List of vizualizations
# - Scorecards (current positive) 
# - Top 5 regions by (most) new cases last seven days
# - Top 5 regions by current positive on population
# - New positive weekly sum by macro region (stacked column chart) trend
# - Rolling avg (7 days) new positive and new case by population by region (with selector)
# - Intensive cares/Deaths and IC/deaths by population by region (with selector)
# 
# The same can be repeated at World and Europe level

# In[12]:


regional_level_values = regional_data.set_index(['denominazione_regione','data']).index.get_level_values


# In[13]:


regional_data = regional_data.sort_values(by=['denominazione_regione','data'], ascending=True)


# In[14]:


metrics = ('terapia_intensiva','totale_ospedalizzati', 'totale_positivi','nuovi_positivi','totale_casi', 
                'deceduti', 'tamponi','ingressi_terapia_intensiva')


# In[15]:


metrics_to_plot = []
for metric in metrics:
    metrics_to_plot.append(metric)
    #over population
    label = metric + '_su_100000'
    metrics_to_plot.append(label)
    regional_data[label] = regional_data[metric]*100000/regional_data['population']


# In[16]:


#result = regional_data.set_index(['denominazione_regione','data']).groupby([regional_level_values(0)]
#                      +[pd.Grouper(freq='7d', level=-1)]).agg({'nuovi_positivi':np.sum})


# In[18]:


regional_data['nuovi_positivi_rolling_avg_7_days'] = regional_data.set_index(['denominazione_regione','data']).groupby(level=0).rolling(7).mean()['nuovi_positivi'].values
regional_data['nuovi_positivi_su_100000_rolling_avg_7_days'] = regional_data.set_index(['denominazione_regione','data']).groupby(level=0).rolling(7).mean()['nuovi_positivi_su_100000'].values
regional_data['nuovi_positivi_rolling_sum_7_days'] = regional_data.set_index(['denominazione_regione','data']).groupby(level=0).rolling(7).sum()['nuovi_positivi'].values
regional_data['nuovi_positivi_su_100000_rolling_sum_7_days'] = regional_data.set_index(['denominazione_regione','data']).groupby(level=0).rolling(7).sum()['nuovi_positivi_su_100000'].values


# In[19]:


#regional_data.query('denominazione_regione=="Veneto"').tail(10)[['nuovi_positivi','nuovi_positivi_rolling_avg_7_days','nuovi_positivi_rolling_sum_7_days']]


# In[20]:


#px.bar(data_frame=regional_data,y='terapia_intensiva',x='data',color='macro_regione', hover_name='denominazione_regione')


# In[21]:


st.title('COVID-19 monitoring dashboard')


# In[22]:


st.write('## Italian data')


# In[23]:


most_recent_day = regional_data.data.max()


# In[39]:


col1, col2 = st.beta_columns(2)


# In[35]:


fig = px.bar(data_frame = regional_data[regional_data['data']==most_recent_day].sort_values(by='nuovi_positivi_rolling_sum_7_days',ascending=False).head(10), 
       x='denominazione_regione', 
       y ='nuovi_positivi_rolling_sum_7_days', 
       labels={'nuovi_positivi_rolling_sum_7_days':'Sum of positive tests, last 7 days','data':'Date', 'denominazione_regione':'region'},
       title='Top 10 regions by sum of positive tests - last 7 days')

col1.plotly_chart(fig)


# In[36]:


fig = px.bar(data_frame = regional_data[regional_data['data']==most_recent_day].sort_values(by='totale_positivi_su_100000',ascending=False).head(10), 
       x='denominazione_regione', 
       y ='totale_positivi_su_100000', 
       labels={'totale_positivi_su_100000':'Currently infected people over 100,000','data':'Date', 'denominazione_regione':'region'},
       title='Top 10 regions by number of infected people over 100000 inhabitants')

col2.plotly_chart(fig)


# In[26]:


metrics_to_plot = ['terapia_intensiva','deceduti','totale_positivi','totale_casi','nuovi_positivi_rolling_avg_7_days','terapia_intensiva_su_100000','deceduti_su_100000','totale_positivi_su_100000','totale_casi_su_100000','nuovi_positivi_rolling_avg_7_days_su_100000']


# In[31]:


# Only a subset of options make sense
y_options = sorted(metrics_to_plot)
# Allow user to choose metric
y_axis = st.sidebar.selectbox(label='Which metric do you want to explore?', options=y_options,key=0)


# In[32]:


# By MacroRegion
fig = px.bar(data_frame=regional_data,
        x='data',
        y = y_axis,
        color='macro_regione',
        hover_name='denominazione_regione', 
        title=f'Daily trend by macro-region: {y_axis}')
col1.plotly_chart(fig)


# In[33]:


# Single Region 
# Allow user to choose regions
regions = st.sidebar.multiselect(label='Which regions do you want to consider?', 
                                      options=sorted(regional_data['denominazione_regione'].unique()), 
                                      default=sorted(regional_data['denominazione_regione'].unique()),
                                key=1)

# plot the value
fig = px.line(regional_data[regional_data['denominazione_regione'].isin(regions)],
                x= 'data',
                y= y_axis ,
                color = 'denominazione_regione',
                title=f'Daily trend by region: {y_axis}')

col2.plotly_chart(fig)


# In[ ]:





# In[ ]:




