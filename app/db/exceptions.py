class AlreadyExistsError(Exception):
    """Row already exists exception."""

    def __init__(self, table_name: str, detail: str):
        self.table_name = table_name
        self.detail = detail


class NotFoundError(Exception):
    """Row not found exception."""

    message = "Not found."
