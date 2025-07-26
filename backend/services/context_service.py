from typing import Dict, Any, Optional, Tuple
from data.context_repository import ContextRepository
from services.ai_service import AIService
from config import settings

class ContextService:
    """Service for managing user context summaries"""
    
    def __init__(self):
        self.context_repo = ContextRepository()
        self.ai_service = AIService()
    
    def get_user_context(self, user_email: str, main_topic: str) -> Optional[str]:
        """Retrieve context summary for user/topic."""
        try:
            context_data = self.context_repo.load_context_summary(user_email, main_topic)
            if context_data:
                return context_data.get("summary", "")
            return None
        except Exception as e:
            print(f"[Context Service] Error retrieving user context: {e}")
            return None
    
    def update_context_with_new_report(self, user_email: str, main_topic: str, 
                                     new_report_content: str, new_topic: str, 
                                     learning_plan: list) -> None:
        """Update context summary with new report content."""
        try:
            self.context_repo.update_context_summary(
                user_email, main_topic, new_report_content, new_topic, learning_plan
            )
            print(f"[Context Service] Updated context for {user_email} on {main_topic}")
        except Exception as e:
            print(f"[Context Service] Error updating context: {e}")
            # Don't block report generation if context update fails
    
    def generate_context_summary(self, update_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Generate context summary using AI."""
        try:
            existing_summary = update_data.get("existing_summary", "")
            new_report_content = update_data.get("new_report_content", "")
            new_topic = update_data.get("new_topic", "")
            learning_plan = update_data.get("learning_plan", [])
            current_topics_covered = update_data.get("current_topics_covered", [])
            current_report_count = update_data.get("current_report_count", 0)
            
            # Generate new summary using AI
            new_summary, token_count = self.ai_service.summarize_content_for_context(
                existing_summary, new_report_content, new_topic, learning_plan
            )
            
            # Update topics covered
            updated_topics_covered = current_topics_covered.copy()
            if new_topic not in updated_topics_covered:
                updated_topics_covered.append(new_topic)
            
            # Prepare summary data
            summary_data = {
                "summary": new_summary,
                "topics_covered": updated_topics_covered,
                "report_count": current_report_count + 1,
                "metadata": {
                    "last_topic_added": new_topic,
                    "total_topics_in_plan": len(learning_plan),
                    "topics_remaining": len(learning_plan) - len(updated_topics_covered)
                }
            }
            
            return summary_data, token_count
            
        except Exception as e:
            print(f"[Context Service] Error generating context summary: {e}")
            # Return minimal summary data if generation fails
            return {
                "summary": existing_summary,
                "topics_covered": current_topics_covered,
                "report_count": current_report_count,
                "metadata": {"error": str(e)}
            }, 0
    
    def create_initial_context(self, user_email: str, main_topic: str, 
                             learning_plan: list, first_report_content: str, 
                             first_topic: str) -> None:
        """Create initial context summary for new user."""
        try:
            # Generate initial summary
            initial_summary, token_count = self.ai_service.generate_initial_context_summary(
                main_topic, learning_plan, first_report_content, first_topic
            )
            
            # Prepare initial context data
            context_data = {
                "summary": initial_summary,
                "topics_covered": [first_topic],
                "report_count": 1,
                "metadata": {
                    "initial_topic": first_topic,
                    "total_topics_in_plan": len(learning_plan),
                    "topics_remaining": len(learning_plan) - 1
                }
            }
            
            # Save initial context
            self.context_repo.save_context_summary(user_email, main_topic, context_data, token_count)
            print(f"[Context Service] Created initial context for {user_email} on {main_topic}")
            
        except Exception as e:
            print(f"[Context Service] Error creating initial context: {e}")
            # Don't block user creation if context creation fails 