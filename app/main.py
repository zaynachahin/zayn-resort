from fastapi import FastAPI
from app.routes import room_category_routes, room_routes, customer_routes

app = FastAPI()

app.include_router(room_category_routes.router)
app.include_router(room_routes.router)
app.include_router(customer_routes.router)