from typing import Any

members: dict[int, dict[str, Any]] = {}
books: dict[int, dict[str, Any]] = {}
_next_member_id = 1
_next_book_id = 1


def create_member(data: dict[str, Any]) -> dict[str, Any]:
    global _next_member_id
    member = {"id": _next_member_id, **data}
    members[_next_member_id] = member
    _next_member_id += 1
    return member


def create_book(data: dict[str, Any]) -> dict[str, Any]:
    global _next_book_id
    book = {"id": _next_book_id, **data}
    books[_next_book_id] = book
    _next_book_id += 1
    return book


def reset_storage() -> None:
    global _next_member_id, _next_book_id
    members.clear()
    books.clear()
    _next_member_id = 1
    _next_book_id = 1
