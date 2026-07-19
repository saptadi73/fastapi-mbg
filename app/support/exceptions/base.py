class AppException(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
        errors: list[dict[str, str]] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.errors = errors or []


class NotFoundException(AppException):
    def __init__(self, *, code: str, message: str) -> None:
        super().__init__(code=code, message=message, status_code=404)


class ConflictException(AppException):
    def __init__(self, *, code: str, message: str) -> None:
        super().__init__(code=code, message=message, status_code=409)


class BadRequestException(AppException):
    def __init__(self, *, code: str, message: str) -> None:
        super().__init__(code=code, message=message, status_code=400)


class ForbiddenException(AppException):
    def __init__(self, *, code: str, message: str) -> None:
        super().__init__(code=code, message=message, status_code=403)


class UnauthorizedException(AppException):
    def __init__(self, *, code: str, message: str) -> None:
        super().__init__(code=code, message=message, status_code=401)


class ServiceUnavailableException(AppException):
    def __init__(self, *, code: str, message: str) -> None:
        super().__init__(code=code, message=message, status_code=503)
