import sys
sys.path

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from geoalchemy2 import Geography, Geometry
from geoalchemy2.shape import from_shape

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")



class Subgrid(Base):
    __tablename__ = "subgrids"

    id = Column(Integer, primary_key=True)
    image = Column(String)

    pt_lat = Column(Float)
    pt_lon = Column(Float)

    build_prob = Column(Float)
    foliage_prob = Column(Float)

    class_ = Column(String)

    #amsl = Column(Float)


class SubgridGeo(Base):
    __tablename__ = "subgrids_geo"

    id = Column(Integer, primary_key=True)
    image = Column(String)

    pt_lat = Column(Float)
    pt_lon = Column(Float)

    build_prob = Column(Float)
    foliage_prob = Column(Float)

    class_ = Column(String)

    amsl = Column(Float)

    #geometry = Column(Geography('POLYGON'), nullable=False)



class Polygon(Base):
    __tablename__ = "polygon"

    id = Column(Integer, primary_key=True)
    geometry = Column(Geography('POLYGON'), nullable=False)



class MasterPolygon(Base):
    __tablename__ = "master_polygon"

    objectId = Column(Integer, primary_key=True, index=True)
    iso = Column(String)
    id_0 = Column(Integer)
    name_0 = Column(String)
    id_1 = Column(Integer)
    name_1 = Column(String)
    id_2 = Column(Integer)
    name_2 = Column(String)
    id_3 = Column(Integer)
    name_3 = Column(String)
    type = Column(String)
    engtype_3 = Column(String)
    nl_name_3 = Column(String)
    varname_3 = Column(String)