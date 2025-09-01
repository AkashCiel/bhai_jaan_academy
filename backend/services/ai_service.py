import openai
import re
from typing import Optional, Dict, Any, Tuple
from config import settings
from config.constants import AI_PROMPTS

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.OPENAI_TIMEOUT
        )
    
    def _build_report_prompt(self, topic: str) -> str:
        """Build a complete report prompt from modular components"""
        return f"""Write a comprehensive educational report on the topic: "{topic}".

{AI_PROMPTS['CONTENT_EXPANSION']}

{AI_PROMPTS['REPORT_STRUCTURE']}

{AI_PROMPTS['ADVANCED_CONTENT']}

{AI_PROMPTS['CONTENT_GUIDELINES']}

{AI_PROMPTS['ENHANCED_CONCEPTS']}

{AI_PROMPTS['ANALOGIES_METAPHORS']}

{AI_PROMPTS['CONCEPT_CONNECTIONS']}

{AI_PROMPTS['INTERACTIVE_ELEMENTS']}

{AI_PROMPTS['QUIZ_GENERATION']}
{AI_PROMPTS['QUIZ_CONTENT_GUIDELINES']}
{AI_PROMPTS['QUIZ_INTEGRATION']}

{AI_PROMPTS['FORMATTING_INSTRUCTIONS']}

Example format:
## Introduction:
This is the introduction paragraph...

## Key Concepts:
### Basic Definition:
**Term:** Definition here...

- Point 1
- Point 2

## Real-World Applications:
Examples of how this is used...

## Advanced Applications and Research Frontiers:
Cutting-edge developments and future implications...

## Think About This:
[Thought-provoking questions for key concepts]

{AI_PROMPTS['TONE_STYLE']}

{AI_PROMPTS['LINK_FORMATTING']}

{AI_PROMPTS['MATH_FORMATTING']}"""
    
    def _build_context_prompt(self, topic: str, context: str, learning_plan: list) -> str:
        """Build a context-aware report prompt"""
        return f"""Write a comprehensive, beginner-friendly educational report on the topic: "{topic}".

{AI_PROMPTS['CONTENT_EXPANSION']}

IMPORTANT CONTEXT - Previous Learning Summary:
{context}

Learning Plan Structure:
{chr(10).join([f"- {topic}" for topic in learning_plan])}

{AI_PROMPTS['CONTEXT_HANDLING']}

{AI_PROMPTS['LEARNING_JOURNEY_INTEGRATION']}

{AI_PROMPTS['REPORT_STRUCTURE'].replace('introduction to the topic', 'introduction that connects to previous learning')}

{AI_PROMPTS['ADVANCED_CONTENT']}

{AI_PROMPTS['CONTENT_GUIDELINES']}

{AI_PROMPTS['ENHANCED_CONCEPTS']}

{AI_PROMPTS['ANALOGIES_METAPHORS']}

{AI_PROMPTS['CONCEPT_CONNECTIONS']}

{AI_PROMPTS['INTERACTIVE_ELEMENTS']}

{AI_PROMPTS['QUIZ_GENERATION']}
{AI_PROMPTS['QUIZ_CONTENT_GUIDELINES']}
{AI_PROMPTS['QUIZ_INTEGRATION']}

{AI_PROMPTS['FORMATTING_INSTRUCTIONS']}

{AI_PROMPTS['CONTEXT_TONE_STYLE']}

{AI_PROMPTS['LINK_FORMATTING']}

{AI_PROMPTS['MATH_FORMATTING']}"""

    def _build_summary_prompt(self, existing_summary: str, new_report_content: str, 
                             new_topic: str, learning_plan: list) -> str:
        """Build a summary prompt from modular components"""
        return f"""Create a concise, coherent summary that combines the existing learning context with new content.

EXISTING LEARNING SUMMARY:
{existing_summary if existing_summary else "No previous learning context available."}

NEW REPORT CONTENT (Topic: {new_topic}):
{new_report_content}

COMPLETE LEARNING PLAN:
{chr(10).join([f"- {topic}" for topic in learning_plan])}

{AI_PROMPTS['SUMMARY_TASK']}

{AI_PROMPTS['SUMMARY_FOCUS']}

{AI_PROMPTS['SUMMARY_TONE']}"""
    
    def _build_initial_summary_prompt(self, main_topic: str, learning_plan: list, 
                                     first_report_content: str, first_topic: str) -> str:
        """Build an initial summary prompt from modular components"""
        return f"""Create an initial learning context summary for a new user starting their learning journey.

MAIN TOPIC: {main_topic}
FIRST TOPIC COVERED: {first_topic}
COMPLETE LEARNING PLAN:
{chr(10).join([f"- {topic}" for topic in learning_plan])}

FIRST REPORT CONTENT:
{first_report_content}

{AI_PROMPTS['INITIAL_SUMMARY_TASK']}

{AI_PROMPTS['INITIAL_SUMMARY_REQUIREMENTS']}

{AI_PROMPTS['INITIAL_SUMMARY_TONE']}"""

    def generate_learning_plan(self, topic: str) -> str:
        """
        Generate a 30-day learning plan using OpenAI GPT-4
        Returns the plan as a string, or "ERROR" if the topic is invalid
        """
        try:
            prompt = f"""Create a comprehensive 30-day learning plan for {topic}. 

The plan should include:
1. A list of 10 topics for each of the three expertise levels:
   - Beginner (10 topics)
   - Intermediate (10 topics) 
   - Advanced (10 topics)

If the topic is not suitable for learning or is inappropriate, respond with "ERROR"."""

            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator specializing in creating structured learning plans."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS_PLAN,
                temperature=settings.OPENAI_TEMPERATURE
            )
            plan = response.choices[0].message.content.strip()
            print(f"OpenAI API raw response: {plan}")
            # Only treat as error if the response is exactly 'ERROR' or starts with 'ERROR'
            if plan.strip().upper() == "ERROR" or plan.strip().upper().startswith("ERROR"):
                return "ERROR"
            return plan
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"ERROR: {str(e)}"

    def _parse_quiz_from_markdown(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract structured quiz data from the 'Interactive Quiz' section in markdown."""
        try:
            quiz_section_match = re.search(r"##\s*Interactive Quiz:\s*Test Your Understanding([\s\S]+)$", content, re.IGNORECASE)
            if not quiz_section_match:
                return None
            quiz_block = quiz_section_match.group(1)

            def extract(pattern: str) -> Optional[str]:
                m = re.search(pattern, quiz_block, re.IGNORECASE | re.MULTILINE)
                return m.group(1).strip() if m else None

            question = extract(r"\*\*Question:\*\*\s*(.+)")
            correct_answer = extract(r"\*\*Correct Answer:\*\*\s*([A-D])\b")
            why_matters = extract(r"\*\*Why This Matters:\*\*\s*(.+)")

            option_texts: Dict[str, str] = {}
            for opt in ["A", "B", "C", "D"]:
                txt = extract(rf"^{opt}\)\s+(.+)$")
                if txt:
                    option_texts[opt] = txt

            option_explanations: Dict[str, str] = {}
            for opt in ["A", "B", "C", "D"]:
                expl = extract(rf"-\s*\*\*Option {opt}:\*\*\s*(.+)")
                if expl:
                    option_explanations[opt] = expl

            if not (question and correct_answer and len(option_texts) == 4 and len(option_explanations) == 4):
                return None

            options = [
                {"id": k, "text": option_texts[k], "explanation": option_explanations.get(k, "")}
                for k in ["A", "B", "C", "D"]
            ]

            return {
                "question": question,
                "options": options,
                "correct_answer": correct_answer,
                "why_it_matters": why_matters or ""
            }
        except Exception:
            return None

    def strip_quiz_section(self, content: str) -> str:
        """Remove the quiz section from the markdown content (if present)."""
        return re.sub(r"\n?##\s*Interactive Quiz:\s*Test Your Understanding[\s\S]+$", "", content, flags=re.IGNORECASE)

    def extract_quiz_from_report(self, content: str) -> Optional[Dict[str, Any]]:
        """Public helper to extract a quiz object from report markdown."""
        return self._parse_quiz_from_markdown(content)

    def generate_report_content(self, topic: str) -> str:
        """
        Generate educational report content using OpenAI
        """
        report_prompt = self._build_report_prompt(topic)
        
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": AI_PROMPTS['SYSTEM_MESSAGES']['REPORT_GENERATOR']},
                {"role": "user", "content": report_prompt}
            ],
            max_tokens=settings.OPENAI_MAX_TOKENS_REPORT,
            temperature=settings.OPENAI_TEMPERATURE
        )
        return response.choices[0].message.content.strip()

    def generate_report_content_with_context(self, topic: str, context: str, learning_plan: list) -> Tuple[str, int]:
        """
        Generate educational report content using OpenAI with user context
        """
        context_prompt = self._build_context_prompt(topic, context, learning_plan)
        
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": AI_PROMPTS['SYSTEM_MESSAGES']['CONTEXT_AWARE_GENERATOR']},
                {"role": "user", "content": context_prompt}
            ],
            max_tokens=settings.OPENAI_MAX_TOKENS_REPORT,
            temperature=settings.OPENAI_TEMPERATURE
        )
        content = response.choices[0].message.content.strip()
        token_usage = response.usage.total_tokens if hasattr(response, 'usage') and response.usage else 0
        return content, token_usage

    def summarize_content_for_context(self, existing_summary: str, new_report_content: str, 
                                    new_topic: str, learning_plan: list) -> Tuple[str, int]:
        """
        Generate a concise summary for context storage using OpenAI
        """
        summary_prompt = self._build_summary_prompt(existing_summary, new_report_content, new_topic, learning_plan)
        
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": AI_PROMPTS['SYSTEM_MESSAGES']['SUMMARY_GENERATOR']},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=1000,  # Generous token limit for high-quality summary
            temperature=0.5  # Lower temperature for more consistent summaries
        )
        content = response.choices[0].message.content.strip()
        token_usage = response.usage.total_tokens if hasattr(response, 'usage') and response.usage else 0
        return content, token_usage

    def generate_initial_context_summary(self, main_topic: str, learning_plan: list, 
                                       first_report_content: str, first_topic: str) -> Tuple[str, int]:
        """
        Generate initial context summary for new user
        """
        initial_prompt = self._build_initial_summary_prompt(main_topic, learning_plan, first_report_content, first_topic)
        
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": AI_PROMPTS['SYSTEM_MESSAGES']['INITIAL_SUMMARY_GENERATOR']},
                {"role": "user", "content": initial_prompt}
            ],
            max_tokens=800,
            temperature=0.5
        )
        content = response.choices[0].message.content.strip()
        token_usage = response.usage.total_tokens if hasattr(response, 'usage') and response.usage else 0
        return content, token_usage

    def extract_topics_from_plan(self, plan: str) -> list:
        """Extract only the topic titles from the OpenAI learning plan response."""
        topics = []
        for line in plan.splitlines():
            # Match lines like '1. **Topic**' or '1. Topic'
            match = re.match(r'^\s*\d+\.\s+\*?\*?(.+?)\*?\*?\s*$', line)
            if match:
                topic = match.group(1).strip()
                topics.append(topic)
        return topics

    def validate_topic(self, topic: str) -> bool:
        """Validate if a topic is suitable for learning"""
        # Basic validation - topic should not be empty and should be reasonable length
        if not topic or len(topic.strip()) < 2 or len(topic.strip()) > 100:
            return False
        return True 