import sqlalchemy
from sqlalchemy.orm import declarative_base

metadata = sqlalchemy.MetaData()
Base = declarative_base(metadata=metadata)
