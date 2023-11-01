from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.responses import Response

from database import SessionLocal, engine
from sqlalchemy.orm import Session

import schemas
import models
import crud

from tasks.scheduler import app as app_rocketry

session = app_rocketry.session

models.Base.metadata.create_all(bind=engine)

description = """
    Предоставляет возможность взаимодействия с данными, полученными с сайта SP-COMPUTERS. 🖥️
    
    Парсер запускается каждые 6 часа. По умолчанию, он выключен. Для проверки состояния парсера воспользуйтесь соответствующим методом.
    """

app = FastAPI(description=description)


# Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Task
# ----

router_task = APIRouter(tags=["task"])


@router_task.get("/parser/status/")
async def status_parser_task():
    task = session['do_parse_data_from_sp_computers']

    # state = "Выключен" if task.disabled else "Включен"

    return Response(status_code=status.HTTP_200_OK,
                    content=f"Статус парсера: {not task.disabled}")


@router_task.post("/parser/enable/")
async def enable_parser_task():
    task = session['do_parse_data_from_sp_computers']
    task.disabled = False
    return Response(status_code=status.HTTP_200_OK,
                    content="Парсер запущен! Каждые 4 часа данные будут обновлятся.")


@router_task.post("/parser/disable/")
async def disable_parser_task():
    task = session['do_parse_data_from_sp_computers']
    task.disabled = True

    return Response(status_code=status.HTTP_200_OK,
                    content="Парсер выключен.")


@router_task.post("/parser/run/")
async def run_parser_task():
    task = session['do_parse_data_from_sp_computers']
    task.force_run = True

    return Response(status_code=status.HTTP_200_OK,
                    content="Парсер принудительно запущен. Скоро данные обновятся.")


@router_task.post("/parser/terminate/")
async def terminate_parser_task():
    task = session['do_parse_data_from_sp_computers']
    task.terminate()

    return Response(status_code=status.HTTP_200_OK,
                    content="Парсер принудительно остановлен. Вероятно, данные были обработаны не полность.")


# PRODUCTS
# ----

router_products = APIRouter(tags=["products"])


@router_products.post("/products/", response_model=schemas.Product)
async def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = crud.get_product_by_url(db, product_url=product.url)

    if db_product:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="This product_url already registered.")

    return crud.create_product(db=db, product=product)


@router_products.get("/products/", response_model=list[schemas.Product])
async def read_products(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.get_products(db, offset=offset, limit=limit)

    # response = schemas.ProductResponse(data=products)
  
    return products


@router_products.delete("/products/")
async def delete_products(db: Session = Depends(get_db)):
    crud.delete_products(db)
    return Response(status_code=status.HTTP_200_OK,
                    content="Таблица 'products' была очищена.")


@router_products.get("/products/{product_id}", response_model=schemas.Product)
async def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found.")
    return db_product


@router_products.put("/products/{product_id}", response_model=schemas.Product)
async def update_product(product_id: int, product: schemas.ProductBase, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)

    if db_product is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Product not found.")

    db_product = crud.update_product(db, db_product, product)
    return db_product


@router_products.delete("/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found.")

    crud.delete_product(db, db_product)
    return Response(status_code=status.HTTP_200_OK,
                    content=f"Запись (ID: {product_id}) удалена из базы данных.")

app.include_router(router_task)
app.include_router(router_products)

# if __name__ == '__main__':
#     uvicorn.run(app, host='0.0.0.0', port=8080)
