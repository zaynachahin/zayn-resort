from fastapi import FastAPI, HTTPException, status

from app.repositories.customer_repository import (
    list_customers, 
    get_customer_by_id,
    get_customer_by_cpf,
    create_customer
)
    
from app.schemas.customer_schema import CustomerCreate

from uuid import UUID


app = FastAPI()


@app.get("/customers")
def get_customers():
    return list_customers()


@app.get("/customers/{customer_id}")
def get_customer(customer_id: UUID):
    customer = get_customer_by_id(customer_id)

    if not customer:
        raise HTTPException(
            status_code=404,
            detail= "Customer not found"
            )
    
    return customer[0]


@app.post("/customers", status_code= status.HTTP_201_CREATED)
def create_customer_endpoint(customer: CustomerCreate):
    existing_customer = get_customer_by_cpf(customer.cpf)

    if existing_customer:
        raise HTTPException(
            status_code=409,
            detail= "CPF is registered"
            )
    
    customer_id = create_customer(
        customer.full_name,
        customer.date_of_birth,
        customer.cpf,
        customer.newsletter_opt_in
        )
        
    return {
        "message": "Customer created",
        "customer_id": customer_id
        }