from fpdf import FPDF
import os
from typing import List, Dict, Any
from utils.logger import logger

class PDFService:
    """
    Service responsible for generating professional PDF documents and HR reports.
    """

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Could not create directory {self.output_dir}: {e}")

    def generate_leave_report(self, emp_name: str, balances: List[Dict[str, Any]]) -> str:
        try:
            logger.info(f"Generating professional PDF report for: {emp_name}")
            
            # Initialization
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # --- 1. Branding & Header Section ---
            # Logo-like text or Company Name placeholder
            pdf.set_font("Arial", "B", 10)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, "HR MANAGEMENT SYSTEM", ln=True, align="R")
            
            pdf.ln(5)
            
            # Main Title
            pdf.set_font("Arial", "B", 22)
            pdf.set_text_color(44, 62, 80)  # Dark Blue/Gray
            pdf.cell(0, 15, "Leave Balance Report", ln=True, align="L")
            
            # Decorative Line
            pdf.set_draw_color(44, 62, 80)
            pdf.set_line_width(0.5)
            pdf.line(10, 38, 200, 38)
            
            pdf.ln(10)
            
            # Employee Info Section
            pdf.set_font("Arial", "B", 12)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(35, 10, "Employee Name:", ln=0)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, emp_name, ln=True)
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(35, 8, "Report Date:", ln=0)
            pdf.set_font("Arial", "", 12)
            from datetime import datetime
            pdf.cell(0, 8, datetime.now().strftime("%Y-%m-%d"), ln=True)
            
            pdf.ln(10)
            
            # --- 2. Table Header ---
            pdf.set_font("Arial", "B", 11)
            pdf.set_fill_color(52, 152, 219) # Professional Blue
            pdf.set_text_color(255, 255, 255) # White Text
            
            headers = ["Leave Type", "Total Entitlement", "Days Used", "Remaining"]
            widths = [55, 45, 45, 45]
            
            for i, header in enumerate(headers):
                pdf.cell(widths[i], 12, header, border=0, align="C", fill=True)
            pdf.ln()
            
            # --- 3. Table Body ---
            pdf.set_font("Arial", "", 11)
            pdf.set_text_color(0, 0, 0)
            fill = False # For Zebra striping
            
            for balance in balances:
                # Zebra striping logic for rows
                if fill:
                    pdf.set_fill_color(245, 245, 245)
                else:
                    pdf.set_fill_color(255, 255, 255)
                
                pdf.cell(widths[0], 10, f" {str(balance.get('leave_type', 'N/A'))}", border='B', fill=True)
                pdf.cell(widths[1], 10, str(balance.get('total', 0)), border='B', align="C", fill=True)
                pdf.cell(widths[2], 10, str(balance.get('used', 0)), border='B', align="C", fill=True)
                
                # Bold the remaining days to make them stand out
                pdf.set_font("Arial", "B", 11)
                pdf.cell(widths[3], 10, str(balance.get('remaining', 0)), border='B', align="C", fill=True)
                pdf.set_font("Arial", "", 11)
                
                pdf.ln()
                fill = not fill # Toggle row color
            
            # --- 4. Footer Section ---
            pdf.ln(20)
            pdf.set_font("Arial", "I", 9)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 10, "This is an electronically generated report. No signature required.", ln=True, align="C")

            # Save the file
            safe_name = emp_name.replace(" ", "_").lower()
            file_path = os.path.join(self.output_dir, f"leave_{safe_name}.pdf")
            
            pdf.output(file_path)
            
            logger.info(f"Professional PDF successfully generated at: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Failed to generate PDF for {emp_name}: {str(e)}")
            raise Exception(f"Technical error during PDF creation: {e}")