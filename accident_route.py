import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
import pydeck as pdk
from geopy.geocoders import Nominatim

current_year = datetime.now().year

departement_correspondances = {
    "01": "Ain",
    "02": "Aisne",
    "03": "Allier",
    "04": "Alpes-de-Haute-Provence",
    "05": "Hautes-Alpes",
    "06": "Alpes-Maritimes",
    "07": "Ardèche",
    "08": "Ardennes",
    "09": "Ariège",
    "10": "Aube",
    "11": "Aude",
    "12": "Aveyron",
    "13": "Bouches-du-Rhône",
    "14": "Calvados",
    "15": "Cantal",
    "16": "Charente",
    "17": "Charente-Maritime",
    "18": "Cher",
    "19": "Corrèze",
    "21": "Côte-d'Or",
    "22": "Côtes-d'Armor",
    "23": "Creuse",
    "24": "Dordogne",
    "25": "Doubs",
    "26": "Drôme",
    "27": "Eure",
    "28": "Eure-et-Loir",
    "29": "Finistère",
    "2A": "Corse-du-Sud",
    "2B": "Haute-Corse",
    "30": "Gard",
    "31": "Haute-Garonne",
    "32": "Gers",
    "33": "Gironde",
    "34": "Hérault",
    "35": "Ille-et-Vilaine",
    "36": "Indre",
    "37": "Indre-et-Loire",
    "38": "Isère",
    "39": "Jura",
    "40": "Landes",
    "41": "Loir-et-Cher",
    "42": "Loire",
    "43": "Haute-Loire",
    "44": "Loire-Atlantique",
    "45": "Loiret",
    "46": "Lot",
    "47": "Lot-et-Garonne",
    "48": "Lozère",
    "49": "Maine-et-Loire",
    "50": "Manche",
    "51": "Marne",
    "52": "Haute-Marne",
    "53": "Mayenne",
    "54": "Meurthe-et-Moselle",
    "55": "Meuse",
    "56": "Morbihan",
    "57": "Moselle",
    "58": "Nièvre",
    "59": "Nord",
    "60": "Oise",
    "61": "Orne",
    "62": "Pas-de-Calais",
    "63": "Puy-de-Dôme",
    "64": "Pyrénées-Atlantiques",
    "65": "Hautes-Pyrénées",
    "66": "Pyrénées-Orientales",
    "67": "Bas-Rhin",
    "68": "Haut-Rhin",
    "69": "Rhône",
    "70": "Haute-Saône",
    "71": "Saône-et-Loire",
    "72": "Sarthe",
    "73": "Savoie",
    "74": "Haute-Savoie",
    "75": "Paris",
    "76": "Seine-Maritime",
    "77": "Seine-et-Marne",
    "78": "Yvelines",
    "79": "Deux-Sèvres",
    "80": "Somme",
    "81": "Tarn",
    "82": "Tarn-et-Garonne",
    "83": "Var",
    "84": "Vaucluse",
    "85": "Vendée",
    "86": "Vienne",
    "87": "Haute-Vienne",
    "88": "Vosges",
    "89": "Yonne",
    "90": "Territoire de Belfort",
    "91": "Essonne",
    "92": "Hauts-de-Seine",
    "93": "Seine-Saint-Denis",
    "94": "Val-de-Marne",
    "95": "Val-d'Oise",
    "971": "Guadeloupe",
    "972": "Martinique",
    "973": "Guyane",
    "974": "La Réunion",
    "975": "Saint-Pierre-et-Miquelon",
    "976": "Mayotte",
}

base_url1 = "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2021/20231005-094229/usagers-"

base_url2 = "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2021/20231005-093927/carcteristiques-"

found = False
while not found and current_year >= 2005:
    csv_url1 = f"{base_url1}{current_year}.csv"
    csv_url2 = f"{base_url2}{current_year}.csv"
    response1 = requests.head(csv_url1)
    response2 = requests.head(csv_url2)
    if response1.status_code == 200 and response2.status_code == 200:
        found = True
    else:
        current_year -= 1

usager = pd.read_csv(csv_url1, sep=";")
caract = pd.read_csv(csv_url2, sep=";")


