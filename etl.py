import pandas as pd
from connector import set_connection

def read_query(query_name):
    with open(f'queriess/{query_name}.sql', 'r') as f:
        return f.read()
    
def get_data(query_name):
    query=read_query(query_name)
    with set_connection() as dc:
        return dc.query(query).to_df()