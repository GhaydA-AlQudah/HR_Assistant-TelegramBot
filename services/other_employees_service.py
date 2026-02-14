from typing import Optional
from utils.logger import logger
from database import Database
from models import User
from expectations import UnauthorizedAccess
class OtherEmployeeService:
    def __init__(self):
        try:
            self.db = Database()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def get_employee_info_shared(self, requester_id: int, target_emp_name: str) -> str:
        """
        Retrieves employee info with dynamic visibility based on roles.
        Managers see 'Salary', others see 'Basic Public Info'.
        """
        query = """
            SELECT 
                e.full_name, e.role, e.job_title, e.email, e.salary_basic, 
                d.name, e.dep_id,
                m.role as req_role, m.dep_id as req_dep_id
            FROM users e
            JOIN departments d ON e.dep_id = d.dep_id
            CROSS JOIN users m WHERE m.emp_id = %s AND e.full_name = %s
        """

        try:
            result = self.db.execute(query, (requester_id, target_emp_name), fetch=True)

            if not result:
                return (
                    "❌ User Not Found | لم يتم العثور على الموظف\n"
                    f"No record found for: {target_emp_name}"
                )

            # استخراج البيانات من النتيجة
            row = result[0]
            name, role, title, email, salary, dep_name, dep_id, req_role, req_dep_id = row

            # منطق الصلاحيات: هل السائل هو مدير نفس القسم؟
            is_manager_of_same_dept = (req_role.lower() == 'manager' and dep_id == req_dep_id)

            # بناء الرد الأساسي (المتاح للجميع)
            response = (
                "👤 Employee Profile | ملف الموظف\n"
                "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                f"🔸 Name          :{name}\n"
                f"🔸 Role         :{role.capitalize()}\n"
                f"🔸 Job Title     :{title}\n"
                f"🔸 Department :{dep_name}\n"
                f"🔸 Email        :{email}\n"
            )

            # إضافة الراتب فقط إذا كان السائل هو مدير القسم
            if is_manager_of_same_dept:
                response += f"💰 Salary :{salary} JOD\n"
                response += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                response += "✅ Full Access Granted | صلاحية مدير قسم"
            else:
                response += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                response += "ℹ️ Public Profile Only | معلومات عامة فقط"

            return response

        except Exception as e:
            logger.error(f"Error in shared lookup: {e}")
            return "❌ **System Error | خطأ في النظام**\nCould not retrieve data."

