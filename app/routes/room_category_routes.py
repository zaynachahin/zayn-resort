from fastapi import APIRouter, HTTPException, status
from app.repositories.room_category_repository import(
    list_room_categories,
    get_room_category_by_id,
    get_room_category_by_name,
    get_room_category_by_name_excluding_id,
    get_room_category_by_id_including_deleted,
    create_room_category,
    update_room_category,
    soft_delete_room_category,
    patch_room_category
)
from app.schemas.room_category_schema import (
    RoomCategoryCreate,
    RoomCategoryUpdate,
    RoomCategoryPatch,
    RoomCategoryCreateResponse,
    RoomCategoryUpdateResponse
)
from uuid import UUID

router = APIRouter(
    prefix="/room-categories",
    tags = ["Room Categories"],
)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=RoomCategoryCreateResponse, summary=" ")
def create_room_category_endpoint(room_category:RoomCategoryCreate):
    existing_room_category = get_room_category_by_name(room_category.name)
    
    if existing_room_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail= "Room Category already exists"
        )

    result = create_room_category(
        room_category.name,
        room_category.capacity,
        room_category.daily_rate
    )

    return result


@router.get("", status_code=status.HTTP_200_OK, summary=" ")
def list_room_categories_endpoint():
    room_categories = list_room_categories()

    response = []

    for room_category in room_categories:
        response.append(
            {
                "room_category_id": room_category["id"],
                "name": room_category["name"],
                "capacity": room_category["capacity"],
                "daily_rate": room_category["daily_rate"]
            }
        )

    return response

@router.get("/{id}", status_code=status.HTTP_200_OK, summary=" ")
def get_room_category_endpoint(id:UUID):
    room_category = get_room_category_by_id(id)

    if not room_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room Category not found"
        )

    return {
        "room_category_id": room_category["id"],
        "name": room_category["name"],
        "capacity": room_category["capacity"],
        "daily_rate": room_category["daily_rate"]
    }

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=RoomCategoryUpdateResponse, summary=" ")
def update_room_category_endpoint(id:UUID, room_category:RoomCategoryUpdate):
    registered_room_category = get_room_category_by_id(id)

    if not registered_room_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room Category does not exist"
        )

    existing_room_category = get_room_category_by_name_excluding_id(room_category.name, id)

    if existing_room_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room Category exists"
        )

    result = update_room_category(
        id,
        room_category.name,
        room_category.capacity,
        room_category.daily_rate
    )

    return result

@router.patch("/{id}", status_code=status.HTTP_200_OK, response_model=RoomCategoryUpdateResponse, summary=" ")
def patch_room_category_endpoint(id:UUID, room_category: RoomCategoryPatch):
    registered_room_category = get_room_category_by_id(id)

    if not registered_room_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room Category does not exist"
        )

    fields = room_category.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No input provided"
        )

    if "name" in fields:
        existing_room_category = get_room_category_by_name_excluding_id(fields["name"], id)

        if existing_room_category:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room Category exists"
            )

    result = patch_room_category(id, fields)

    return result

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary=" ")
def soft_delete_room_category_endpoint(id:UUID):
    existing_room_category = get_room_category_by_id_including_deleted(id)

    if not existing_room_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room category not found"
        )
    room_category = soft_delete_room_category(id)
    if not room_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room category is already deleted"
        )