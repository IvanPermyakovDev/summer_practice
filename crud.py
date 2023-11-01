from sqlalchemy.orm import Session

import schemas
import models


def get_products(db: Session, offset: int | None = None, limit: int | None = None):
    query = db.query(models.Product)

    if offset is not None:
        query = query.offset(offset)

    if limit is not None:
        query = query.limit(limit)

    return query.all()


def delete_products(db: Session):
    db.query(models.Product).delete()
    db.commit()
    return


def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_product_by_url(db: Session, product_url: str):
    return db.query(models.Product).filter(models.Product.url == product_url).first()


def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, db_product: models.Product, product: schemas.ProductBase):
    # Update model class variable from requested fields
    for var, value in vars(product).items():
        setattr(db_product, var, value) if value or str(value) == 'False' else None

    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, db_product: models.Product):
    db.delete(db_product)
    db.commit()

    return True
