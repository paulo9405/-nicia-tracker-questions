class DomainException(Exception):
    """Exceção base do domínio Nícia Track."""


class ValidationError(DomainException):
    pass


class NotFoundError(DomainException):
    pass
