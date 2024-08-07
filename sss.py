import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import duckdb
from datetime import datetime as dtime
from etl import get_data  # Убедитесь, что этот импорт правильный
from connector import set_connection  # Убедитесь, что этот импорт правильный

# Загрузка данных
tab1_df = get_data('get_v_qual')
tab2_df = get_data('get_v_top_sel')
tab3_df = get_data('get_v_top_product')
tab4_df = get_data('get_v_qual_cat')
tab5_df = get_data('get_v_top_state')  # Исправлено имя переменной

print(tab5_df.head())