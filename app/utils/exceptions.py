from fastapi import HTTPException
 
 
class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(
            status_code=status_code,
            detail=detail
        )
 
 
class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(400, detail)
 
 
class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(401, detail)
 
 
class ForbiddenException(AppException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(403, detail)
 
 
class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(404, detail)
 
 
class ConflictException(AppException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(409, detail)
 
 
class InternalServerException(AppException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(500, detail)
 