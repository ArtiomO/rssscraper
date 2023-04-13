class FeedAlreadyRegisteredByUser(Exception):
    """Field already registered by user."""

    message = "Feed already registered by current user."


class ItemAlreadyMarkedAsRead(Exception):
    """Item already marked as read exception."""

    message = "Item already marked as read."
