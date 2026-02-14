"""
Custom Exceptions for the HR ChatBot System.
These classes help identify specific business logic failures.
"""

class HRBotException(Exception):
    """Base class for all exceptions in this project."""
    pass

class EmployeeNotFound(HRBotException):
    """Raised when a requested employee ID or name does not exist in the database."""
    pass

class UnauthorizedAccess(HRBotException):
    """Raised when a user (e.g., manager or employee) tries to access unauthorized data."""
    pass

class DatabaseConnectionError(HRBotException):
    """Raised when the system fails to connect to PostgreSQL."""
    pass

class OnboardingError(HRBotException):
    """Raised when there is a failure in the onboarding process (e.g., duplicate email)."""
    pass

class LeaveRequestError(HRBotException):
    """Raised when a leave request cannot be processed (e.g., insufficient balance)."""
    pass

class MissingDataError(HRBotException):
    """Raised when the AI Agent or user fails to provide required fields for a tool."""
    pass