class InsufficientHistoricalDataError(Exception):
    """Raised when a city/date combination has no historical readings at all."""


class UnsupportedLocationError(Exception):
    """Raised when a requested location doesn't match any known city."""
