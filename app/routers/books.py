from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_book_service
from app.exceptions import LibraryError
from app.routers.http_errors import http_error
from app.schemas.books import BookCreate, BookResponse, BookUpdate
from app.services.books.base import BookService

router = APIRouter(prefix="/api/books", tags=["books"])


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a book",
    responses={404: {"description": "Member not found"}, 409: {"description": "ISBN already exists"}},
)
def create_book(book: BookCreate, service: BookService = Depends(get_book_service)):
    try:
        return service.create(book.model_dump())
    except LibraryError as exc:
        raise http_error(exc) from exc


@router.get("", response_model=list[BookResponse], summary="List books")
def list_books(service: BookService = Depends(get_book_service)):
    return service.list()


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="Get a book",
    responses={404: {"description": "Book not found"}},
)
def get_book(book_id: int, service: BookService = Depends(get_book_service)):
    try:
        return service.get(book_id)
    except LibraryError as exc:
        raise http_error(exc) from exc


@router.patch(
    "/{book_id}",
    response_model=BookResponse,
    summary="Update a book",
    responses={
        404: {"description": "Book or Member not found"},
        409: {"description": "ISBN already exists"},
    },
)
def update_book(book_id: int, changes: BookUpdate, service: BookService = Depends(get_book_service)):
    try:
        return service.update(book_id, changes.model_dump(exclude_unset=True))
    except LibraryError as exc:
        raise http_error(exc) from exc


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a book",
    responses={404: {"description": "Book not found"}},
)
def delete_book(book_id: int, service: BookService = Depends(get_book_service)) -> Response:
    try:
        service.delete(book_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LibraryError as exc:
        raise http_error(exc) from exc
