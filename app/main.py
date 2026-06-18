from fastapi import FastAPI, HTTPException

from app.repositories.customer_repository import (
    list_customers, 
    get_customer_by_uuid
)

from uuid import UUID

app = FastAPI()


@app.get("/customers")
def get_customers():
    return list_customers()


@app.get("/customers/{customer_id}")
def get_customer(customer_id: UUID):
    customer = get_customer_by_uuid(customer_id)

    if not customer:
        raise HTTPException(
            status_code=404, 
            detail= "Customer not found"
            )
    
    return customer[0]