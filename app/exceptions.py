class LibraryError(Exception):
    pass


class NotFoundError(LibraryError):
    pass


class DuplicateError(LibraryError):
    pass


class MemberHasBooksError(LibraryError):
    pass

