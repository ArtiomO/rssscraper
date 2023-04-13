class FieldError(Exception):
    """Invalid field exception."""

    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
