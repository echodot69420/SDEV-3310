from fastapi import APIRouter, HTTPException, Response, status

from app.models.schemas import BookCreate, BookResponse, BookUpdate
from app.services import storage

router = APIRouter(prefix="/api/books", tags=["books"])


def find_duplicate_isbn(isbn: str, excluding_id: int | None = None) -> bool:
    return any(
        book["isbn"] == isbn and book_id != excluding_id
        for book_id, book in storage.books.items()
    )


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a book",
)
def create_book(book: BookCreate) -> dict:
    if book.member_id not in storage.members:
        raise HTTPException(status_code=404, detail="Member not found")
    if find_duplicate_isbn(book.isbn):
        raise HTTPException(status_code=409, detail="ISBN already exists")
    return storage.create_book(book.model_dump())


@router.get("", response_model=list[BookResponse], summary="List books")
def list_books() -> list[dict]:
    return list(storage.books.values())


@router.get("/{book_id}", response_model=BookResponse, summary="Get a book")
def get_book(book_id: int) -> dict:
    book = storage.books.get(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.patch("/{book_id}", response_model=BookResponse, summary="Update a book")
def update_book(book_id: int, changes: BookUpdate) -> dict:
    book = storage.books.get(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    updates = changes.model_dump(exclude_unset=True)
    if "member_id" in updates and updates["member_id"] not in storage.members:
        raise HTTPException(status_code=404, detail="Member not found")
    if "isbn" in updates and find_duplicate_isbn(updates["isbn"], book_id):
        raise HTTPException(status_code=409, detail="ISBN already exists")

    book.update(updates)
    return book


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a book",
)
def delete_book(book_id: int) -> Response:
    if storage.books.pop(book_id, None) is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
