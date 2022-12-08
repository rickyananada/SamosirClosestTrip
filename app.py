from flask import Flask, render_template, url_for, request
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer
import networkx as nx
import osmnx as ox
import geopandas as gpd
import json
from ipyleaflet import *
import folium

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/closest')
def closest():
    return render_template('closest.html')

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/predict', methods=['POST'])
def predict():
    start_x = float(request.form['start_x'])
    start_y= float(request.form['start_y'])
    end_x = float(request.form['end_x'])
    end_y= float(request.form['end_y'])
    
    ox.config(log_console=True, use_cache=True)
    start_latlng = (start_x,start_y)
    end_latlng = (end_x,end_y)
    place = 'Samosir, North Sumatra, Indonesia'
    mode      = 'walk' 
    optimizer = 'length'  
    graph = ox.graph_from_place(place, network_type = mode)
    orig_node = ox.get_nearest_node(graph, start_latlng)
    dest_node = ox.get_nearest_node(graph, end_latlng)
    shortest_route = nx.shortest_path(graph, orig_node,dest_node,weight=optimizer)
    shortest_route_map = ox.plot_route_folium(graph, shortest_route)
    start_marker = folium.Marker(
            location = start_latlng,
            popup = start_latlng,
            icon = folium.Icon(color='green'))
    end_marker = folium.Marker(
                location = end_latlng,
                popup = end_latlng,
                icon = folium.Icon(color='red'))
    start_marker.add_to(shortest_route_map)
    end_marker.add_to(shortest_route_map)
    # folium.TileLayer('openstreetmap').add_to(shortest_route_map)
    # folium.LayerControl().add_to(shortest_route_map)
    shortest_route_map.save('templates/map.html')
    return render_template('map.html')
   
if __name__ == '__main__':
    app.run(debug=True)
