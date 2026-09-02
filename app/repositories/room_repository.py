from app.database import execute_query
from app.repositories.room_category_repository import get_room_category_by_id

allowed_room_columns = {"name", "description", "number", "room_category_id"}

def get_room_by_id(id):
    query = """
        SELECT id, number, name, description, room_category_id
        FROM rooms
        WHERE id = %s AND deleted_at IS NULL;
        """
    params = (id,)
    result = execute_query(query, params, fetch=True)
    return result

def get_room_by_id_including_deleted(id):
    query = """
    SELECT id, number, name, description, room_category_id
    FROM rooms
    WHERE id = %s;
    """
    params = (id,)
    result = execute_query(query, params, fetch=True)
    return result

def get_room_by_number(number):
    query = """
    SELECT id, number, name, description, room_category_id
    FROM rooms
    WHERE number = %s AND deleted_at IS NULL
    """
    params = (number,)
    result = execute_query(query, params, fetch=True)
    return result

def get_room_by_number_excluding_id(number, id):
    query = """
    SELECT id, number, name, description, room_category_id
    FROM rooms
    WHERE number = %s AND id != %s AND deleted_at IS NULL
    """
    params = (number, id)
    result = execute_query(query, params, fetch=True)
    return result

def list_rooms():
    query = """
    SELECT id, number, name, description, room_category_id
    FROM rooms
    WHERE deleted_at IS NULL
    """
    result = execute_query(query, fetch=True)
    return result

def create_room(number, name, description, room_category_id):
    query = """
    INSERT INTO rooms (number, name, description, room_category_id)
    VALUES (%s, %s, %s, %s)
    RETURNING id
    """
    params = (number, name, description, room_category_id)
    result = execute_query(query, params, fetch=True)
    return result[0][0]

def update_room(id, number, name, description, room_category_id):
    query = """
    UPDATE rooms
    SET number = %s, name = %s, description = %s, room_category_id = %s, updated_at = NOW()
    WHERE id = %s AND deleted_at IS NULL
    RETURNING id
    """
    params = (number, name, description, room_category_id, id)
    result = execute_query(query, params, fetch=True)
    return result

def patch_room(id, fields: dict):
    set_clauses = []
    params = []

    for column, value in fields.items():
        if column in allowed_room_columns:
            set_clauses.append(f"{column} = %s")
            params.append(value)

    set_clause = ", ".join(set_clauses)

    query = f"""
    UPDATE rooms
    SET {set_clause}, updated_at = NOW()
    WHERE id = %s AND deleted_at IS NULL
    RETURNING id
    """
    params.append(id)

    result = execute_query(query, params, fetch=True)
    return result

def soft_delete_room(id):
    query = """
    UPDATE rooms
    SET deleted_at = NOW()
    WHERE id = %s AND deleted_at IS NULL
    RETURNING id
    """
    params = (id,)
    result = execute_query(query, params, fetch=True)
    return result