import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Output, Input
from datetime import datetime as dtime
from etl import get_data
import json

tab3_df = get_data('get_v_top_sel')
tab5_df = get_data('get_v_top_state')

tab3_df['timestamp'] = pd.to_datetime(tab3_df['timestamp'])

min_date = tab3_df['timestamp'].min()
max_date = tab3_df['timestamp'].max()
years = tab3_df['timestamp'].dt.year.unique().tolist()
regions = tab3_df['region'].sort_values().unique().tolist()

date_picker_block = dcc.DatePickerRange(
    id='date_prange',
    min_date_allowed=min_date,
    max_date_allowed=max_date,
    display_format='YYYY-MM-DD',
    start_date=min_date.date(),
    end_date=max_date.date()
)

radio_items_block = html.Div(
    children=[
        html.H2('Places'),
        dcc.RadioItems(
            id='radio_items',
            options=[{'label': region, 'value': region} for region in regions],
            value='North',
            inline=True
        )
    ]
)

dropdown_block = dcc.Dropdown(
    id='region_dd',
    options=[
        {'label': c, 'value': c} for c in tab3_df['seller_state'].sort_values().unique().tolist()
    ],
    style={'margin-top': '20px', 'width': '50%'}
)

with open('brazil-states.geojson', 'r') as f:
    brazil_states_geojson = json.load(f)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)
server = app.server

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1('Sales Dashboard', style={'text-align': 'center'}),
                width=12
            )
        ),
        dbc.Row(
            [
                dbc.Col(date_picker_block, width=4),
                dbc.Col(radio_items_block, width=4),
                dbc.Col(dropdown_block, width=4)
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='line_fig'), width=6),
                dbc.Col(dcc.Graph(id='bar_fig'), width=6)
            ]
        ),
        dbc.Row(
            dbc.Col(
                dcc.Graph(id='table_fig'), width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Button('Обновить карту', id='update_button', n_clicks=0),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                dcc.Graph(id='map_fig'), width=12
            )
        )
    ],
    fluid=True
)

@app.callback(
    Output(component_id='line_fig', component_property='figure'),
    Input(component_id='date_prange', component_property='start_date'),
    Input(component_id='date_prange', component_property='end_date'),
    Input(component_id='region_dd', component_property='value'),
    Input(component_id='bar_fig', component_property='clickData')
)
def update_line_plot(start_date, end_date, selected_country, click_data):
    sdate = pd.to_datetime(start_date)
    edate = pd.to_datetime(end_date)
    country_filter = 'All States'
    
    sales = tab3_df.copy(deep=True)

    if selected_country:
        country_filter = selected_country
        sales = sales[sales['seller_state'] == country_filter]
    if start_date and end_date:
        sales = sales[(sales['timestamp'] >= sdate) & (sales['timestamp'] <= edate)]
    if click_data:
        click_cat = click_data['points'][0]['customdata'][0]
        sales = sales[sales['monthkey'] == click_cat]

    sales_summary = sales.groupby(['timestamp'], as_index=False).agg({'orders': 'sum'})

    line_fig = px.line(
        data_frame=sales_summary,
        x='timestamp',
        y='orders',
        title=f'Sales for {country_filter}'
    )

    line_fig.update_layout(template='plotly_dark')
    line_fig.update_layout(showlegend=True)
    line_fig.update_layout({'title': {'text': f'Sales for {country_filter}', 'font': {'weight': 'bold'}}})

    return line_fig

@app.callback(
    Output(component_id='bar_fig', component_property='figure'),
    Input(component_id='date_prange', component_property='start_date'),
    Input(component_id='date_prange', component_property='end_date'),
    Input(component_id='region_dd', component_property='value')
)
def update_bar_plot(start_date, end_date, selected_country):
    sdate = pd.to_datetime(start_date)
    edate = pd.to_datetime(end_date)
    country_filter = 'All States'
    
    tracks = tab3_df.copy(deep=True)

    if selected_country:
        country_filter = selected_country
        tracks = tracks[tracks['seller_state'] == country_filter]
    if start_date and end_date:
        tracks = tracks[(tracks['timestamp'] >= sdate) & (tracks['timestamp'] <= edate)]

    tracks_summary = tracks.groupby('monthkey').agg({'seller_id': 'count'}).reset_index()

    bar_fig = px.bar(
        data_frame=tracks_summary,
        x='monthkey',
        y='seller_id',
        title=f'Sold Tracks Count for {country_filter}',
        labels={'seller_id': 'Count of Sold Tracks'},
        custom_data=['monthkey']
    )
    
    bar_fig.update_layout(template='plotly_dark')
    bar_fig.update_layout({'xaxis': {'type': 'category'}})
    bar_fig.update_layout({'title': {'text': f'Sold Tracks Count for {country_filter}', 'font': {'weight': 'bold'}}})

    return bar_fig

@app.callback(
    Output(component_id='table_fig', component_property='figure'),
    Input(component_id='date_prange', component_property='start_date'),
    Input(component_id='date_prange', component_property='end_date')
)
def update_table(start_date, end_date):
    sdate = pd.to_datetime(start_date)
    edate = pd.to_datetime(end_date)

    filtered_df = tab3_df[(tab3_df['timestamp'] >= sdate) & (tab3_df['timestamp'] <= edate)]

    table_fig = px.imshow(filtered_df.head(10), text_auto=True, title='Top 10 Entries')

    table_fig.update_layout(template='plotly_dark')
    table_fig.update_layout({'title': {'text': 'Top 10 Entries', 'font': {'weight': 'bold'}}})

    return table_fig

@app.callback(
    Output('map_fig', 'figure'),
    Input('update_button', 'n_clicks')
)
def update_map(n_clicks):
    map_fig = px.choropleth_mapbox(
        tab5_df,
        geojson=brazil_states_geojson,
        locations='seller_state',
        featureidkey='properties.sigla',
        color='seller_count',
        hover_name='seller_state',
        hover_data=['seller_count'],
        title='Sales by State'
    )

    map_fig.update_layout(
        mapbox_style='carto-positron',
        mapbox_zoom=3,
        mapbox_center={'lat': -14.2350, 'lon': -51.9253},
        template='plotly_dark',
        paper_bgcolor='blue',
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    return map_fig

if __name__ == '__main__':
    app.run_server(debug=True)
