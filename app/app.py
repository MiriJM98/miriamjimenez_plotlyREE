import dash
import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objects as go
import pandas as pd
from dash import dcc
from dash.dependencies import Input, Output
from flask import Flask
from sqlalchemy import create_engine, text


# ----------------- CARGAR LOS DATOS ----------------- #
def cargaDatos():
    # Conexion a la BBDD del servidor mySQL
    dialect = 'mysql+pymysql://sistemesbd:bigdata2223@192.168.193.133:3306/alumnes'
    sql = text("SELECT * from natural_gas_miriam ")
    sqlEngine = create_engine(dialect)
    dbConnection = sqlEngine.connect()
    frame = pd.read_sql(sql, dbConnection)
    dbConnection.close()
    return frame


df_gas = cargaDatos()

# ----------------- CAMBIAR NOMBRES DE LAS COLUMNAS ----------------- #
df_gas.columns = ['fecha', 'mes', 'precio']


# ----------------- CONVERTIR PRECIO EN FLOAT ----------------- #
def convertir_string(df):
    df['fecha'] = df['fecha'].astype(str)
    return df


convertir_string(df_gas)

# ----------------- INICIALIZAR LA APP ----------------- #
server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'miriamjimenez_plotlyREE'
app.config.suppress_callback_exceptions = True

# ----------------- SELECTORES ----------------- #
fecha_selector = df_gas['fecha'].unique()

# DÍA INICIAL
dia_inicial = fecha_selector[0]

# ----------------- MÁXIMOS Y MÍNIMOS ----------------- #
precio_maximo = df_gas['precio'].max()
precio_minimo = df_gas['precio'].min()

# ----------------- GRÁFICOS ----------------- #
# ----------------- NAVBAR ----------------- #
navbar = dbc.Navbar(
    [dbc.NavbarBrand(
        "DASHBOARD GAS NATURAL", className="mb-3", style={'textAlign': 'center', 'height': '20px', "margin": "auto", "font-size": "16pt"}),
     ],
    color="dark",
    dark=True
)


# ----------------- SCATTER ----------------- #
grafico_scatter = dbc.Alert([dcc.Graph(id='grafico_scatter',
                                       figure={'data': [
                                          go.Scatter(
                                              x=df_gas['mes'][(
                                                  df_gas['fecha'] == dia_inicial)],
                                              y=df_gas['precio'][(
                                                  df_gas['fecha'] == dia_inicial)],
                                              mode='lines',
                                          )],
                                           'layout':go.Layout(xaxis={'title': 'Mes'}, yaxis={'title': 'Precio'})})],
                            style={'text-align': 'center', 'color': 'black'})

# ----------------- BARRAS ----------------- #
grafico_barras = dbc.Alert([dcc.Graph(id='grafico_barras',
                                      figure={'data': [
                                         go.Bar(
                                             x=df_gas['mes'][(
                                                 df_gas['fecha'] == dia_inicial)],
                                             y=df_gas['precio'][(
                                                 df_gas['fecha'] == dia_inicial)],
                                         )],
                                          'layout':go.Layout(xaxis={'title': 'Mes'}, yaxis={'title': 'Precio'})})
                            ], style={'text-align': 'center', 'color': 'black'})

# ----------------- LAYOUT ----------------- #
app.layout = html.Div(children=[navbar,
                                dbc.Row([
                                    # Selectores
                                    dbc.Col(
                                        html.Div([dcc.Dropdown(fecha_selector, dia_inicial, id='selector_scatter',
                                                               style={'width': '100%', "margin-top": "5px", "margin-bottom": "5px"}), ]), width=2),
                                ]),
                                dbc.Row([
                                    # Gráficos
                                    dbc.Col(
                                        html.Div([grafico_scatter]), width=5),
                                    dbc.Col(
                                        html.Div([grafico_barras]), width=5),
                                    dbc.Col(html.Div([
                                                     dbc.Alert([html.H3("Máximo", className="alert-heading", style={
                                                         'textAlign': 'center'}), html.H3(str(precio_maximo), id="precio_maximo", style={'textAlign': 'center'})]),
                                                     dbc.Alert([html.H3("Mínimo", className="alert-heading", style={
                                                         'textAlign': 'center'}), html.H3(str(precio_minimo), id="precio_minimo", style={'textAlign': 'center'})])
                                                     ]), width=2)
                                ]),
                                html.Br(),
                                dbc.Row([
                                    dbc.Col(html.Div(["Diseñado por Míriam Jiménez"],
                                                     style={'background-color': '#212529', 'color': 'cyan', 'text-align': 'center', 'font-size': '18pt'}))]),
                                ]
                      )


# ----------------- CALLBACKS ----------------- #
# Scatter precio
@app.callback(Output('grafico_scatter', 'figure'),
              Output('precio_maximo', 'children'),
              Output('precio_minimo', 'children'),
              [Input('selector_scatter', 'value'), ])
def update_scatter(fecha_seleccionada):
    x_mes = df_gas['mes'][(df_gas['fecha'] == fecha_seleccionada)]
    y_precio = df_gas['precio'][(df_gas['fecha'] == fecha_seleccionada)]
    maximo = round(y_precio.max(), 2)
    minimo = round(y_precio.min(), 2)

    figure = {'data': [
        go.Scatter(
            x=x_mes,
            y=y_precio,
            mode='lines',
        )],
        'layout': go.Layout(
        xaxis={'title': 'Mes'},
        yaxis={'title': "Precio"},
        title="Precio del gas natural"
    )}
    return figure, maximo, minimo


# Barras precio
@app.callback(Output('grafico_barras', 'figure'),
              [Input('selector_scatter', 'value')])
def update_scatter(fecha_seleccionada):
    x_mes = df_gas['mes'][(df_gas['fecha'] == fecha_seleccionada)]
    y_precio = df_gas['precio'][(df_gas['fecha'] == fecha_seleccionada)]

    figure = {'data': [
        go.Bar(
            x=x_mes,
            y=y_precio,
        )],
        'layout': go.Layout(
        xaxis={'title': 'Mes'},
        yaxis={'title': "Precio"},
        title="Precio del gas natural",
    )}
    return figure


if __name__ == '__main__':
    app.run_server()
