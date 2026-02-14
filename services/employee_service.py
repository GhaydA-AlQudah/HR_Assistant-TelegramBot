from utils.logger import logger
from database import Database
from models import User
from expectations import EmployeeNotFound

logger.info("[+] employee_service.py started")

class EmployeeService:
    """
    Service class responsible for handling employee-related data operations.
    """

    def __init__(self):
        """Initializes the database connection."""
        try:
            self.db = Database()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def get_employee_by_id(self, emp_id: int) -> User:
        """
        Retrieves a single employee's details from the database by their ID.

        Args:
            emp_id (int): The unique employee ID.

        Returns:
            User: An instance of the User model populated with employee data.

        Raises:
            EmployeeNotFound: If no user is found with the provided emp_id.
            Exception: If a database execution error occurs.
        """
        query = """
            SELECT emp_id, full_name, email, role, job_title, salary_basic
            FROM users
            WHERE emp_id = %s
        """
        
        try:
            # Execute the query with provided parameters
            result = self.db.execute(query, (emp_id,), fetch=True)

            # Check if any result was returned
            if not result:
                logger.warning(f"Employee with ID {emp_id} not found.")
                raise EmployeeNotFound(emp_id)

            # Extract the first row from the result list
            employee_data = result[0]
            
            # Log successful retrieval for debugging purposes
            logger.debug(f"Successfully retrieved employee: {employee_data}")

            # Return a User object using the unpacked row data
            return User(*employee_data)

        except EmployeeNotFound:
            # Re-raise the custom exception after logging
            raise
        except Exception as e:
            # Catch database or unexpected errors and log them
            logger.error(f"Error retrieving employee {emp_id}: {str(e)}")
            raise Exception(f"Database operation failed: {e}")

logger.info("[@] employee_service.py Stopped")


