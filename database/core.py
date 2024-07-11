from sqlalchemy import text
from database.db import sync_engine
from database.models import metadata_obj

def create_tables():
    metadata_obj.create_all(sync_engine)
    
# def insert_data():
#     with sync_engine.connect() as conn:
#         stmt = """INSERT INTO users (username) VALUES 
#             ('AO Bobr'),
#             ('OOO Volk');"""
#         conn.execute(text(stmt))