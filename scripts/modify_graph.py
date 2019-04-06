# -*- coding: utf-8 -*-
"""
Modified on Feb 1 2019
@author: tjwied

Features added: Color by user sentiment score

Original template created on Mon Oct 29 2018
@author: jingwenken
"""

import pandas as pd
import dash
import pickle
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import networkx as nx
import os

#edgelist = '/home/rubisco/Desktop/insight/dash/final/monero.grid'

#create graph G
def plot_graph(edgelist):
    basename_extract = os.path.basename(edgelist)
    pkl_file = open(basename_extract[:-4]+'pkl', 'rb') #open file with sentiments
    values = pickle.load(pkl_file)

    G=nx.read_edgelist(edgelist, delimiter=":") #define graph with an edgelist
    degree = nx.degree(G)
    pos = nx.layout.spring_layout(G, ) #x,y positions of each node
    for node in G.nodes:    #as pos attribute for each node
        G.nodes[node]['pos'] = list(pos[node])

    pos=nx.get_node_attributes(G,'pos')

    dmin=1
    ncenter=0
    for n in pos:
        x,y=pos[n]
        d=(x-0.5)**2+(y-0.5)**2
        if d<dmin:
            ncenter=n
            dmin=d
    p=nx.single_source_shortest_path_length(G,ncenter)

    #Create Edges
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5,color='#888'),
        hoverinfo='none',
        mode='lines')

    for edge in G.edges():
        x0, y0 = G.node[edge[0]]['pos']
        x1, y1 = G.node[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='RdBu',
            reversescale=True,
            color=[],
            size=[],
            colorbar=dict(
                thickness=15,
                title='Sentiment',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=2)))

    for node in G.nodes():
        x, y = G.node[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])

    #add color to node points
    for node in G.nodes:
        if node in values:
            node_trace['marker']['color'] += tuple([values[node]])
            for deg in degree:
                if deg[0] == node:
                    num = deg[1]
                    numb = [10+2*float(num)]
                    node_trace['marker']['size']  += tuple(numb)
        if node not in values:
            node_trace['marker']['color'] += tuple([0])
            for deg in degree:
                if deg[0] == node:
                    num = deg[1]
                    numb = [10+2*float(num)]
                    node_trace['marker']['size']  += tuple(numb)

    for node, adjacencies in enumerate(G.adjacency()):
        #node_trace['marker']['color']+=tuple([len(adjacencies[1])])
        node_info = 'Name: ' + str(adjacencies[0]) + '<br># of connections: '+str(len(adjacencies[1]))
        node_trace['text']+=tuple([node_info])
    return G, edge_trace, node_trace, G.edges(), G.nodes()
