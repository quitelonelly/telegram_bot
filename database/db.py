from sqlalchemy import create_engine, text
from database.config import settings

sync_engine = create_engine(
    url = settings.DATABASE_URL_psycopg,
    echo = True,
    # pool_size = 5,
    # max_overflow = 10
)

with sync_engine.connect() as conn:
    res = conn.execute(text("SELECT VERSION()"))
    print(f"{res.first()=} ")
