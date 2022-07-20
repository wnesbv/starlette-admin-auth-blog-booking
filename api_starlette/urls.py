
from starlette.routing import Route

from .item.views import item_list, item_details, item_create, item_update, item_delete


routes = [

    Route("/list", item_list),
    Route("/details/{id:int}", item_details),
    Route("/create/", item_create, methods=["GET", "POST"]),
    Route("/update/{id:int}", item_update, methods=["GET", "POST"]),
    Route("/delete/{id:int}", item_delete, methods=["GET", "POST"]),

]
