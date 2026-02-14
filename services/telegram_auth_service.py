from typing import Optional, Dict, Any
from utils.logger import logger
from database import Database

logger.info("[+] telegram_auth_service.py started")

class TelegramAuthService:
    """
    Service responsible for authenticating users via their Telegram Bot ID.
    Maps Telegram IDs to internal Employee records.
    """

    def __init__(self):
        """Initializes the database connection for authentication tasks."""
        try:
            self.db = Database()
            logger.info("[+] TelegramAuthService initialized successfully")
        except Exception as e:
            logger.error(f"[-] Database Initialization Error in AuthService: {e}")
            # Re-raising ensures the application doesn't run with a broken auth service
            raise

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves internal employee data associated with a specific Telegram ID.

        Args:
            telegram_id (int): The unique ID provided by the Telegram API.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing user details if found, 
                                     otherwise returns None.
        """
        query = """
            SELECT emp_id, full_name, email, role, job_title, dep_id
            FROM users
            WHERE telegram_bot_id = %s
        """
        
        try:
            # Execute the query to find a matching telegram_bot_id
            result = self.db.execute(query, (telegram_id,), fetch=True)

            # Check if any user record was returned
            if result and len(result) > 0:
                row = result[0]
                
                # Log successful authentication for tracking
                logger.debug(f"Authentication successful for Telegram ID: {telegram_id}")

                # Construct a structured dictionary for higher-level services
                return {
                    "Authenticated": True,
                    "emp_id": row[0],
                    "full_name": row[1],
                    "email": row[2],
                    "role": row[3],
                    "job_title": row[4],
                    "dep_id": row[5]
                }
            
            # Log non-authenticated attempts if necessary
            logger.warning(f"Unauthorized access attempt or user not found: {telegram_id}")
            return None

        except Exception as e:
            # Catching and logging database exceptions to avoid bot crashing
            logger.error(f"Critical Database Query Error in AuthService: {e}")
            return None

logger.info("[+] telegram_auth_service.py stopped")
