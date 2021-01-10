import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import folium
from streamlit_folium import folium_static

## Veriyi Yükleme

df_confirmed = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
df_deaths = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
df_covid19 = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv")

turkiye = pd.read_csv("https://raw.githubusercontent.com/ozanerturk/covid19-turkey-api/master/dataset/timeline.csv")
## Ön İşleme

df_confirmed = df_confirmed.replace(np.nan, '', regex=True)
df_deaths = df_deaths.replace(np.nan, '', regex=True)

df_country_cases = df_covid19.copy().drop(['Lat', 'Long_', 'Last_Update', 'People_Tested', 'People_Hospitalized'], axis = 1)

turkiye_patients = turkiye.loc[turkiye["patients"] >= 100].copy().drop('date', axis = 1)
turkiye_deaths = turkiye.loc[turkiye["totalDeaths"] >= 10].copy().drop('date', axis = 1)
## Hesaplamalar
df_total_confirmed = pd.to_numeric(df_confirmed.drop(["Province/State", "Country/Region", "Lat", "Long"], axis =1).sum())
df_total_death = pd.to_numeric(df_deaths.drop(["Province/State", "Country/Region", "Lat", "Long"], axis =1).sum())
df_total_confirmed.columns = ['count'] 
df_total_death.columns = ['count']

df_total_confirmed.count = df_total_confirmed.values.tolist()
df_total_death.count = df_total_death.values.tolist()

map_data = df_covid19.copy().drop(['Last_Update', 'People_Tested','People_Hospitalized', 'UID','ISO3'], axis=1)
map_data=map_data.rename({'Long_':'lon', 'Lat':'lat', 'Country_Region':'Country'}, axis=1)
map_data=map_data.dropna(subset=['lat', 'lon'])
map_data.dropna(subset=['lat', 'lon'])

#Logaritma
turkiye["log(totalTests)"] = round(np.log(turkiye.totalTests + 1),3) 
turkiye["log(cases)"] = round(np.log(turkiye.cases + 1),3) 
turkiye["log(totalDeaths)"] = round(np.log(turkiye.totalDeaths + 1),3) 
turkiye["log(totalRecovered)"] = round(np.log(turkiye.totalRecovered + 1),3) 
turkiye["log(critical)"] = round(np.log(turkiye.critical + 1),3) 

turkiye = turkiye.replace(np.nan, '', regex=True)
## Kullanıcı Ara Yüzü
st.title('COVID-19')
radio_opt = ('Dünya', 'Vaka Sayısı', 'Vefat Sayısı', 'İyileşen Sayısı', 'Türkiye')
radio = st.radio('',radio_opt[0:])

if radio=='Dünya':
	st.subheader('Dünya')
	st.dataframe(df_covid19)
	df_world = pd.DataFrame(pd.to_numeric(df_country_cases.drop('Country_Region', axis = 1).sum()),dtype=np.float64).transpose()
	df_world["Mortality Rate (per 100)"] = np.round(100*df_world["Deaths"]/df_world["Confirmed"],2)
	st.dataframe(df_world.style.background_gradient(cmap='Wistia',axis=1).format("{:.0f}",subset=["Confirmed"]))

	st.subheader('Korelasyon Tablosu')
	st.dataframe(df_country_cases.iloc[:,:-1].corr().style.background_gradient(cmap='Reds'))

	## Dünya Haritası
	st.subheader('Dünya Haritası')
	m = folium.Map(location=[0,0], tiles="cartodbpositron", zoom_start=2)
	 
	for i in range(0,len(map_data)):
	   folium.Circle(
	      location=[map_data.iloc[i]['lat'], map_data.iloc[i]['lon']],
	      tooltip = "<h5 style='text-align:center;font-weight: bold'>"+map_data.iloc[i]["Country"]+"</h5>"+
	                    "<div style='text-align:center;'>"+"</div>"+
	                    "<hr style='margin:10px;'>"+
	                    "<ul style='color: #444;list-style-type:circle;align-item:left;padding-left:20px;padding-right:20px'>"+
	        "<li>Confirmed: "+str(int(map_data.iloc[i]["Confirmed"]))+"</li>"+
	        "<li>Deaths:   "+str(int(map_data.iloc[i]["Deaths"]))+"</li>"+
	        "<li>Mortality Rate:   "+str(round(map_data.iloc[i]["Mortality_Rate"],2))+"</li>"+
	        "</ul>"
	        ,
	      radius=int(map_data.iloc[i]["Confirmed"])*0.05,
	      color='crimson',
	      fill=True,
	      fill_color='crimson'
	   ).add_to(m)

	folium_static(m)
