class AppError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ValidationError(AppError):
    def __init__(self, message="Invalid input"):
        super().__init__(message, 400)

class AuthenticationError(AppError):
    def __init__(self, message="Authentication failed"):
        super().__init__(message, 401)  

class AuthorizationError(AppError):
    def __init__(self, message="Forbidden access"):
        super().__init__(message, 403)

class NotFoundError(AppError):
    def __init__(self, message="Resource not found"):
        super().__init__(message, 404)



       