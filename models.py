"""
Data Models for the HR ChatBot System.
Defines the structure of core entities like Users, Departments, and Leaves.
"""

from typing import Optional, Dict, Any
from datetime import date
from utils.logger import logger

logger.info("[.] models.py: Initializing domain models")

class Department:
    """Represents a company department."""
    def __init__(self, dep_id: int, name: str, manager_id: Optional[int] = None):
        self.dep_id = dep_id
        self.name = name
        self.manager_id = manager_id  # Stores the manager's employee ID

class User:
    """Represents an employee/user within the system."""
    def __init__(
        self, 
        emp_id: int, 
        full_name: str, 
        email: str, 
        role: str, 
        job_title: str, 
        salary_basic: float
    ):
        self.emp_id = emp_id
        self.full_name = full_name
        self.email = email
        self.role = role
        self.job_title = job_title
        self.salary_basic = salary_basic

    def to_dict(self) -> Dict[str, Any]:
        """Converts user object to dictionary for API or Logging purposes."""
        return {
            "emp_id": self.emp_id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "job_title": self.job_title,
            "salary_basic": self.salary_basic
        }

class LeaveType:
    """Defines types of leaves (e.g., Annual, Sick)."""
    def __init__(self, name: str, total_days: int, is_paid: bool = True):
        self.name = name
        self.total_days = total_days
        self.is_paid = is_paid

class LeaveBalance:
    """Tracks used and remaining leave days for an employee."""
    def __init__(self, leave_type: str, total_days: int, used_days: int):
        self.leave_type = leave_type
        self.total_days = total_days
        self.used_days = used_days

    @property
    def remaining_days(self) -> int:
        """Calculates the available balance."""
        return self.total_days - self.used_days

    def use_days(self, days: int):
        """Updates the used days after validation."""
        if days > self.remaining_days:
            # We use a custom exception logic here if needed
            raise ValueError(f"Insufficient balance. Available: {self.remaining_days}")
        self.used_days += days

class LeaveRequest:
    """Represents an employee's application for leave."""
    def __init__(self, user: User, leave_type: str, start_date: date, end_date: date):
        self.user = user
        self.leave_type = leave_type
        self.start_date = start_date
        self.end_date = end_date
        self.status = "pending"

    def duration_days(self) -> int:
        """Calculates the total number of days for the request."""
        try:
            return (self.end_date - self.start_date).days + 1
        except Exception as e:
            logger.error(f"Error calculating duration: {e}")
            return 0

    def approve(self, balance: LeaveBalance):
        """Processes approval and updates the employee balance."""
        try:
            if self.status != "pending":
                raise ValueError("Request has already been processed.")

            requested_days = self.duration_days()
            balance.use_days(requested_days)
            self.status = "approved"
            logger.info(f"Leave approved for {self.user.full_name}: {requested_days} days.")
            
        except ValueError as ve:
            logger.warning(f"Approval failed: {ve}")
            raise ve
        except Exception as e:
            logger.error(f"Unexpected error during leave approval: {e}")
            raise

    def reject(self):
        """Sets request status to rejected."""
        self.status = "rejected"



logger.info("[.] models.py: Module loaded successfully")

