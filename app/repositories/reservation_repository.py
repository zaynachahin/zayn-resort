from app.database import execute_query

def get_reservation_by_id(id):
    query= """
    SELECT id, customer_id, room_id, check_in, check_out, status, total_amount
    FROM reservations
    WHERE id = %s AND deleted_at IS NULL;
    """

    params= (id,)

    result = execute_query(query, params, fetch_one=True)
    return result

def get_reservation_by_id_including_deleted(id):
    query= """
    SELECT id, customer_id, room_id, check_in, check_out, status, total_amount
    FROM reservations
    WHERE id = %s;
    """

    params= (id,)

    result = execute_query(query, params, fetch_one=True)
    return result

def list_reservations():
    query = """
    SELECT id, customer_id, room_id, check_in, check_out, status, total_amount
    FROM reservations 
    WHERE deleted_at IS NULL;
    """

    result = execute_query(query, fetch_all=True)
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

    result = execute_query(query, params, fetch_all=True)
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

    result = execute_query(query, params, fetch_all=True)
    return result

def create_reservation(customer_id, room_id, check_in, check_out, total_amount):
    query = """
    INSERT INTO reservations(customer_id, room_id, check_in, check_out, total_amount)
    VALUES(%s, %s, %s, %s, %s)
    RETURNING id, customer_id, room_id, check_in, check_out, status, total_amount, created_at;
    """

    params = (customer_id, room_id, check_in, check_out, total_amount)

    result = execute_query(query, params, fetch_one=True)
    return result

def update_reservation_dates(id, check_in, check_out, total_amount):
    query = """
    UPDATE reservations
    SET check_in = %s, check_out = %s, total_amount = %s, updated_at = NOW()
    WHERE id = %s AND deleted_at IS NULL
    RETURNING id, customer_id, room_id, check_in, check_out, status, total_amount, updated_at;
    """

    params = (check_in, check_out, total_amount, id)

    result = execute_query(query, params, fetch_one=True)
    return result

def update_reservation_status(id, status):
    query = """
    UPDATE reservations
    SET status = %s, updated_at = NOW()
    WHERE id = %s AND deleted_at IS NULL
    RETURNING id, customer_id, room_id, check_in, check_out, status, total_amount, updated_at;
    """

    params = (status, id)

    result = execute_query(query, params, fetch_one=True)
    return result

def soft_delete_reservation(id):
    query = """
    UPDATE reservations
    SET deleted_at = NOW()
    WHERE id = %s AND deleted_at IS NULL
    RETURNING id, deleted_at;
    """

    params = (id,)

    result = execute_query(query, params, fetch_one=True)
    return result