import pandas as pd
from sqlalchemy import create_engine

dbname = 'orderboxbotdb'
user = 'postgres'
password = 'sObW}smNk9'
host = 'localhost'
port = '5432'

engine_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
engine = create_engine(engine_string)

ua_df = pd.read_sql_table('user_actions', engine)
ua_df = ua_df.drop(['timestamp', 'action', 'id'], axis=1).drop_duplicates()
ua_df.to_sql("users", engine)