from flask import Flask, render_template, url_for, request
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer
import joblib
import networkx as nx
import osmnx as ox
from shapely.geometry import LineString, mapping
import geopandas as gpd
import json
from ipyleaflet import *

app = Flask(__name__)
# Prediction


# def predict_gender(x):
#     vect = gender_cv.transform(data).toarray()
#     result = gender_clf.predict(vect)
#     return result

# # Prediction


# def predict_nationality(x):
#     vect = nationality_cv.transform(data).toarray()
#     result = nationality_clf.predict(vect)
#     return result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/closest')
def gender():
    return render_template('closest.html')



def get_node(center,destin):
    place_name = 'Samosir, North Sumatra'

    graph = ox.graph_from_place(place_name)
    fig, ax = ox.plot_graph(graph)
    nodes, edges = ox.graph_to_gdfs(graph)
    center = (nodes.iloc[center].y,nodes.iloc[center].x)
    dest = (nodes.iloc[destin].y, nodes.iloc[destin].x)
    dest2 = (nodes.iloc[destin+1].y,nodes.iloc[destin+1].x)
    return center,dest,dest2

@app.route('/predict', methods=['POST'])
def predict():
    input_datang = int(request.form['datang'])
    input_tujuan = int(request.form['tujuan'])
    m = Map(center=get_node(input_datang,input_tujuan)[2], basemap=basemaps.OpenStreetMap.Mapnik, zoom=12)


    to_marker_style = AwesomeIcon(
        name='map-marker',
        icon_color='red',
        spin=False
    )

    alamat = get_node(input_datang,input_tujuan)
    center = alamat[0]
    dest = alamat[1]
    dest2 = alamat[2]

    from_marker = Marker(location=center)
    to_marker = Marker(location=dest, icon=to_marker_style)
    marker_2 = Marker(location=dest2, icon=to_marker_style)
    marker.nearest_node = ox.get_nearest_node(graph, marker.location)
    return render_template('index.html', prediction_text='{}'.format(m))

@app.route('/result', methods=['POST'])
def handle_change_location(event, marker):
    event_owner = event['owner']
    event_owner.nearest_node = ox.get_nearest_node(graph, event_owner.location)
    marker.neares_node = ox.get_nearest_node(graph, marker.location)
    shortest_path = nx.dijkstra_path(graph, event_owner.nearest_node, marker.neares_node, 
                                    weight='length')

    if len(path_layer_list) == 1:
        m.remove_layer(path_layer_list[0])
        path_layer_list.pop()
    
    shortest_path_points = nodes.loc[shortest_path]
    path = gpd.GeoDataFrame([LineString(shortest_path_points.geometry.values)], columns=['geometry'])
    path_layer = GeoData(geo_dataframe=path, style={'color':'black', 'weight':2})
    m.add_layer(path_layer)
    path_layer_list.append(path_layer)
    dest_node = ox.get_nearest_node(graph,dest)  
    from_marker.observe(lambda event: handle_change_location(event, to_marker), 'location')
    to_marker.observe(lambda event: handle_change_location(event, from_marker), 'location')
    marker_2.observe((dest,from_marker), 'location')
    m.add_layer(from_marker)
    m.add_layer(to_marker)
    # m.add_layer(marker_2)
    set_nearest_node(from_marker)
    set_nearest_node(to_marker)
    # set_nearest_node(marker_2)
    return render_template('index.html', prediction_text='{}'.format(m))

if __name__ == '__main__':
    app.run(debug=True)
