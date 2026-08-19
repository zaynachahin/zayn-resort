from app.database import execute_query

def list_room_categories():
    query = """
    SELECT id, name, capacity, daily_rate
    FROM room_categories
    WHERE deleted_at IS NULL;
    """

    room_categories = execute_query(query, fetch=True)
    return room_categories

def get_room_category_by_id(id):
    query = """
    SELECT id, name, capacity, daily_rate
    FROM room_categories
    WHERE id = %s AND deleted_at IS NULL;
    """

    params = (id,)

    room_category = execute_query(query, params, fetch=True)
    return room_category

def get_room_category_by_name(name):
    query = """
    SELECT id
    FROM room_categories
    WHERE name = %s AND deleted_at IS NULL;
    """

    params = (name,)

    room_category = execute_query(query, params, fetch=True)
    return room_category

def get_room_category_by_name_excluding_id(name, id):
    query = """
    SELECT id
    FROM room_categories
    WHERE name = %s
    AND id != %s
    AND deleted_at IS NULL;
    """

    params = (name,id)

    room_category = execute_query(query, params, fetch=True)
    return room_category

def create_room_category(name, capacity, daily_rate):
    query = """
    INSERT INTO room_categories(
    name,
    capacity,
    daily_rate
    )
    VALUES(
    %s,
    %s,
    %s
    )
    RETURNING id;
    """

    params = (
        name,
        capacity,
        daily_rate
    )

    result = execute_query(query, params, fetch=True)
    return result[0][0]

def update_room_category(id, name, capacity, daily_rate):
    query = """
    UPDATE room_categories
    SET 
    name = %s,
    capacity = %s,
    daily_rate = %s,
    updated_at = NOW()
    WHERE id = %s
    RETURNING id;
    """

    params = (
        name,
        capacity,
        daily_rate,
        id
    )

    result = execute_query(query, params, fetch=True)
    return result

def soft_delete_room_category(id):
    query = """
    UPDATE room_categories
    SET deleted_at = NOW()
    WHERE id = %s AND deleted_at IS NULL
    RETURNING id;
    """

    params = (id,)

    result = execute_query(query, params, fetch=True)
    return result

allowed_room_category_columns = {"name", "capacity", "daily_rate"}

def patch_room_category(id,fields: dict):
    set_clauses = []
    params = []

    for column, value in fields.items():
        if column in allowed_room_category_columns:
            set_clauses.append(f"{column} = %s")
            params.append(value)

    set_clause = ", ".join(set_clauses)

    query = f"""
    UPDATE room_categories
    SET {set_clause}, updated_at = NOW()
    WHERE id = %s
    RETURNING id;
    """

    params.append(id)

    result = execute_query(query, params, fetch=True)
    return result