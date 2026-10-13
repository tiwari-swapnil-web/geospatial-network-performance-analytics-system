from typing import List, Union

from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None


class PolygonBase(BaseModel):
    objectId: int
    '''iso: str
    id_0: int
    name_0: str
    id_1: int
    name_1: str
    id_2: int
    name_2: str
    id_3: int
    name_3: str
    type: str
    engtype_3: str
    nl_name_3: str
    varname_3: str'''
    pass


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: List[Item] = []

    class Config:
        from_attributes = True

# map polygon class goes here

class MasterPolygonCreate(PolygonBase):
    pass

class MasterPolygon(PolygonBase):
    objectId: int
    iso: str
    id_0: int
    name_0: str
    id_1: int
    name_1: str
    id_2: int
    name_2: str
    id_3: int
    name_3: str
    type: str
    engtype_3: str
    nl_name_3: str
    varname_3: str

    class Config:
        from_attributes = True
