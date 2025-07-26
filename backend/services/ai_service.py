import openai
import re
from typing import Optional, Dict, Any
from config import settings

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.OPENAI_TIMEOUT
        )
    
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

    def generate_report_content(self, topic: str) -> str:
        """
        Generate educational report content using OpenAI
        """
        report_prompt = f"""Write a comprehensive, beginner-friendly educational report on the topic: "{topic}".

The report should include:
- An introduction to the topic
- Key concepts and definitions
- Real-world applications or examples
- Common misconceptions or pitfalls
- Further reading/resources (if appropriate)

IMPORTANT: Format your response with clear structural markers:
- Use "## Heading:" for main sections (e.g., "## Introduction:", "## Key Concepts:", "## Real-World Applications:")
- Use "### Subheading:" for subsections
- Use "**Bold text**" for emphasis and important terms
- Use "- " for bullet points
- Use "---" for section breaks
- Use "**Link: [text](url)**" for any relevant links

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

The tone should be clear, engaging, and accessible to someone new to the subject. Include at least 3-5 relevant links throughout the report."""
        
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert educator and science communicator."},
                {"role": "user", "content": report_prompt}
            ],
            max_tokens=settings.OPENAI_MAX_TOKENS_REPORT,
            temperature=settings.OPENAI_TEMPERATURE
        )
        return response.choices[0].message.content.strip()

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