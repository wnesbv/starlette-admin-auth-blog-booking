
from starlette.routing import Route

from .views import (
    cmt_item_create,
    cmt_service_create,
    cmt_rent_create,
    cmt_item_update,
    cmt_service_update,
    cmt_rent_update,
    cmt_delete,
)

routes = [

    Route("/item/create/{id:int}", cmt_item_create, methods=["GET", "POST"]),
    Route("/service/create/{id:int}", cmt_service_create, methods=["GET", "POST"]),
    Route("/rent/create/{id:int}", cmt_rent_create, methods=["GET", "POST"]),
    #..
    Route("/item/update/{id:int}", cmt_item_update, methods=["GET", "POST"]),
    Route("/service/update/{id:int}", cmt_service_update, methods=["GET", "POST"]),
    Route("/rent/update/{id:int}", cmt_rent_update, methods=["GET", "POST"]),
    #..
    Route("/delete/{id:int}", cmt_delete, methods=["GET", "POST"]),
]
