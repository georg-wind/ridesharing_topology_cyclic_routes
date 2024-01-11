# Import required libraries
import dash
import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objects as go
from dash import dcc
from dash.dependencies import Input, Output

from _05_dashboard.graph_visualisation import generate_base_graph_traces, build_vis_df, generate_node_traces
from utils import pickle_loader, topologies, shortest_path_modes, xrange, numreqs, get_all_x

# 0. set initial parameters
topology = topologies[0]
mode = shortest_path_modes[0]
## TODO:
# xrange = get_all_x(topology, mode, )
x = xrange[1]  # request-value x for the data used in the analysis

pickle_path_graph = f'./data/graphs/{topology}_{mode}_x_{str(float(x))}_nreq_{numreqs}_graph.pkl'
G = pickle_loader(pickle_path_graph)
print("Graph loaded.")

letter_5_base_net = {"nodes":
                         {"A": (-1.0, 1.0),
                          "B": (1.0, 1.0),
                          "C": (1.0, -1.0),
                          "D": (-1.0, -1.0),
                          "E": (0.0, 0.0)},
                     "edges": [("A", "B"), ("B", "C"), ("C", "D"), ("A", "D"), ("A", "E"), ("B", "E"), ("C", "E"),
                               ("D", "E")]
                     }

## DASHBOARD
base_traces = generate_base_graph_traces(letter_5_base_net)
df = build_vis_df(G, letter_5_base_net)
node_traces_on_lvls = generate_node_traces(df)
fig = go.Figure(data=node_traces_on_lvls + base_traces,
                skip_invalid=True)

# Initialize the Dash app

# Prepare edge options for the Checklist
edge_options = [{'label': '-'.join(edge), 'value': '-'.join(edge)}
                for edge in sorted(letter_5_base_net['edges'])]

# Prepare initial values for the Checklist
# initial_values = ['-'.join(edge) for edge in letter_5_base_net['edges']]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.layout = dbc.Container([
    dbc.Row([  # Single row with two columns inside for horizontal arrangement

        # Checklist Column
        dbc.Col([
            html.Label("Select Edges:", className="mb-2"),  # Label for the checklist
            dbc.Card([
                dbc.CardBody([
                    dcc.Checklist(
                        id='edge-selector',
                        options=edge_options,
                        value=[]
                    )
                ])
            ])
        ], width=2),  # Adjust width as required

        # Graph Column
        dbc.Col([
            dcc.Graph(
                id='route-space-3d-scatter',
                figure=fig,
                style={'height': '100vH'}
            )
        ], width=8)  # Adjust width as required

    ])
], fluid=True)


@app.callback(
    Output('route-space-3d-scatter', 'figure'),
    Input('edge-selector', 'value')
)
def update_node_selection(selected_edges):
    # filter edges
    selected_edges = [tuple(string_value.split('-')) for string_value in selected_edges]
    # TODO: implement this as a toggle to switch between modes: if <selected_edges> in set <-> if <selected_edges> == set
    if True:
        mask = (df[selected_edges] == 1).all(axis=1)
    # else:
    #     unselected_edges = [edge for edge in letter_5_base_net['edges'] if edge not in selected_edges]
    #     mask = (df[unselected_edges] == 0).all(axis=1)

    # Filter the DataFrame using the mask
    df_new = df[mask]

    # build new node-traces
    updated_node_traces_on_lvls = generate_node_traces(df_new)
    # update figure
    fig = go.Figure(data=updated_node_traces_on_lvls + base_traces,
                    skip_invalid=True)
    return fig
