#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import plotly.graph_objs as go

import pandas as pd
from colour import Color
from datetime import datetime
from textwrap import dedent as d
import json
import plotly.io as pio
import dash_core_components as dcc

#TODO: Packet filters is sorta broken, need to add in argument for variable to control.

app = dash.Dash(__name__)
app.title = "BLE Tracker"
SLIDER=[1, 100]
ACCOUNT=""

def network_graph(sR, AccountToSearch):
    edge1 = pd.read_csv('graph-Edges.csv', delimiter='*')
    node1 = pd.read_csv('graph-Nodes.csv', delimiter='*')

    accountSet=set()
    for index in range(0,len(edge1)):
        if edge1['TransactionAmt'][index]<sR[0] or edge1['TransactionAmt'][index]>sR[1]:
            edge1.drop(axis=0, index=index, inplace=True)
            continue
        accountSet.add(edge1['Source'][index])
        accountSet.add(edge1['Target'][index])

    shells=[]
    shell1=[]
    shell1.append(AccountToSearch)
    shells.append(shell1)
    shell2=[]
    for ele in accountSet:
        if ele!=AccountToSearch:
            shell2.append(ele)
    shells.append(shell2)


    G = nx.from_pandas_edgelist(edge1, 'Source', 'Target', ['Source', 'Target', 'TransactionAmt'], create_using=nx.MultiDiGraph())
    nx.set_node_attributes(G, node1.set_index('Mac')['Rssi'].to_dict(), 'Rssi')
    nx.set_node_attributes(G, node1.set_index('Mac')['PDU'].to_dict(), 'PDU')
    nx.set_node_attributes(G, node1.set_index('Mac')['Manufacturer'].to_dict(), 'Manufacturer')
    nx.set_node_attributes(G, node1.set_index('Mac')['Local_Name'].to_dict(), 'Local_Name')

    if len(shell2)>1:
        pos = nx.drawing.layout.shell_layout(G, shells)
    else:
        pos = nx.drawing.layout.spring_layout(G)
    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])

    if len(shell2)==0:
        traceRecode = []

        node_trace = go.Scatter(x=tuple([1]), y=tuple([1]), text=tuple([str(AccountToSearch)]), textposition="bottom center",
                                mode='markers+text',
                                marker={'size': 50, 'color': 'turquoise'}) #LightSkyBlue
        traceRecode.append(node_trace)

        node_trace1 = go.Scatter(x=tuple([1]), y=tuple([1]),
                                mode='markers',
                                marker={'size': 50, 'color': 'turquoise'},
                                opacity=0)
        traceRecode.append(node_trace1)

        figure = {
            "data": traceRecode,
            "layout": go.Layout(title='x', showlegend=False,
                                margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                                xaxis={'showgrid': True, 'zeroline': False, 'showticklabels': False},
                                yaxis={'showgrid': True, 'zeroline': False, 'showticklabels': False},
                                height=600
                                )}
        return figure


    traceRecode = []
    colors = list(Color('lightcoral').range_to(Color('darkred'), len(G.edges())))
    colors = ['rgb' + str(x.rgb) for x in colors]

    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        weight = float(G.edges[edge]['TransactionAmt']) / max(edge1['TransactionAmt']) * 10
        trace = go.Scatter(x=tuple([x0, x1, None]), y=tuple([y0, y1, None]),
                           mode='lines',
                           line={'width': weight},
                           marker=dict(color=colors[index]),
                           line_shape='spline',
                           opacity=1)
        traceRecode.append(trace)
        index = index + 1
    node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                            hoverinfo="text", marker={'size': 50, 'color': 'turquoise', 'line': { 'color':'rgb(5, 5, 5)','width':1}})
    index = 0
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        rssi = str(G.nodes[node]['Rssi'])
        pdu = str(G.nodes[node]['PDU'])
        manufacturer = str(G.nodes[node]['Manufacturer'])
        local_name = str(G.nodes[node]['Local_Name'])
        hovertext = "<b>Rssi:</b> " + str(rssi) + "<br>" + "<b>PDU Types:</b> " + pdu + "<br><b>Manufacturer:</b> " + manufacturer + "<br><b>Local Name:</b> " + local_name
        text = node1['Mac'][index]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([hovertext])
        node_trace['text'] += tuple([text])
        index = index + 1

    traceRecode.append(node_trace)
    middle_hover_trace = go.Scatter(x=[], y=[], hovertext=[], mode='markers', hoverinfo="text",
                                    marker={'size': 20, 'color': 'lightcoral'},
                                    opacity=0)
    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        hovertext = "From: " + str(G.edges[edge]['Source']) + "<br>" + "To: " + str(
            G.edges[edge]['Target']) + "<br>" + "# of Packets: " + str(
            G.edges[edge]['TransactionAmt']) + "<br>"
        middle_hover_trace['x'] += tuple([(x0 + x1) / 2])
        middle_hover_trace['y'] += tuple([(y0 + y1) / 2])
        middle_hover_trace['hovertext'] += tuple([hovertext])
        index = index + 1

    traceRecode.append(middle_hover_trace)
    figure = {
        "data": traceRecode,
        "layout": go.Layout(title='', showlegend=False, hovermode='closest',
                            margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                            xaxis={'showgrid': True, 'zeroline': False, 'showticklabels': False, 'gridcolor':'lightgrey'},
                            yaxis={'showgrid': True, 'zeroline': False, 'showticklabels': False, 'gridcolor':'lightgrey'},
                            height=1100,
                            clickmode='event+select',
                            annotations=[
                                dict(
                                    ax=(G.nodes[edge[0]]['pos'][0] + G.nodes[edge[1]]['pos'][0]) / 2,
                                    ay=(G.nodes[edge[0]]['pos'][1] + G.nodes[edge[1]]['pos'][1]) / 2, axref='x', ayref='y',
                                    x=(G.nodes[edge[1]]['pos'][0] * 3 + G.nodes[edge[0]]['pos'][0]) / 4,
                                    y=(G.nodes[edge[1]]['pos'][1] * 3 + G.nodes[edge[0]]['pos'][1]) / 4, xref='x', yref='y',
                                    showarrow=True,
                                    arrowhead=3,
                                    arrowsize=4,
                                    arrowwidth=1,
                                    opacity=1
                                ) for edge in G.edges]
                            )}
    return figure
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
app.layout = html.Div([
    html.Div([html.H1("Bluetooth Low Energy Asset and Personnel Tracking")],
             className="row",
             style={'textAlign': "center"}),
    
    html.Div(
        className="row",
        children=[
            html.Div(
                className="one columns",
                children=[
                    dcc.Markdown(d("""
                            **Packet Filtering:**
                            Slide the bar to define # of packets.
                            """)),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.RangeSlider(
                                id='my-range-slider',
                                min=1,
                                max=100,
                                step=1,
                                value=[10, 100],
                                marks={
                                    1: {'label': '1'},
                                    10: {'label': '10'},
                                    20: {'label': '20'},
                                    30: {'label': '30'},
                                    40: {'label': '40'},
                                    50: {'label': '50'},
                                    60: {'label': '60'},
                                    70: {'label': '70'},
                                    80: {'label': '80'},
                                    100: {'label': '100'}
                                }
                            ),
                            html.Br(),
                            html.Div(id='output-container-range-slider')

                        ],
                        style={'height': '60', 'width': '600', 'textAlign': "center"}
                    ),
                    html.Div(
                        className="one columns",
                        children=[
                            dcc.Markdown(d("""
                            **MAC Address Search:**""")),
                            dcc.Input(id="input1", type="text", placeholder="Input the MAC to centralize."),
                            html.Div(id="output")
                        ],
                        style={'height': '60', 'width': '100', 'textAlign': 'center'}
                    )
                ]
            ),
            html.Div(
                className="twenty-two columns",
                children=[dcc.Graph(id="my-graph", figure=network_graph(SLIDER, ACCOUNT))],
                style={'textAlign': "center"}
            ),
        ]
    )
])
@app.callback(
    dash.dependencies.Output('my-graph', 'figure'),
    [dash.dependencies.Input('my-range-slider', 'value'), dash.dependencies.Input('input1', 'value')])
def update_output(value,input1):
    SLIDER = value
    ACCOUNT = input1
    return network_graph(value, input1)

if __name__ == '__main__':
    app.run_server(debug=False)