from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

# db
Base = declarative_base()
engine = create_engine(
    'mssql+pyodbc://n111404:linebot1234@140.131.114.241:1433/111-linebotcalender?driver=SQL+Server+Native+Client+11.0',
    echo=True)
