import streamlit as st
import folium
import osmnx
import networkx as nx
import leafmap.foliumap as leafmap
from streamlit_folium import st_folium
from folium.plugins import Draw
from apps.navigator_offline import (get_location_from_address,
                            get_graph,
                            find_shortest_path) 

BASEMAPS = ['Satellite', 'Roadmap', 'Terrain', 'Hybrid', 'OpenStreetMap']
TRAVEL_MODE = ['Drive', 'Walk', 'Bike']
TRAVEL_OPTIMIZER = ['Dijistra', 'Bellman-Ford', 'Floyd Warshall' ]

ADDRESS_DEFAULT = "Đại Học Bách Khoa HCM"


def clear_text():
    st.session_state["go_from"] = ""
    st.session_state["go_to"] = ""


st.set_page_config(page_title="🚋 Route finder", layout="wide")

# ====== SIDEBAR ======
with st.sidebar:

    st.title("Choose you travel settings")

    st.markdown("A simple app that finds and displays the shortest path between two points on a map.")

    basemap = st.selectbox("Choose basemap", BASEMAPS)
    if basemap in BASEMAPS[:-1]:
        basemap=basemap.upper()

    transport = st.selectbox("Choose transport", TRAVEL_MODE)
    optimizer = st.selectbox("Choose algorithm", TRAVEL_OPTIMIZER)

    address_from = st.text_input("Go from", key="go_from")
    address_to = st.text_input("Go to", key="go_to")
    
    st.button("Clear all address boxes", on_click=clear_text)
    st.write(address_to)

    st.info(
        "This is an open source project and you are very welcome to contribute your "
        "comments, questions, resources and apps as "
        "[issues](https://github.com/maxmarkov/streamlit-navigator/issues) or "
        "[pull requests](https://github.com/maxmarkov/streamlit-navigator/pulls) "
        "to the [source code](https://github.com/maxmarkov/streamlit-navigator). "
    )




# ====== MAIN PAGE ======
lat, lon = get_location_from_address(address=ADDRESS_DEFAULT)

m = leafmap.Map(center=(lat, lon), zoom=16)

m.add_basemap(basemap)

def get_pos(lat, lng):
    return lat, lng

# m.add_child(folium.LatLngPopup())
Draw(export=True).add_to(m)
m.add_child(
    folium.ClickForLatLng(format_str='"[" + lat + "," + lng + "]"', alert=True)
)
data = None

if address_from and address_to:

    # === FIND THE PATH ===
    graph, location_orig, location_dest = get_graph(address_from, address_to)
    # = Alternative options (mode='place' seems to be the fastest) =
    #graph, location_orig, location_dest = get_graph_from_mode(address_from, address_to, mode="place", city="Manhattan")
    #graph, location_orig, location_dest = get_graph_from_mode(address_from, address_to, mode="address", dist=3000)

    # Search information 
    st.markdown(f'**From**: {address_from}')
    st.markdown(f'**To**: {address_to}')
    st.write(graph)

    # re-center
    # leafmap.Map(center=location_orig, zoom=16)



    # find the nearest node to the start location
    # folium.Marker( list(location_orig), popup="Liberty Bell", tooltip="Liberty Bell").add_to(m)
    # folium.Marker( list(location_dest), popup="Liberty Bell", tooltip="Liberty Bell").add_to(m)
    m.add_marker(location=list(location_orig), icon=folium.Icon(color='red', icon='suitcase', prefix='fa'))
    m.add_marker(location=list(location_dest), icon=folium.Icon(color='green', icon='street-view', prefix='fa'))
    # output = st_folium(m, width=700, height=500)
    # print(output)
    # find the shortest path
    route = find_shortest_path(graph, location_orig, location_dest, optimizer)

    osmnx.plot_route_folium(graph, route, m)
    # map = st_folium(m, height=800, width=1400)
    print(route)
else:

    # m.add_marker(location=(lat, lon), popup=f"lat, lon: {lat}, {lon}", icon=folium.Icon(color='green', icon='eye', prefix='fa'))
    st.write(f"Lat, Lon: {lat}, {lon}")

map = st_folium(m, height=800, width=1400)
# m.to_streamlit()
