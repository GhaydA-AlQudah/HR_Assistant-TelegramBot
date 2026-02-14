from typing import Dict, Any, Union
from services.employee_service import EmployeeService
from database import Database
from utils.logger import logger

class OnboardingService:
    """
    Service responsible for onboarding new employees.
    Validates requester permissions and handles database insertion for new hires.
    """

    def __init__(self):
        """Initializes database connection and employee search service."""
        try:
            self.db = Database()
            self.emp_service = EmployeeService()
        except Exception as e:
            logger.error(f"Initialization failed in OnboardingService: {e}")
            raise

    def onboard_new_employee(self, hr_emp_id: int, new_emp_data: Dict[str, Any]) -> str:
        """
        Validates HR credentials and creates a new employee record in the database.

        Args:
            hr_emp_id (int): The employee ID of the person performing the onboarding.
            new_emp_data (Dict[str, Any]): Dictionary containing new employee details 
                                          (name, email, telegram_id, job_title, etc.).
        """
        try:
            # 1. Permission Check: Verify if the requester exists and has the 'HR' role
            hr_user = self.emp_service.get_employee_by_id(hr_emp_id)
            
            if not hr_user or hr_user.role.lower() != 'hr':
                logger.warning(f"Unauthorized onboarding attempt by User ID: {hr_emp_id}")
                return (
                    "❌ Access Denied | غير مسموح\n"
                    "This action is restricted to HR personnel only.\n"
                    "هذه الصلاحية متاحة فقط لموظفي الـ HR."
                )

            # 2. Data Preparation: Added telegram_id to the insertion query
            query = """
                INSERT INTO users (
                    full_name, email, telegram_bot_id, hashed_password, role, 
                    job_title, hire_date, salary_basic, dep_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE, %s, %s)
                RETURNING emp_id;
            """
            
            # Map dictionary keys to parameters
            # Note: The key used here is 'telegram_id' to match common naming conventions
            params = (
                new_emp_data.get('full_name'),
                new_emp_data.get('email'),
                new_emp_data.get('telegram_bot_id'), # القيمة الجديدة التي سيتم استلامها
                "hashed_pass_placeholder",
                new_emp_data.get('role', 'employee'),
                new_emp_data.get('job_title'),
                new_emp_data.get('salary_basic'),
                new_emp_data.get('dep_id')
            )

            # 3. Execution: Run the query and commit changes
            result = self.db.execute(query, params, commit=True, fetch=True)

            if result:
                new_id = result[0][0]
                logger.info(f"HR User {hr_emp_id} successfully onboarded {new_emp_data['full_name']} (ID: {new_id})")
                
                return (
                    "✅ <b>Onboarding Successful | تم الإضافة بنجاح</b>\n"
                    "────────────────────────────\n"
                    f"🔸 <b>Name        :</b> <code>{new_emp_data['full_name']}</code>\n"
                    f"🔸 <b>New ID      :</b> <code>{new_id}</code>\n"
                )
            
            return "⚠️ **Partial Success | نجاح جزئي**\nRecord created but ID not returned."

        except Exception as e:
            logger.error(f"Unexpected error during onboarding: {str(e)}")
            return (
                "❌ System Error | خطأ في النظام\n"
                "Possible duplicate email, telegram ID, or database constraint.\n"
                "حدث خطأ فني. قد يكون البريد أو رقم التيليجرام مسجلاً مسبقاً."
            )