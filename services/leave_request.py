from typing import Optional, Union
from utils.logger import logger
from database import Database

logger.info("[+] leave_request_service.py started")

class LeaveRequestService:
    """
    Service class to manage leave request operations within the database.
    """

    def __init__(self):
        """Initializes the service with a database connection."""
        try:
            self.db = Database()
        except Exception as e:
            logger.error(f"Database connection failed in LeaveRequestService: {e}")
            raise

    def create_leave_request(
        self, 
        emp_id: int, 
        leave_type_id: int, 
        start_date: str, 
        end_date: str
    ) -> str:
        """
        Submits a new leave request to the database with a default 'pending' status.

        Args:
            emp_id (int): Unique identifier of the employee.
            leave_type_id (int): Category ID of the leave (e.g., Annual, Sick).
            start_date (str): Request start date in 'YYYY-MM-DD' format.
            end_date (str): Request end date in 'YYYY-MM-DD' format.

        Returns:
            str: A localized success message with the Request ID or an error message.
        """
        
        # Structured SQL query for readability and maintenance
        query = """
            INSERT INTO leaves (emp_id, leave_type_id, start_date, end_date, status)
            VALUES (%s, %s, %s, %s, 'pending')
            RETURNING leave_id;
        """
        
        params = (emp_id, leave_type_id, start_date, end_date)

        try:
            # Execute the query, commit changes, and fetch the generated leave_id
            result = self.db.execute(
                query, 
                params, 
                commit=True, 
                fetch=True
            )

            if result and len(result) > 0:
                leave_id = result[0][0]
                logger.info(f"Leave request created successfully: ID {leave_id}")
                return (
                    f"✅ <b>Leave Request Submitted | تم تقديم طلب الإجازة بنجاح</b>\n"
                    f"────────────────────────────\n"
                    f"🔸 <b>Request ID :</b> <code>{leave_id}</code>\n"
                    f"🔸 <b>Status     :</b> <code>Pending Approval | قيد الانتظار</code>\n"
                    f"────────────────────────────\n"
                    f"ℹ️ <i>You will be notified once reviewed.</i>\n"
                    f"<i>سيتم إشعارك فور مراجعة الطلب.</i>"
                )            
            # Case where execution succeeds but no ID is returned
            logger.warning(f"Leave insertion executed but failed to return an ID for Employee {emp_id}")
            return f"Leave insertion executed but failed to return an ID for Employee {emp_id}"

        except Exception as e:
            # Catch all database exceptions and log with context
            logger.error(f"Critical error creating leave request for Employee {emp_id}: {str(e)}")
            return "حدث خطأ فني أثناء معالجة طلبك، يرجى المحاولة مرة أخرى لاحقاً."

logger.info("[@] leave_request_service.py Stopped")



