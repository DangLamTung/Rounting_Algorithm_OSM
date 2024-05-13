import streamlit as st
import folium
import osmnx
import networkx as nx
import numpy as np
import pandas as pd
import leafmap.foliumap as leafmap
from streamlit_folium import st_folium
from folium.plugins import Draw

from apps.navigator_offline import (get_location_from_address,
                            get_graph,
                            compare_find_shortest_path,
                            find_shortest_path) 

BASEMAPS = ['Satellite', 'Roadmap', 'Terrain', 'Hybrid', 'OpenStreetMap']
TRAVEL_MODE = ['Drive', 'Walk', 'Bike']
TRAVEL_OPTIMIZER = ['Dijkstra', 'Bellman-Ford', 'Floyd Warshall' ]
ADDRESS_DEFAULT = "[10.7724,106.65922]"



# Create a session variable
if 'comparing' not in st.session_state:
    st.session_state['comparing'] = False

if '3short' not in st.session_state:
    st.session_state['3short'] = False
 #path folder of the data file


def clear_text():
    st.session_state["go_from"] = ""
    st.session_state["go_to"] = ""
@st.cache_data
def compare_algo():
    st.session_state['comparing'] = True
    graph, location_orig, location_dest = get_graph(address_from, address_to)
    time_cal,routes = compare_find_shortest_path(graph, location_orig, location_dest, optimizer)


    time_details = {
    'Algo' : ['Dijkstra', 'Bellman-Ford', 'Floyd Warshall'],
    'Time' : [time_cal[0],time_cal[1],0],
    }
  
    df = pd.DataFrame.from_dict(time_details, orient="index")
    df.to_csv("data.csv")
    # return time_cal
    return routes

@st.cache_data
def short_algo():
    st.session_state['3short'] = True
    graph, location_orig, location_dest = get_graph(address_from, address_to)
    time_cal,routes = compare_find_shortest_path(graph, location_orig, location_dest, optimizer)


    time_details = {
    'Algo' : ['Dijkstra', 'Bellman-Ford', 'Floyd Warshall'],
    'Time' : [time_cal[0],time_cal[1],0.0],
    }
  
    df = pd.DataFrame.from_dict(time_details, orient="index")
    df.to_csv("data.csv")
    # return time_cal
    return routes


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


    # st.table(df)

    st.button("Clear all address boxes", on_click=clear_text)
    

    btn = st.button('Compare 3 algos')


    if(btn):
        compare_algo()
    btn1 = st.button('Draw 3 shortest path')


    if(btn1):
        compare_algo()
    data = pd.read_csv("data.csv")
    st.write(data) #displays the table of data     
    
 
    st.write(address_to)



    # st.info(
    #     "This is an open source project and you are very welcome to contribute your "
    #     "comments, questions, resources and apps as "
    #     "[issues](https://github.com/maxmarkov/streamlit-navigator/issues) or "
    #     "[pull requests](https://github.com/maxmarkov/streamlit-navigator/pulls) "
    #     "to the [source code](https://github.com/maxmarkov/streamlit-navigator). "
    # )




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
route =  []
if address_from and address_to:

    # === FIND THE PATH ===
    
    # = Alternative options (mode='place' seems to be the fastest) =
    #graph, location_orig, location_dest = get_graph_from_mode(address_from, address_to, mode="place", city="Manhattan")
    #graph, location_orig, location_dest = get_graph_from_mode(address_from, address_to, mode="address", dist=3000)

    # Search information 
    st.markdown(f'**From**: {address_from}')
    st.markdown(f'**To**: {address_to}')
    

    # re-center
    # leafmap.Map(center=location_orig, zoom=16)



    # find the nearest node to the start location
    # folium.Marker( list(location_orig), popup="Liberty Bell", tooltip="Liberty Bell").add_to(m)
    # folium.Marker( list(location_dest), popup="Liberty Bell", tooltip="Liberty Bell").add_to(m)

    # output = st_folium(m, width=700, height=500)
    # print(output)
    # find the shortest path
    # if not st.session_state['comparing']:
    #     graph, location_orig, location_dest = get_graph(address_from, address_to)
    #     st.write(graph)


        
    #     route = find_shortest_path(graph, location_orig, location_dest, optimizer)

    #     osmnx.plot_route_folium(graph, route, m)
    #     # map = st_folium(m, height=800, width=1400)
    #     print(route)
    # else:

        
    graph, location_orig, location_dest = get_graph(address_from, address_to)

    st.write(graph)
    #Draw 3 shortest path using the Yen Algorithm as default
    time_cal,routes = compare_find_shortest_path(graph, location_orig, location_dest, optimizer)
    

    rc = ['r', 'b', 'g']

    node_orig = osmnx.nearest_nodes(graph, location_orig[1],location_orig[0])
    node_dest = osmnx.nearest_nodes(graph, location_dest[1],location_dest[0])

    m.add_marker(location=list(location_orig), icon=folium.Icon(color='red', icon='suitcase', prefix='fa'))
    m.add_marker(location=list(location_dest), icon=folium.Icon(color='green', icon='street-view', prefix='fa'))

    routes = osmnx.k_shortest_paths(graph, node_orig, node_dest, k=3, weight="length")


    
    k = 3
    short_routes = []
    for counter, path in enumerate(routes):
        short_routes.append(path)
        if counter == k-1:
            break
    print(short_routes)
    fig, ax = osmnx.plot_graph_routes(
        graph, short_routes, route_colors=rc,
        route_linewidth=4, node_size=0)
    
        # for i in range(2):
    osmnx.plot_route_folium(graph, short_routes[0],m,  color= '#ff0000', opacity=1)
    osmnx.plot_route_folium(graph, short_routes[1],m,  color= '#00ffff', opacity=1)
    osmnx.plot_route_folium(graph, short_routes[2],m,  color= '#0000ff', opacity=1)
        # map = st_folium(m, height=800, width=1400)

    # rc = ['r', 'b']
    # fig, ax = osmnx.plot_graph_routes(graph, routes, route_colors=rc, route_linewidth=6, node_size=0)
    st.session_state['comparing'] = False
    st.pyplot(fig)

else:

    # m.add_marker(location=(lat, lon), popup=f"lat, lon: {lat}, {lon}", icon=folium.Icon(color='green', icon='eye', prefix='fa'))
    st.write(f"Lat, Lon: {lat}, {lon}")

map = st_folium(m, height=800, width=1400)
# m.to_streamlit()
