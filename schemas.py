from datetime import datetime

from pydantic import BaseModel


class ProductBase(BaseModel):
    title: str
    available: str
    price: int
    image: str
    url: str


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
