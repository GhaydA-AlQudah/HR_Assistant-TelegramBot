import psycopg2
from typing import Optional, Any, List, Union
from utils.logger import logger
from dotenv import load_dotenv 
import os 

# Load environment variables from .env file
load_dotenv() 

logger.info("[+] database.py: Initializing database module...")

class Database:
    """
    A utility class to manage PostgreSQL database connections and query executions.
    Implements robust transaction management with automated commits and rollbacks.
    """

    def __init__(self):
        """
        Initializes the database connection using credentials from environment variables.
        
        Raises:
            ConnectionError: If the connection to the PostgreSQL server fails.
        """
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                port=os.getenv("DB_PORT")
            )
            # Ensure transactions are handled manually per execute call
            self.conn.autocommit = False
            logger.info("[+] Database: Connection established successfully.")
        except Exception as e:
            logger.error(f"[-] Database: Critical Connection Error: {e}")
            raise ConnectionError(f"Could not connect to the database: {e}")

    def execute(
        self, 
        query: str, 
        params: Optional[Union[tuple, list]] = None, 
        fetch: bool = False,
        commit: bool = True
    ) -> Optional[List[Any]]:
        """
        Executes a SQL query safely using parameter binding.
        
        This method ensures that:
        1. Cursors are automatically closed using context managers.
        2. Data is committed BEFORE returning results (fixing the rollback issue).
        3. Transactions are rolled back if any error occurs to maintain integrity.

        Args:
            query (str): The SQL statement to execute.
            params (tuple/list, optional): Values to safely bind to the query.
            fetch (bool): If True, fetches and returns all result rows.
            commit (bool): If True, persists changes to the database.

        Returns:
            Optional[List[Any]]: A list of rows if fetch is True, else None.
        """
        result = None
        try:
            # Context manager handles cursor cleanup automatically
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                
                # Capture results if requested (e.g., for SELECT or RETURNING clauses)
                if fetch:
                    result = cur.fetchall()
                
                # Persist changes to DB. Important: Commit must happen before returning 
                # to prevent automatic rollback in non-autocommit mode.
                if commit:
                    self.conn.commit()
                
                logger.debug(f"Database: Query executed successfully: {query[:60]}...")
                return result

        except Exception as e:
            # Revert any pending changes if an error occurs to keep DB state clean
            if self.conn:
                self.conn.rollback()
            logger.error(f"[-] Database: Execution Error during query '{query[:60]}': {e}")
            raise e

    def close(self):
        """
        Gracefully closes the database connection.
        Should be called when the application or worker is shutting down.
        """
        try:
            if self.conn:
                self.conn.close()
                logger.info("[+] Database: Connection closed successfully.")
        except Exception as e:
            logger.error(f"[-] Database: Error while closing connection: {e}")

# Module execution flag
logger.info("[@] database.py: Module ready for operations.")