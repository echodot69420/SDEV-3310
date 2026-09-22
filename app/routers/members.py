from fastapi import APIRouter, HTTPException, Response, status

from app.models.schemas import BookResponse, MemberCreate, MemberResponse, MemberUpdate
from app.services import storage

router = APIRouter(prefix="/api/members", tags=["members"])


def duplicate_member_field(field: str, value: object, excluding_id: int | None = None) -> bool:
    return any(
        member[field] == value and member_id != excluding_id
        for member_id, member in storage.members.items()
    )


@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a member",
)
def create_member(member: MemberCreate) -> dict:
    data = member.model_dump()
    data["email"] = str(data["email"]).lower()
    for field in ("email", "membership_id"):
        if duplicate_member_field(field, data[field]):
            raise HTTPException(status_code=409, detail=f"{field} already exists")
    return storage.create_member(data)


@router.get("", response_model=list[MemberResponse], summary="List members")
def list_members() -> list[dict]:
    return list(storage.members.values())


@router.get("/{member_id}", response_model=MemberResponse, summary="Get a member")
def get_member(member_id: int) -> dict:
    member = storage.members.get(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.get(
    "/{member_id}/books",
    response_model=list[BookResponse],
    summary="List a member's books",
)
def list_member_books(member_id: int) -> list[dict]:
    if member_id not in storage.members:
        raise HTTPException(status_code=404, detail="Member not found")
    return [book for book in storage.books.values() if book["member_id"] == member_id]


@router.patch("/{member_id}", response_model=MemberResponse, summary="Update a member")
def update_member(member_id: int, changes: MemberUpdate) -> dict:
    member = storage.members.get(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    updates = changes.model_dump(exclude_unset=True)
    if "email" in updates:
        updates["email"] = str(updates["email"]).lower()
    for field in ("email", "membership_id"):
        if field in updates and duplicate_member_field(field, updates[field], member_id):
            raise HTTPException(status_code=409, detail=f"{field} already exists")

    member.update(updates)
    return member


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a member",
)
def delete_member(member_id: int) -> Response:
    if member_id not in storage.members:
        raise HTTPException(status_code=404, detail="Member not found")
    if any(book["member_id"] == member_id for book in storage.books.values()):
        raise HTTPException(status_code=409, detail="Member has associated books")
    del storage.members[member_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
