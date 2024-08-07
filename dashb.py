import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Output, Input
from datetime import datetime as dtime
from etl import get_data

# Загрузка данных
tab1_df = get_data('get_v_qual')
tab2_df = get_data('get_v_top_product')
tab3_df = get_data('get_v_top_sel')
tab4_df = get_data('get_v_qual_cat')
tab5_df = get_data('get_v_top_state')

# Преобразование столбца timestamp в datetime
tab3_df['timestamp'] = pd.to_datetime(tab3_df['timestamp'])

# Определение минимальной и максимальной даты
min_date = tab3_df['timestamp'].min()
max_date = tab3_df['timestamp'].max()
years = tab3_df['timestamp'].dt.year.unique().tolist()
regions = tab3_df['region'].sort_values().unique().tolist()

# Определение блоков интерфейса
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

# Определение дашборда
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

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
        sales = sales.query(f"seller_state == '{country_filter}'")
    if start_date and end_date:
        sales = sales[(sales['timestamp'] >= sdate) & (sales['timestamp'] <= edate)]
    if click_data:
        click_cat = click_data['points'][0]['customdata'][0]
        sales = sales.query(f"monthkey == {click_cat}")

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
        tracks = tracks.query(f"seller_state == '{country_filter}'")
    if start_date and end_date:
        tracks = tracks[(tracks['timestamp'] >= sdate) & (tracks['timestamp'] <= edate)]

    tracks_summary = tracks.groupby('monthkey').agg({'seller_id': 'count'}).reset_index()

    bar_fig = px.bar(
        data_frame=tracks_summary,
        x='monthkey',
        y='seller_id',
        title=f'Sold Tracks Count for {country_filter}',
        labels={'seller_id': 'Count of Sold Tracks'}
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

    # Преобразование DataFrame в таблицу Plotly
    table_fig = px.imshow(filtered_df.head(10), text_auto=True, title='Top 10 Entries')

    table_fig.update_layout(template='plotly_dark')
    table_fig.update_layout({'title': {'text': 'Top 10 Entries', 'font': {'weight': 'bold'}}})

    return table_fig

if __name__ == '__main__':
    app.run_server(debug=True)
