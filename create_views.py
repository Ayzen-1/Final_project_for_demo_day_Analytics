from connector import set_connection

with open('queriess/create_v.sql', 'r') as f:
    with set_connection() as dc:
        dc.execute(f.read())