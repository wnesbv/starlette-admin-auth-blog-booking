
from starlette.routing import Route

from .views import (
    reserve_add,
    reserve_choice,
    reserve_list,
    reserve_detail,
    reserve_update,
    reserve_delete,
)


routes = [
    Route("/", reserve_add, methods=["GET", "POST"]),
    Route("/choice/{id:int}/", reserve_choice, methods=["GET", "POST"]),
    Route("/list", reserve_list),
    Route("/detail/{id:int}/", reserve_detail),
    Route("/update/{id:int}/", reserve_update, methods=["GET", "POST"]),
    Route("/delete/{id:int}/", reserve_delete, methods=["GET", "POST"]),
]