elif radio=='Vaka Sayısı':
	st.subheader('Vaka Sayısı')
	st.dataframe(df_confirmed.iloc[:,1:])
	st.subheader('Vaka Sayısına Göre Ülkeler')
	df_country_cases["Mortality Rate (per 100)"] = np.round(100*df_country_cases["Deaths"]/df_country_cases["Confirmed"],2)
	st.dataframe(df_country_cases.sort_values('Confirmed', ascending = False).style.background_gradient(cmap='Wistia',subset=['Confirmed'])\
                                        .background_gradient(cmap='Reds', subset=['Deaths'])\
                                        .background_gradient(cmap='Greens', subset=['Recovered'])\
                                        .background_gradient(cmap='Purples', subset=['Active'])\
                                        .background_gradient(cmap='Blues', subset=["Mortality Rate (per 100)"]))
	# En fazla vakanın olduğu 10 ülke
	countries_confirmed = df_country_cases.sort_values('Confirmed').copy().drop(['Deaths', 'Recovered', 'Active', "Mortality Rate (per 100)"], axis=1)
	top_ten_countries = countries_confirmed[-10:]
	## Grafik
	fig = go.Figure(data=go.Bar(name = 'Confirmed', x=top_ten_countries.Confirmed, y=top_ten_countries.Country_Region, orientation='h'))
	fig.update_layout(title = 'En çok vakanın olduğu 10 ülke',
	                  xaxis_title="Vaka Sayısı",
	                  yaxis_title="Ülke")
	st.plotly_chart(fig)

	## Aktif Vaka Sayısı
	countries_active = df_country_cases.sort_values('Active').copy().drop(['Confirmed', 'Recovered', 'Deaths', "Mortality Rate (per 100)"], axis=1)
	top_ten_countries_active = countries_active[-10:]
	top_ten_countries_active.sort_values('Active', ascending = False)
	## Grafik
	fig = go.Figure(data=go.Bar(name = 'Active', x=top_ten_countries_active.Active, y=top_ten_countries_active.Country_Region, orientation='h'))
	fig.update_layout(title = 'En çok aktif hastanın olduğu 10 ülke',
	                  xaxis_title="Hasta Sayısı",
	                  yaxis_title="Ülke")
	st.plotly_chart(fig)

	## Ülkelerin Vaka Sayısı

	st.subheader('Ülkelerin Vaka Sayısı')

	df_confirmed=df_confirmed.iloc[:,1:].groupby(['Country/Region']).sum()
	counties = st.selectbox('Ülkeyi seçiniz', df_confirmed.index.unique())


	country = df_confirmed.loc[df_confirmed.index==counties].copy()
	country = country.T
	country.columns = ['confirmed']

	fig = go.Figure()
	fig.add_trace(go.Scatter(x = country.index,y=country.confirmed,
		            		 mode='lines+markers',
		                     name=counties))

	fig.update_layout(
		    title = counties,
		    xaxis_title="Tarih",
		    yaxis_title="Vaka Sayısı",
		    yaxis_type="log",
		    yaxis_dtick=1,
		    yaxis_exponentformat="power",
		    hovermode="x unified",
		    template='simple_white'
		)
	fig.update_xaxes(tickangle=-90)
	st.plotly_chart(fig)

elif radio=='Vefat Sayısı':
	st.subheader('Vefat Sayısı')
	st.dataframe(df_deaths.iloc[:,1:])
	# En fazla ölümün olduğu 10 ülke
	countries_death = df_country_cases.sort_values('Deaths').copy().drop(['Confirmed', 'Recovered', 'Active'], axis=1)
	top_ten_countries_death = countries_death[-10:]

	## Grafik
	fig = go.Figure(data=go.Bar(name = 'Death', x=top_ten_countries_death.Deaths, y=top_ten_countries_death.Country_Region, orientation='h', marker_color = 'red'))
	fig.update_layout(title = 'En çok vefatın olduğu 10 ülke',
	                  xaxis_title="Toplam",
	                  yaxis_title="Ülkeler")
	st.plotly_chart(fig)

	## Ülkelerin Vefat Sayısı

	st.subheader('Ülkelerin Vefat Sayısı')

	df_deaths=df_deaths.iloc[:,1:].groupby(['Country/Region']).sum()
	counties = st.selectbox('Ülkeyi seçiniz', df_deaths.index.unique())


	deaths = df_deaths.loc[df_deaths.index==counties].copy()
	deaths = deaths.T
	deaths.columns = ['deaths']

	fig = go.Figure()
	fig.add_trace(go.Scatter(x = deaths.index,y=deaths.deaths,
		            		 mode='lines',
		                     name=counties))

	fig.update_layout(
		    title = counties,
		    xaxis_title="Tarih",
		    yaxis_title="Vefat Sayısı",
		    yaxis_type="log",
		    yaxis_dtick=1,
		    yaxis_exponentformat="power",
		    hovermode="x unified",
		    template='simple_white'
		)
	fig.update_xaxes(tickangle=-90)
	st.plotly_chart(fig)


	## Vaka vs Vefat Grafiği
	fig = go.Figure()
	fig = make_subplots(specs=[[{"secondary_y": True}]])

	fig.add_trace(go.Scatter(x=df_total_confirmed.index, y=df_total_confirmed.count,
	                         mode = "lines",
	                         name = "Vaka Sayısı",
	                         ),
	              secondary_y=False)
	fig.add_trace(go.Scatter(x = df_total_death.index,y=df_total_death.count,
	                         mode='lines',
	                         name='Vefat Sayısı',
	                         ),
	              secondary_y=True)

	fig.update_layout(title = 'Vaka-Vefat',
	                  xaxis_title="Tarih",
	                  yaxis_title="Toplam Sayı",
	                  hovermode="x unified",
	                  template='simple_white')

	fig.update_xaxes(tickangle=-90)
	fig.update_yaxes(title_text="<b>Vaka</b> Sayısı", secondary_y=False)
	fig.update_yaxes(title_text="<b>Vefat</b> Sayısı", secondary_y=True)

	st.plotly_chart(fig)

