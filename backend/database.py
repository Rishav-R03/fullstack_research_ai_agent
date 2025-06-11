from sqlalchemy import create_engine 
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker 

dburl = URL.create(
    drivername="postgresql",
    username="postgres",
    password="root123",
    database="smartresearchagent",
    port=5432
)

engine = create_engine(dburl)
Session = sessionmaker(bind=engine) 
session = Session()
