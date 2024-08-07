from connector import set_connection
import pandas as pd

with open('queriess/ddl.sql') as f:
    query=f.read()

with set_connection() as dc:
    dc.execute(query)
    tables = [ 
        'sellers',
        'products',
        'orders',
        'order_reviews', 
        'order_items' 
        ]
    
    for table in tables:                
        df = pd.read_csv(f'source/{table}.csv')
        dc.query(f"""
            insert into {table}
            select *
            from df
        """)