elif radio=='İyileşen Sayısı':
	## En fazla iyileşenin olduğu 10 ülke
	countries_recovered = df_country_cases.sort_values('Recovered').copy().drop(['Confirmed', 'Deaths', 'Active'], axis=1)
	countries_recovered = countries_recovered.dropna(subset=['Recovered'])
	top_ten_countries_recovered = countries_recovered[-10:]
	## Grafik
	fig = go.Figure(data=go.Bar(name = 'Recovered', x=top_ten_countries_recovered.Recovered, y=top_ten_countries_recovered.Country_Region, orientation='h', marker_color = 'green'))
	fig.update_layout(title = 'En çok iyileşenin olduğu 10 ülke',
	                  xaxis_title="Toplam",
	                  yaxis_title="Ülkeler")
	st.plotly_chart(fig)

else:
	st.dataframe(turkiye)

	fig = go.Figure()
	fig = make_subplots(specs=[[{"secondary_y": True}]])

	fig.add_trace(go.Scatter(x=turkiye.date , y=turkiye.cases ,
	                        mode="lines",
	                        name="Vaka Sayısı"))

	fig.add_trace(go.Scatter(x=turkiye.date , y=turkiye.patients ,
	                        mode="lines",
	                        name="Hasta Sayısı"))

	fig.add_trace(go.Scatter(x=turkiye.date , y=turkiye.deaths ,
	                        mode="lines",
	                        name="Ölüm Sayısı"),
	              secondary_y=True)

	fig.update_layout(
	    title='Günlük Vaka ve Ölüm Sayısı',
	    xaxis_title='Tarih',
	    hovermode='x unified',
	    template='simple_white'
	    )

	fig.update_xaxes(tickangle=-90, dtick = 10)
	fig.update_yaxes(title_text="<b>Vaka</b> Sayısı", secondary_y=False)
	fig.update_yaxes(title_text="<b>Vefat</b> Sayısı", secondary_y=True)
	st.plotly_chart(fig)

	fig = go.Figure()
	fig = make_subplots(specs=[[{"secondary_y": True}]])

	fig.add_trace(go.Scatter(x=turkiye_patients.index, y=turkiye_patients.patients,
	                        mode='lines',
	                        name='Hasta Sayısı',
	                        hovertemplate =
	                         '<br><b>Gün</b>: %{x}<br>' +
	                         '<i>Hasta Sayısı</i>: %{y:}'))
	fig.add_trace(go.Scatter(x=turkiye_deaths.index, y=turkiye_deaths.totalDeaths,
	                        mode='lines',
	                        name='Ölü Sayısı',
	                        hovertemplate =
	                         '<br><b>Gün</b>: %{x}<br>' +
	                         '<i>Ölü Sayısı</i>: %{y:}'),
	             secondary_y=True)

	fig.update_layout(
	    title='100. hastadan sonra logaritmik artış',
	    xaxis_title='Gün',
	    hovermode='x',
	    template='simple_white'
	    )
	fig.update_yaxes(type='log',
	                exponentformat='power',
	                dtick=1)
	fig.update_yaxes(title_text="<b>Hasta</b> Sayısı", secondary_y=False)
	fig.update_yaxes(title_text="<b>Ölü</b> Sayısı", secondary_y=True)
	st.plotly_chart(fig)

	fig = go.Figure()
	fig = make_subplots(specs=[[{"secondary_y": True}]])

	
	fig.add_trace(go.Bar(x=turkiye.date, y=turkiye.deaths,name="Ölü Sayısı"))
	fig.add_trace(go.Bar(x=turkiye.date, y=turkiye.recovered,name="İyileşen Hasta Sayısı"))
	fig.add_trace(go.Bar(x=turkiye.date, y=turkiye.patients,name="Hasta Sayısı"))
	fig.add_trace(go.Scatter(x=turkiye.date , y=turkiye.tests ,name="Test Sayısı",
	                        mode="lines"),
	              secondary_y=True)
	fig.add_trace(go.Scatter(x=turkiye.date, y=turkiye.cases, name="Vaka Sayısı",
						     mode="lines"),
				  secondary_y=True)

	fig.update_layout(
	    title="Vaka, Ölüm, Hasta, İyileşen Hasta Sayısı",
	    xaxis_title="Tarih",
	    barmode = 'stack',
	    hovermode="x unified",
	    template='simple_white'
	)

	fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1,
    xanchor="right",
    x=1.5
))

	