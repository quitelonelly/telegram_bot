from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

metadata_obj = MetaData()

users_table = Table(
    "users",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", String),
    Column("userphone", String),
    Column("usertgid", Integer),
)

orders_table = Table(
    "orders",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("client_name", String),
    Column("client_phone", String),
    Column("client_tgid", String),
    Column("client_time", String)
)