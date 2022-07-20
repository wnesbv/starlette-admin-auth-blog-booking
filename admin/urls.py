
from starlette.routing import Route

from .import user, item, service, schedule, rent, comment


routes = [

    Route("/", item.all_list),
    #..
    Route("/user/list", user.item_list),
    Route("/user/details/{id:int}", user.item_details),
    Route("/user/create/", user.item_create, methods=["GET", "POST"]),
    Route("/user/update/{id:int}", user.item_update, methods=["GET", "POST"]),
    Route("/item/delete/{id:int}", item.item_delete, methods=["GET", "POST"]),
    #..
    Route("/item/list", item.item_list),
    Route("/item/details/{id:int}", item.item_details),
    Route("/item/create/", item.item_create, methods=["GET", "POST"]),
    Route("/item/update/{id:int}", item.item_update, methods=["GET", "POST"]),
    Route("/item/delete/{id:int}", item.item_delete, methods=["GET", "POST"]),
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
    #..
    Route("/comment/item/create/{id:int}", comment.cmt_item_create, methods=["GET", "POST"]),
    Route("/comment/service/create/{id:int}", comment.cmt_service_create, methods=["GET", "POST"]),
    Route("/comment/rent/create/{id:int}", comment.cmt_rent_create, methods=["GET", "POST"]),
    #..
    Route("/comment/item/update/{id:int}", comment.cmt_item_update, methods=["GET", "POST"]),
    Route("/comment/service/update/{id:int}", comment.cmt_service_update, methods=["GET", "POST"]),
    Route("/comment/rent/update/{id:int}", comment.cmt_rent_update, methods=["GET", "POST"]),
    #..
    Route("/comment/delete/{id:int}", comment.cmt_delete, methods=["GET", "POST"]),

]
