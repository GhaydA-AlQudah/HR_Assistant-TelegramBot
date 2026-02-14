import asyncio
import os
from typing import Final, Dict, Any
from telegram.constants import ParseMode

from dotenv import load_dotenv
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, 
    KeyboardButton
)
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    CallbackQueryHandler
)

from utils.logger import logger
from services.telegram_auth_service import TelegramAuthService 
from agents.llm_service import LLMService

# --- Configuration & Initialization ---
load_dotenv()
TOKEN: Final = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN not found in .env file!")
    raise ValueError("TELEGRAM_BOT_TOKEN is missing. Check your .env file.")

# Service instances
auth_service = TelegramAuthService()
llm_service = LLMService()

class HRBot:
    """
    Core class for the HR Telegram Bot to manage interactions and services.
    Includes security layers and business logic routing.
    """

    @staticmethod
    def is_malicious_prompt(user_input: str) -> bool:
        """
        Sanitizes user input to prevent Prompt Injection and Prompt Leakage.
        Checks for restricted keywords related to system internal configuration.
        """
        try:
            forbidden_keywords = [
                "system prompt", "internal instructions", 
                "ignore previous", "give me your prompt",
                "system instructions", "reveal tools", "سستم برومبت", "سيستم برومبت", 
                "برومبت" , "توجيهاتك", "اوامرك", "تعليماتك"
            ]
            normalized_input = user_input.lower()
            return any(keyword in normalized_input for keyword in forbidden_keywords)
        except Exception as e:
            logger.error(f"Error in prompt sanitization: {e}")
            return False

    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the /start command. Displays a dynamic menu based on the user's role.
        """
        try:
            user_id = update.effective_user.id
            user_data = auth_service.get_user_by_telegram_id(user_id)
            
            if not user_data:
                await update.message.reply_text("🔒 Access Denied: You are not registered in the HR system.")
                return 

            user_role = user_data.get('role', 'employee').lower()
            full_name = user_data.get('full_name')

            # Base menu for all employees
            menu_keyboard = [
                [KeyboardButton("📄 My Info - معلوماتي الشخصية")],
                [KeyboardButton("📅 Leaves Balance as PDF - كشف الإجازات (PDF)")],
                [KeyboardButton("📝 Leave Request - طلب إجازة")]
            ]

            # Role-based menu customization
            if user_role == 'manager':
                menu_keyboard.insert(1, [KeyboardButton("👥 Employees Info - معلومات الموظفين")])
            elif user_role == 'hr':
                menu_keyboard.insert(1, [KeyboardButton("👥 Employees Info - معلومات الموظفين")])
                menu_keyboard.append([KeyboardButton("➕ Onboarding - إضافة موظف")])

            menu_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

            welcome_msg = (
                f"Welcome <b>{full_name}</b>! 👋\n"
                f"Role: <code>{user_role.upper()}</code>\n\n"
                "How can I assist you today?"
            )

            await update.message.reply_text(
                welcome_msg,
                reply_markup=menu_markup,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error in start_command: {e}")
            await update.message.reply_text("⚠️ An error occurred while starting the bot.")

    @staticmethod
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Routes incoming text messages to the processing engine after security checks.
        """
        try:
            if not update.message or not update.message.text:
                return

            user_text = update.message.text

            # --- Security Check: Prompt Leakage Mitigation ---
            if HRBot.is_malicious_prompt(user_text):
                logger.warning(f"Blocked potential prompt injection from user {update.effective_user.id}")
                await update.message.reply_text("🛡️ Security Policy: I cannot disclose internal configuration or system instructions.")
                return

            await HRBot.process_and_reply(update, update.message, user_text)
        except Exception as e:
            logger.error(f"Error in handle_message: {e}")

    @staticmethod
    async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles interactions with Inline Buttons (Callback Queries).
        """
        query = update.callback_query
        try:
            await query.answer() 
            
            text_mapping = {
                'get_my_info': 'بدي معلوماتي الشخصية',
                'onboarding': 'بدي أعمل onboarding لموظف جديد',
                'team_info': 'بدي معلومات الموظفين اللي عندي في القسم',
                'leave_balance': 'اعطيني كشف رصيد إجازاتي بصيغة PDF',
                'leave_request': 'بدي أقدم طلب إجازة جديد',
                'cancel_action': 'إلغاء العملية'
            }
            
            user_text = text_mapping.get(query.data)

            if query.data == "cancel_action":
                await query.edit_message_text("❌ Operation cancelled.")
                return

            if query.data.startswith("confirm_l_"):
                await HRBot.process_and_reply(update, query.message, f"CONFIRM_LEAVE_DATA:{query.data}")
                return

            if user_text:
                await HRBot.process_and_reply(update, query.message, user_text)
                
        except Exception as e:
            logger.error(f"Error in button_handler: {e}")

    @staticmethod
    async def process_and_reply(update: Update, message_obj, text: str):
        """
        Central logic to process requests via LLM Service and manage tool outputs.
        """
        try:
            user_id = update.effective_user.id
            user_data = auth_service.get_user_by_telegram_id(user_id)

            if not user_data:
                await message_obj.reply_text("🔒 Please register to access HR services.")
                return

            emp_id = user_data.get('emp_id') 
            await message_obj.chat.send_action("typing")

            # Orchestrate message through AI Agentic Layer
            tool_response, llm_response = await llm_service.process_user_message(text, emp_id)
            
            # 1. Handle conversational AI response
            if llm_response and "ACTION_" not in llm_response:
                await message_obj.reply_text(llm_response, parse_mode=ParseMode.HTML)

            # 2. Handle Deterministic Tool Outputs
            if tool_response:
                if "ACTION_SEND_PDF:" in tool_response:
                    file_path = tool_response.split(":")[1]
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as doc:
                            await message_obj.reply_document(
                                document=doc, 
                                caption="Here is your leave balance report 📄"
                            )
                    else:
                        await message_obj.reply_text("⚠️ Error: PDF file not found.")
                
                elif "ACTION_CONFIRM_LEAVE:" in tool_response:
                    data = tool_response.split(":")[1]
                    keyboard = [[
                        InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_l_{data}"),
                        InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")
                    ]]
                    await message_obj.reply_text(
                        "Please confirm your leave request details above.",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                else:
                    # Generic tool output (e.g., formatted employee info from Service Layer)
                    await message_obj.reply_text(tool_response, parse_mode=ParseMode.HTML)

        except Exception as e:
            logger.error(f"Critical error in process_and_reply: {e}")
            await message_obj.reply_text("⚠️ Sorry, I encountered a problem processing your request.")

def main():
    """
    Main entry point for the HR Telegram Application.
    """
    try:
        logger.info("Bot is starting...")
        app = Application.builder().token(TOKEN).build()
        
        # Register Handlers
        app.add_handler(CommandHandler("start", HRBot.start_command))
        app.add_handler(CallbackQueryHandler(HRBot.button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, HRBot.handle_message))
        
        logger.info("Bot is running. Press Ctrl+C to stop.")
        app.run_polling()
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")

if __name__ == "__main__":
    main()