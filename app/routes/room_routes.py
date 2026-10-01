from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from app.schemas.rooms_schema import RoomCreate, RoomUpdate, RoomPatch, RoomCreateResponse, RoomUpdateResponse
from app.repositories import room_repository
from app.repositories.room_category_repository import get_room_category_by_id


router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("", status_code=status.HTTP_200_OK, summary=" ")
def list_rooms():
    rooms = room_repository.list_rooms()
    response = []
    for room in rooms:
        response.append({
            "room_id": room["id"],
            "number": room["number"],
            "name": room["name"],
            "description": room["description"],
            "room_category_id": room["room_category_id"]
        })
    return response


@router.get("/{id}", status_code=status.HTTP_200_OK, summary=" ")
def get_room(id: UUID):
    room = room_repository.get_room_by_id(id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return {
        "room_id": room["id"],
        "number": room["number"],
        "name": room["name"],
        "description": room["description"],
        "room_category_id": room["room_category_id"]
    }


@router.post("", status_code=status.HTTP_201_CREATED, response_model=RoomCreateResponse, summary=" ")
def create_room(payload: RoomCreate):
    category = get_room_category_by_id(payload.room_category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room category not found")

    existing = room_repository.get_room_by_number(payload.number)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room number already exists")

    result = room_repository.create_room(
        number=payload.number,
        name=payload.name,
        description=payload.description,
        room_category_id=payload.room_category_id
    )
    return result


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=RoomUpdateResponse, summary=" ")
def update_room(id: UUID, payload: RoomUpdate):
    room = room_repository.get_room_by_id(id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    category = get_room_category_by_id(payload.room_category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room category not found")

    existing = room_repository.get_room_by_number_excluding_id(payload.number, id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room number already exists")

    result = room_repository.update_room(
        id=id,
        number=payload.number,
        name=payload.name,
        description=payload.description,
        room_category_id=payload.room_category_id
    )
    return result


@router.patch("/{id}", status_code=status.HTTP_200_OK, response_model=RoomUpdateResponse, summary=" ")
def patch_room(id: UUID, payload: RoomPatch):
    room = room_repository.get_room_by_id(id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    fields = payload.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided")

    if "room_category_id" in fields:
        category = get_room_category_by_id(fields["room_category_id"])
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room category not found")

    if "number" in fields:
        existing = room_repository.get_room_by_number_excluding_id(fields["number"], id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room number already exists")

    result = room_repository.patch_room(id=id, fields=fields)
    return result


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary=" ")
def soft_delete_room_endpoint(id: UUID):
    existing_room = room_repository.get_room_by_id_including_deleted(id)
    if not existing_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    room = room_repository.soft_delete_room(id)
    if not room:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room is already deleted")