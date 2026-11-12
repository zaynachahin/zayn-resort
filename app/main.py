from fastapi import FastAPI
from app.routes import room_category_routes, room_routes, customer_routes, reservation_routes

app = FastAPI(
    title="Zayn Resort API",
    description="A hotel reservation REST API — managing room availability, booking conflicts, and reservation lifecycle from confirmation to check-out.",
    version="1.0.0",
)

app.include_router(room_category_routes.router)
app.include_router(room_routes.router)
app.include_router(customer_routes.router)
app.include_router(reservation_routes.router)