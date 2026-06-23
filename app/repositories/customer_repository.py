from app.database import execute_query

def list_customers():
    query = """
    SELECT *
    FROM customers
    """

    customers = execute_query(query, fetch=True)
    return customers


def get_customer_by_id(customer_id):
    query = """
    SELECT id, full_name, date_of_birth, cpf, newsletter_opt_in 
    FROM customers
    WHERE id = %s;
    """

    params = (str(customer_id),)

    customer = execute_query(query, params, fetch=True)
    return customer


def create_customer(full_name, date_of_birth, cpf, newsletter_opt_in):
    query = """
    INSERT INTO customers(
    full_name,
    date_of_birth,
    cpf,
    newsletter_opt_in,
    created_at
    )
    VALUES(
    %s,
    %s,
    %s,
    %s,
    NOW()
    )
    RETURNING id;
    """

    params = (
        full_name,
        date_of_birth,
        cpf,
        newsletter_opt_in
    )

    result = execute_query(query, params, fetch=True)
    return result[0][0]