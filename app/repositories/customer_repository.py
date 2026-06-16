from app.database import execute_query

def list_customers():
    query = """
    SELECT *
    FROM customers
    """

    customers = execute_query(query, fetch=True)
    return customers