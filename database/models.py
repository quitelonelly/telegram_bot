from sqlalchemy import Table, Column, Integer, String, MetaData

metadata_obj = MetaData()

users_table = Table(
    "users",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", String)
)