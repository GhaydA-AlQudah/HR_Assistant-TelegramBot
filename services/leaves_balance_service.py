from typing import List, Dict, Any
from utils.logger import logger
from database import Database

logger.info("[+] leave_service.py started")

class LeaveService:
    """
    Service class to handle leave balance calculations and leave history retrieval.
    """

    def __init__(self):
        """Initializes the database connection for leave operations."""
        try:
            self.db = Database()
        except Exception as e:
            logger.error(f"Failed to connect to database in LeaveService: {e}")
            raise

    def get_leave_balance(self, emp_id: int) -> List[Dict[str, Any]]:
        """
        Calculates leave balances (total, used, and remaining) for an employee.
        
        It aggregates all 'approved' leave records and subtracts them from 
        the default total days defined for each leave type.

        Args:
            emp_id (int): The unique identifier of the employee.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing leave type metrics.
                                  Returns an empty list if no data is found or on error.
        """
        
        # SQL query using COALESCE to handle NULL values for employees with no leave records.
        # It calculates days by: (end_date - start_date + 1).
        query = """
            SELECT 
                lt.name AS leave_type,
                lt.default_total_days AS total,
                COALESCE(SUM(l.end_date - l.start_date + 1), 0) AS used,
                (lt.default_total_days - COALESCE(SUM(l.end_date - l.start_date + 1), 0)) AS remaining
            FROM leave_types lt
            LEFT JOIN leaves l ON lt.leave_types_id = l.leave_type_id 
                AND l.emp_id = %s 
                AND l.status = 'approved'
            GROUP BY lt.leave_types_id, lt.name, lt.default_total_days
            ORDER BY lt.leave_types_id;
        """
        
        try:
            # Execute the query and fetch results
            result = self.db.execute(query, (emp_id,), fetch=True)

            if not result:
                logger.warning(f"No leave configurations found in the system for emp_id: {emp_id}")
                return []

            # Transforming raw SQL rows into a structured list of dictionaries
            balances = [
                {
                    "leave_type": row[0],
                    "total": row[1],
                    "used": int(row[2]),      # Ensure numeric values are integers
                    "remaining": int(row[3])
                }
                for row in result
            ]
            
            logger.info(f"Successfully calculated leave balance for emp_id: {emp_id}")
            return balances

        except Exception as e:
            # Log the full error context for debugging
            logger.error(f"Database error while calculating leave balance for emp_id {emp_id}: {str(e)}")
            # Return an empty list to prevent the calling agent from crashing
            return []

logger.info("[@] leave_service.py Stopped")



