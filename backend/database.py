from sqlalchemy import create_engine 
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker 
import os 
dburl = URL.create(
    drivername="postgresql",
    username="postgres",
    password=os.getenv("POSTGRESQL_PASSWORD"),
    database="smartresearchagent",
    port=5432,
    host="localhost"
)

engine = create_engine(dburl)
Session = sessionmaker(bind=engine) 
session = Session()
