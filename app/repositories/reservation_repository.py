from app.database import execute_query

def get_reservation_by_id(id):
    query= """
    SELECT id, customer_id, room_id, check_in, check_out, status, total_amount
    FROM reservations
    WHERE id = %s AND deleted_at IS NULL;
    """

    params= (id,)

    result = execute_query(query, params, fetch=True)
    return result

def list_reservations():
    query = """
    SELECT id, customer_id, room_id, check_in, check_out, status, total_amount
    FROM reservations 
    WHERE deleted_at IS NULL;
    """

    result = execute_query(query, fetch=True)
    return result

def get_conflicting_reservations(room_id, check_out, check_in):
    query = """
    SELECT id
    FROM reservations
    WHERE room_id = %s
    AND check_in < %s
    AND check_out > %s
    AND status IN ('confirmed', 'checked_in')
    AND deleted_at IS NULL;
    """

    params = (room_id, check_out, check_in)

    result = execute_query(query, params, fetch=True)
    return result

def get_conflicting_reservations_excluding_id(room_id, id, check_out, check_in):
    query = """
    SELECT id
    FROM reservations
    WHERE room_id = %s
    AND id != %s
    AND check_in < %s
    AND check_out > %s
    AND status IN ('confirmed', 'checked_in')
    AND deleted_at IS NULL;
    """

    params = (room_id, id, check_out, check_in)

    result = execute_query(query, params, fetch=True)
    return result

def create_reservation(customer_id, room_id, check_in, check_out, total_amount):
    query = """
    INSERT INTO reservations(customer_id, room_id, check_in, check_out, total_amount)
    VALUES(%s, %s, %s, %s, %s)
    RETURNING id;
    """

    params = (customer_id, room_id, check_in, check_out, total_amount)

    result = execute_query(query, params, fetch=True)
    return result[0][0]

def update_reservation_dates(id, check_in, check_out, total_amount):
    query = """
    UPDATE reservations
    SET check_in = %s, check_out = %s, total_amount = %s, updated_at = NOW()
    WHERE id = %s AND deleted_at IS NULL
    RETURNING id;
    """

    params = (check_in, check_out, total_amount, id)

    result = execute_query(query, params, fetch=True)
    return result[0][0]

def update_reservation_status(id, status):
    query = """
    UPDATE reservations
    SET status = %s, updated_at = NOW()
    WHERE id = %s AND deleted_at IS NULL
    RETURNING id;
    """

    params = (status, id)

    result = execute_query(query, params, fetch=True)
    return result[0][0]

def soft_delete_reservation(id):
    query = """
    UPDATE reservations
    SET deleted_at = NOW()
    WHERE id = %s AND deleted_at IS NULL
    RETURNING id;
    """

    params = (id,)

    result = execute_query(query, params, fetch=True)
    return result[0][0]