from fastapi import FastAPI
from app.repositories.customer_repository import list_customers

app = FastAPI()

@app.get("/customers")
def get_customers():
    return list_customers()