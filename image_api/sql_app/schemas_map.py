from typing import List, Union
from pydantic import BaseModel



class SubgridSchema(BaseModel):
    __tablename__ = "subgrids"

    id: int
    image: str

    pt_lat: float
    pt_lon: float

    build_prob: float
    foliage_prob: float

    class_: str


class CentresSchema(BaseModel):
    __tablename__ = "cluster_centres"

    id: int
    area: str

    centre_lat: float
    centre_lon: float

