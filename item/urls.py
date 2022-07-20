
from starlette.routing import Route

from .import views, service, schedule, rent


routes = [

    Route("/list", views.item_list),
    Route("/details/{id:int}", views.item_details),
    Route("/create/", views.item_create, methods=["GET", "POST"]),
    Route("/update/{id:int}", views.item_update, methods=["GET", "POST"]),
    Route("/delete/{id:int}", views.item_delete, methods=["GET", "POST"]),
    #...
    Route("/service/list", service.item_list),
    Route("/service/details/{id:int}", service.item_details),
    Route("/service/create/", service.item_create, methods=["GET", "POST"]),
    Route("/service/update/{id:int}", service.item_update, methods=["GET", "POST"]),
    Route("/service/delete/{id:int}", service.item_delete, methods=["GET", "POST"]),
    #...
    Route("/rent/list", rent.item_list),
    Route("/rent/details/{id:int}", rent.item_details),
    Route("/rent/create/", rent.item_create, methods=["GET", "POST"]),
    Route("/rent/update/{id:int}", rent.item_update, methods=["GET", "POST"]),
    Route("/rent/delete/{id:int}", rent.item_delete, methods=["GET", "POST"]),
    #...
    Route("/schedule/list", schedule.item_list),
    Route(
        "/schedule/details/{id:int}",
        schedule.item_details,
        methods=["GET", "POST"]
    ),
    Route("/schedule/create/", schedule.item_create, methods=["GET", "POST"]),
    Route("/schedule/update/{id:int}", schedule.item_update, methods=["GET", "POST"]),
    Route("/schedule/delete/{id:int}", schedule.item_delete, methods=["GET", "POST"]),

]
