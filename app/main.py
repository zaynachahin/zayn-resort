from fastapi import FastAPI, HTTPException, status

from app.repositories.customer_repository import (
    list_customers, 
    get_customer_by_id,
    get_customer_by_cpf,
    get_customer_by_cpf_excluding_id,
    create_customer,
    update_customer,
    patch_customer
)
    
from app.schemas.customer_schema import CustomerCreate, CustomerUpdate, CustomerPatch

from uuid import UUID


app = FastAPI()


@app.get("/customers", status_code=status.HTTP_200_OK)
def get_customers():
    customers = list_customers()

    response = []

    for customer in customers:
        response.append(
            {
                "customer_id": customer[0],
                "full_name": customer[1],
                "date_of_birth": customer[2],
                "cpf": customer[3],
                "newsletter_opt_in": customer[4],
            }
        )

    return response


@app.get("/customers/{customer_id}", status_code=status.HTTP_200_OK)
def get_customer(customer_id: UUID):
    customer = get_customer_by_id(customer_id)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "Customer not found"
            )
    
    return {
        "customer_id": customer[0][0],
        "full_name": customer[0][1],
        "date_of_birth": customer[0][2],
        "cpf": customer[0][3],
        "newsletter_opt_in": customer[0][4],
    }


@app.post("/customers", status_code= status.HTTP_201_CREATED)
def create_customer_endpoint(customer: CustomerCreate):
    existing_customer = get_customer_by_cpf(customer.cpf)

    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
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

@app.put("/customers/{customer_id}", status_code= status.HTTP_200_OK)
def update_customer_endpoint(customer_id:UUID, customer: CustomerUpdate):
    existing_cpf = get_customer_by_cpf_excluding_id(customer.cpf, customer_id)

    if existing_cpf:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CPF is registered"
        )
    
    updated_customer = update_customer(
        customer_id,
        customer.full_name,
        customer.date_of_birth,
        customer.cpf,
        customer.newsletter_opt_in
    )

    if not updated_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return {
        "message": "Customer updated",
        "customer_id": updated_customer[0][0]
    }

@app.patch("/customers/{customer_id}", status_code=status.HTTP_200_OK)
def patch_customer_endpoint(customer_id:UUID, customer: CustomerPatch):
    fields = customer.model_dump(exclude_unset=True)

    if not fields:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail = "No input provided"
        )

    registered_customer = get_customer_by_id(customer_id)

    if not registered_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "Customer not found"
        )
    
    if "cpf" in fields:
        existing_customer = get_customer_by_cpf_excluding_id(fields["cpf"], customer_id)

        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CPF is registered"
                )

    updated_customer = patch_customer(customer_id, fields)
    
    return {
        "message": "Customer updated",
        "customer_id": updated_customer[0][0]
    }