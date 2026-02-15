from typing import Dict, List, Tuple, Optional, Any

from pydantic_ai.messages import ModelRequest, ToolReturnPart, ModelMessage
from agents.hr_agent import hr_agent, HRDeps
from utils.logger import logger

# Global registry to maintain chat history per employee
# Key: emp_id (int), Value: List of ModelMessage objects
chat_history_registry: Dict[int, List[ModelMessage]] = {}

class LLMService:
    """
    Service responsible for managing interactions between the Telegram Bot 
    and the Pydantic AI HR Agent, including session history management.
    """

    def __init__(self):
        """Initializes the LLMService and logs status."""
        logger.info("[+] LLMService initialized with Pydantic AI Tools and History Support")

    async def process_user_message(self, user_prompt: str, emp_id: int, role: str) -> Tuple[Optional[str], str]:
        """
        Processes a user message by invoking the HR Agent with existing chat history.

        Args:
            user_prompt (str): The text message sent by the user.
            emp_id (int): The unique identifier for the employee (used for context and history).

        Returns:
            Tuple[Optional[str], str]: 
                - The first element is the raw content returned by a tool (if triggered).
                - The second element is the natural language response from the AI.
        """
        try:
            # Prepare dependencies for the HR Agent
            deps = HRDeps(emp_id=emp_id, role = role)
            
            # Initialize history for new users to prevent KeyErrors
            if emp_id not in chat_history_registry:
                chat_history_registry[emp_id] = []
                logger.debug(f"Created new history session for emp_id: {emp_id}")
            
            logger.info(f"Processing request for emp_id: {emp_id}")

            # Execute the agent run within the current context and history
            result = await hr_agent.run(
                user_prompt, 
                deps=deps,
                message_history=chat_history_registry[emp_id]
            )

            # Update the registry with the complete message thread (including new turns)
            chat_history_registry[emp_id] = result.all_messages()

            # Extract specific tool output if the Agent decided to call a function
            final_tool_content = self._extract_tool_return(result.new_messages())
            
            if final_tool_content:
                logger.info(f"🎯 Tool output captured: {final_tool_content[:50]}...")

            return final_tool_content, result.output

        except Exception as e:
            logger.error(f"Critical error in LLMService.process_user_message: {str(e)}")
            # Return None for tool output and a safe fallback message for the UI
            return None, "⚠️ System Issue | مشكلة في النظام\n"

    def _extract_tool_return(self, messages: List[ModelMessage]) -> Optional[str]:
        """
        Helper method to traverse the latest message parts and find tool execution results.

        Args:
            messages (List[ModelMessage]): The list of new messages from the agent run.

        Returns:
            Optional[str]: The string content of the tool return, or None if no tool was used.
        """
        try:
            for msg in messages:
                # We check ModelRequest because ToolReturnPart is often nested 
                # within the conversational turn responses
                if hasattr(msg, 'parts'):
                    for part in msg.parts:
                        if isinstance(part, ToolReturnPart):
                            return str(part.content)
            return None
        except Exception as e:
            logger.warning(f"Failed to extract tool return content: {e}")
            return None


