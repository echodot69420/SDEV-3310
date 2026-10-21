from fastapi import Request
from app.services.books.base import BookService
from app.services.members.base import MemberService


def get_member_service(request: Request) -> MemberService:
    return request.app.state.member_service


def get_book_service(request: Request) -> BookService:
    return request.app.state.book_service
