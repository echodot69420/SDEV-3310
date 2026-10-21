from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_member_service
from app.exceptions import LibraryError
from app.routers.http_errors import http_error
from app.schemas.books import BookResponse
from app.schemas.members import MemberCreate, MemberResponse, MemberUpdate
from app.services.members.base import MemberService

router = APIRouter(prefix="/api/members", tags=["members"])


@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a member",
    responses={409: {"description": "Email or membership ID already exists"}},
)
def create_member(member: MemberCreate, service: MemberService = Depends(get_member_service)):
    try:
        data = member.model_dump()
        data["email"] = str(data["email"]).lower()
        return service.create(data)
    except LibraryError as exc:
        raise http_error(exc) from exc


@router.get("", response_model=list[MemberResponse], summary="List members")
def list_members(service: MemberService = Depends(get_member_service)):
    return service.list()


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Get a member",
    responses={404: {"description": "Member not found"}},
)
def get_member(member_id: int, service: MemberService = Depends(get_member_service)):
    try:
        return service.get(member_id)
    except LibraryError as exc:
        raise http_error(exc) from exc


@router.get(
    "/{member_id}/books",
    response_model=list[BookResponse],
    summary="List a member's books",
    responses={404: {"description": "Member not found"}},
)
def list_member_books(member_id: int, service: MemberService = Depends(get_member_service)):
    try:
        return service.books(member_id)
    except LibraryError as exc:
        raise http_error(exc) from exc


@router.patch(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Update a member",
    responses={
        404: {"description": "Member not found"},
        409: {"description": "Email or membership ID already exists"},
    },
)
def update_member(member_id: int, changes: MemberUpdate, service: MemberService = Depends(get_member_service)):
    try:
        updates = changes.model_dump(exclude_unset=True)
        if "email" in updates:
            updates["email"] = str(updates["email"]).lower()
        return service.update(member_id, updates)
    except LibraryError as exc:
        raise http_error(exc) from exc


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a member",
    responses={
        404: {"description": "Member not found"},
        409: {"description": "Member has associated books"},
    },
)
def delete_member(member_id: int, service: MemberService = Depends(get_member_service)) -> Response:
    try:
        service.delete(member_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LibraryError as exc:
        raise http_error(exc) from exc
