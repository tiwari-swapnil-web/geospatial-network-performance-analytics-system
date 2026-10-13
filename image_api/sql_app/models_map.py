import sys
sys.path

from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Column, Integer, String, Float
#from sql_app.database_sql import Base
from database_sql import Base

#from database import Base

Base = declarative_base()


class Subgrid(Base):
    __tablename__ = "subgrids"

    id = Column(Integer, primary_key=True)
    image = Column(String)

    pt_lat = Column(Float)
    pt_lon = Column(Float)

    build_prob = Column(Float)
    foliage_prob = Column(Float)

    class_ = Column(String)



class Centres(Base):
    __tablename__ = "cluster_centres"

    id = Column(Integer, primary_key=True)
    area = Column(String)

    centre_lat = Column(Float)
    centre_lon = Column(Float)