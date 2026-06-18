from app.database import execute_query

def list_customers():
    query = """
    SELECT *
    FROM customers
    """

    customers = execute_query(query, fetch=True)
    return customers


def get_customer_by_uuid(customer_id):
    query = """
    SELECT id, full_name, date_of_birth, cpf, newsletter_opt_in 
    FROM customers
    WHERE id = %s;
    """

    params = (str(customer_id),)

    customer = execute_query(query, params, fetch=True)
    return customer