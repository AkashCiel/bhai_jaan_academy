import datetime
import time
import traceback
import markdown  # type: ignore
from typing import Dict, Any, List, Optional
from config import settings
from services.ai_service import AIService
from services.user_service import UserService
from services.email_service import EmailService
from services.context_service import ContextService
from html_generation import generate_learning_plan_html, update_learning_plan_html, generate_topic_report_html
from data import report_repository, response_repository

class ReportService:
    def __init__(self):
        self.ai_service = AIService()
        self.user_service = UserService()
        self.email_service = EmailService()
        self.context_service = ContextService()
    
    def generate_initial_learning_plan(self, email: str, topic: str, paid: bool = False) -> Dict[str, Any]:
        """Generate initial learning plan for new user"""
        try:
            print(f"[Report Service] Generating learning plan for topic: {topic}")
            
            # Generate AI learning plan
            learning_plan = self.ai_service.generate_learning_plan(topic)
            print(f"[Report Service] Learning plan generated.")
            
            if learning_plan == "ERROR":
                print(f"[Report Service] OpenAI returned ERROR for topic: {topic}")
                return {
                    "success": False,
                    "message": "Sorry, this topic is not suitable for learning or may be inappropriate. Please try a different topic.",
                    "email": email,
                    "topic": topic
                }
            
            # Save learning plan response for future context
            try:
                response_repository.save_response(
                    user_email=email,
                    main_topic=topic,
                    response_type="learning_plan",
                    response_data={"raw_response": learning_plan}
                )
            except Exception as e:
                print(f"[Report Service] Warning: Failed to save learning plan response: {e}")
            
            # Extract topic titles
            topic_titles = self.ai_service.extract_topics_from_plan(learning_plan)
            
            # Generate initial learning plan HTML
            html_content = generate_learning_plan_html(
                topic=topic,
                user_email=email,
                topics=topic_titles
            )
            
            # Upload HTML report to GitHub
            public_url = report_repository.upload_report(email, topic, html_content)
            
            # Generate first topic report
            first_topic = topic_titles[0] if topic_titles else None
            report_links = {}
            last_report_time = None
            
            if first_topic:
                print(f"[Report Service] Generating report for first topic: {first_topic}")
                try:
                    report_content = self.ai_service.generate_report_content(first_topic)
                    # Extract quiz and strip from content for separate rendering
                    try:
                        quiz_obj = self.ai_service.extract_quiz_from_report(report_content)
                        content_without_quiz = self.ai_service.strip_quiz_section(report_content) if quiz_obj else report_content
                    except Exception:
                        quiz_obj = None
                        content_without_quiz = report_content
                    
                    # Create initial context summary
                    try:
                        self.context_service.create_initial_context(
                            user_email=email,
                            main_topic=topic,
                            learning_plan=topic_titles,
                            first_report_content=report_content,
                            first_topic=first_topic
                        )
                    except Exception as e:
                        print(f"[Report Service] Warning: Failed to create initial context: {e}")
                    
                    # Save report response for future context
                    try:
                        response_repository.save_response(
                            user_email=email,
                            main_topic=topic,
                            response_type="report",
                            response_data={"raw_response": report_content},
                            report_topic=first_topic
                        )
                    except Exception as e:
                        print(f"[Report Service] Warning: Failed to save report response: {e}")
                    
                    # Convert markdown to HTML
                    report_content_html = markdown.markdown(content_without_quiz)
                    report_html = generate_topic_report_html(
                        topic=first_topic,
                        user_email=email,
                        report_content=report_content_html,
                        quiz=quiz_obj
                    )
                    
                    # Upload the report HTML
                    report_url = report_repository.upload_report(email, topic, report_html, filename=first_topic)
                    report_links[0] = report_url
                    last_report_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    print(f"[Report Service] First topic report uploaded: {report_url}")
                    
                except Exception as e:
                    print(f"[Report Service] Error generating/uploading first topic report: {e}")
            
            # Update the learning plan HTML to link the first topic
            updated_html_content = update_learning_plan_html(
                topic=topic,
                user_email=email,
                topics=topic_titles,
                report_links=report_links
            )
            
            # Upload the updated learning plan HTML
            updated_public_url = report_repository.upload_report(email, topic, updated_html_content)
            
            # Add new user entry
            user_entry = self.user_service.add_user(
                email=email,
                topic=topic,
                learning_plan=topic_titles,
                plan_url=updated_public_url,
                report_links=report_links,
                last_report_time=last_report_time,
                paid=paid
            )
            
            print(f"[Report Service] User entry added to users.json.")
            
            self._wait_before_email()
            
            # Send welcome email
            email_sent = self.email_service.send_welcome_email(email, topic, updated_public_url)
            
            if email_sent:
                return {
                    "success": True,
                    "message": "Welcome email with learning plan link sent successfully!",
                    "email": email,
                    "topic": topic,
                    "plan_url": updated_public_url
                }
            else:
                return {
                    "success": True,
                    "message": "Submission received and learning plan generated! (Email service not configured)",
                    "email": email,
                    "topic": topic,
                    "plan_url": updated_public_url
                }
                
        except Exception as e:
            print(f"[Report Service] Error generating initial learning plan: {e}")
            traceback.print_exc()
            return {
                "success": False,
                "message": f"Error generating learning plan: {str(e)}",
                "email": email,
                "topic": topic
            }
    
    def generate_next_report(self, user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate next report for existing user"""
        try:
            print(f"[Report Service] Generating next report for {user['email']}")
            
            # Check if user should receive a report based on PAID status and current_index
            if not self.user_service.should_generate_report(user):
                current_index = user.get("current_index", 0)
                paid = user.get("paid", False)
                print(f"[Report Service] Skipping report for {user['email']} - payment required (index: {current_index}, paid: {paid})")
                return user
            
            # Get next topic
            idx, topic = self.user_service.get_next_topic(user)
            if topic is None:
                print(f"[Report Service] No more topics for {user['email']}")
                return user
            
            print(f"[Report Service] Generating report for {user['email']} on topic: {topic}")
            
            # Get user context for context-aware report generation
            user_context = self.context_service.get_user_context(user["email"], user["main_topic"])
            
            # Generate report content with context
            if user_context:
                print(f"[Report Service] Using context for {user['email']} on topic: {topic}")
                report_content_md, token_count = self.ai_service.generate_report_content_with_context(
                    topic, user_context, user["learning_plan"]
                )
            else:
                print(f"[Report Service] No context available for {user['email']}, generating without context")
                report_content_md = self.ai_service.generate_report_content(topic)
                token_count = None
            
            # Update context summary with new report content
            try:
                self.context_service.update_context_with_new_report(
                    user_email=user["email"],
                    main_topic=user["main_topic"],
                    new_report_content=report_content_md,
                    new_topic=topic,
                    learning_plan=user["learning_plan"]
                )
            except Exception as e:
                print(f"[Report Service] Warning: Failed to update context: {e}")
            
            # Save report response for future context
            try:
                response_repository.save_response(
                    user_email=user["email"],
                    main_topic=user["main_topic"],
                    response_type="report",
                    response_data={"raw_response": report_content_md},
                    report_topic=topic,
                    token_count=token_count
                )
            except Exception as e:
                print(f"[Report Service] Warning: Failed to save report response: {e}")
            
            # Convert to HTML and generate report
            try:
                quiz_obj = self.ai_service.extract_quiz_from_report(report_content_md)
                content_without_quiz = self.ai_service.strip_quiz_section(report_content_md) if quiz_obj else report_content_md
            except Exception:
                quiz_obj = None
                content_without_quiz = report_content_md

            report_content_html = markdown.markdown(content_without_quiz)
            report_html = generate_topic_report_html(topic, user["email"], report_content_html, quiz=quiz_obj)
            
            # Upload report
            plan_topic = user["main_topic"]
            report_url = report_repository.upload_report(user["email"], plan_topic, report_html, filename=topic)
            
            # Update user progress
            current_index = user.get("current_index", 0)
            last_report_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            updated_user = self.user_service.update_user_progress(
                user, report_url, topic, current_index, last_report_time
            )
            
            # Update learning plan HTML
            updated_plan_html = update_learning_plan_html(
                topic=plan_topic,
                user_email=user["email"],
                topics=user["learning_plan"],
                report_links=updated_user["report_links"]
            )
            
            plan_url = report_repository.upload_report(user["email"], plan_topic, updated_plan_html)
            updated_user["plan_url"] = plan_url
            
            self._wait_before_email()
            
            # Send email
            self.email_service.send_report_email(updated_user, topic, plan_url, report_url)
            
            print(f"[Report Service] Report and email sent for {user['email']} on topic: {topic}")
            return updated_user
            
        except Exception as e:
            print(f"[Report Service] Error for {user['email']} on topic {topic}: {e}")
            traceback.print_exc()
            return user 

    def _wait_before_email(self):
        """Wait for the configured delay before sending an email, with logging."""
        print(f"[Report Service] Waiting {settings.REPORT_DELAY_SECONDS} seconds before sending email...")
        time.sleep(settings.REPORT_DELAY_SECONDS) 