caract = caract.rename(columns={'Accident_Id': 'Num_Acc'})
combined_data = pd.merge(caract, usager, on='Num_Acc')
combined_data['lat'] = combined_data['lat'].str.replace(',', '.').astype(float)
combined_data['long'] = combined_data['long'].str.replace(',', '.').astype(float)

# Sidebar
st.sidebar.title('#Datavz2023efrei')
st.sidebar.markdown('Clément Guillaux')
st.sidebar.title("Filtrer par département")
selected_department = st.sidebar.selectbox("Sélectionnez un département", sorted(combined_data['dep'].unique()))

filtered_data = combined_data[combined_data['dep'] == selected_department]

def get_departement_name(numero):
    return departement_correspondances.get(numero, "Nom Inconnu")

selected_department_nom = get_departement_name(selected_department)

# coordonnées du département sélectionné
geolocator = Nominatim(user_agent="geoapiExercises")
location = geolocator.geocode(f"{selected_department_nom}, France")

if location:
    center_lat = location.latitude
    center_lon = location.longitude
else:
    center_lat = 46.603354
    center_lon = 1.888334  

st.title("Les accidents sont-ils fréquents près de chez vous ?")

# 1. Carte 
st.header("Carte de localisation des accidents")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered_data,
    get_position=["long", "lat"],
    get_radius=200,
    get_color=[255, 0, 0],
    pickable=True,
)

view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=8)  
r = pdk.Deck(map_style="mapbox://styles/mapbox/light-v9", layers=[layer], initial_view_state=view_state)

st.pydeck_chart(r)

# Carte avec gravité
def get_color(grav):
    if grav == 2:
        return [255, 0, 0]  
    elif grav == 1:
        return [0, 255, 0]
    elif grav == 3:
        return [0, 0, 255]  
    elif grav == 4:
        return [255, 255, 0]  
    else:
        return [128, 128, 128]  

filtered_data['fill_color'] = filtered_data['grav'].apply(get_color)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered_data,
    get_position=["long", "lat"],
    get_radius=400,
    get_fill_color="fill_color",
    pickable=True,
)

view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=8)
r = pdk.Deck(map_style="mapbox://styles/mapbox/light-v9", layers=[layer], initial_view_state=view_state)

# Légende
st.pydeck_chart(r)
st.markdown("Mortel: Rouge")
st.markdown("Blessé hospitalisé : Jaune")
st.markdown("Blessé léger: Bleu")
st.markdown("Indemne: Vert")

# Age streamlit
filtered_data["age"] = current_year - filtered_data["an_nais"]

st.write("Age des personnes ayant des accidents")
st.bar_chart(filtered_data["age"].value_counts())

# Heure streamlit
filtered_data = filtered_data.sort_values(by="hrmn")

st.write("Horaires les plus dangereux")
hour_counts = filtered_data["hrmn"].value_counts()
st.bar_chart(hour_counts)

# Cammembert
correspondance_trajet = {
    -1: "Non renseigné",
    0: "Non renseigné",
    1: "Domicile – travail",
    2: "Domicile – école",
    3: "Courses – achats",
    4: "Utilisation professionnelle",
    5: "Promenade – loisirs",
    9: "Autre"
}

filtered_data['trajet'] = filtered_data['trajet'].map(correspondance_trajet)

fig = px.pie(filtered_data, names="trajet", title="Répartition des types d'accidents", hole=0.3)
st.plotly_chart(fig)

# Sécurité
secur_data = filtered_data[filtered_data['secu1'] != -1]

correspondance_secu = {
    -1: "Non renseigné",
    0: "Aucun équipement",
    1: "Ceinture",
    2: "Casque",
    3: "Dispositif enfants",
    4: "Gilet réfléchissant",
    5: "Airbag (2RM/3RM)",
    6: "Gants (2RM/3RM)",
    7: "Gants + Airbag (2RM/3RM)",
    8: "Non déterminable",
    9: "Autre"
}

secu_labels = [correspondance_secu[secu] for secu in secur_data['secu1']]
secur_data['secu1_label'] = secu_labels

secur_data = secur_data.sort_values(by='grav')

fig = px.bar(
    secur_data, 
    x='secu1_label',
    y='grav',
    color='grav',  
    labels={'grav': 'Gravité'},
    title='Gravité des accidents en fonction de la sécurité'
)

st.plotly_chart(fig)

