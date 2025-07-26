import openai
import re
from typing import Optional, Dict, Any, Tuple
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

The tone should be clear, engaging, and accessible to someone new to the subject. Include at least 3-5 relevant links throughout the report. IMPORTANT: Only include links to real, working websites and resources. Verify that all URLs are valid and accessible.

For mathematical formulas, use proper LaTeX syntax:
- Inline math: $formula$ or \\(formula\\)
- Display math: $$formula$$ or \\[formula\\]
- Examples: $|\psi\rangle = \alpha |0\rangle + \beta |1\rangle$ for quantum states
- Use proper notation for quantum computing: $|0\rangle$, $|1\rangle$, $\langle\psi|$, etc."""
        
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

    def generate_report_content_with_context(self, topic: str, context: str, learning_plan: list) -> Tuple[str, int]:
        """
        Generate educational report content using OpenAI with user context
        """
        context_prompt = f"""Write a comprehensive, beginner-friendly educational report on the topic: "{topic}".

IMPORTANT CONTEXT - Previous Learning Summary:
{context}

Learning Plan Structure:
{chr(10).join([f"- {topic}" for topic in learning_plan])}

The report should:
- Build upon the user's previous learning (referenced in the context above)
- Maintain consistency with previously covered topics
- Create a coherent narrative that fits into the overall learning journey
- Include references to previously learned concepts where relevant
- Continue the progressive learning structure

The report should include:
- An introduction that connects to previous learning
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

The tone should be clear, engaging, and accessible to someone new to the subject. Include at least 3-5 relevant links throughout the report. IMPORTANT: Only include links to real, working websites and resources. Verify that all URLs are valid and accessible.

For mathematical formulas, use proper LaTeX syntax:
- Inline math: $formula$ or \\(formula\\)
- Display math: $$formula$$ or \\[formula\\]
- Examples: $|\psi\rangle = \alpha |0\rangle + \beta |1\rangle$ for quantum states
- Use proper notation for quantum computing: $|0\rangle$, $|1\rangle$, $\langle\psi|$, etc."""
        
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert educator and science communicator who creates coherent, progressive learning experiences."},
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
        summary_prompt = f"""Create a concise, coherent summary that combines the existing learning context with new content.

EXISTING LEARNING SUMMARY:
{existing_summary if existing_summary else "No previous learning context available."}

NEW REPORT CONTENT (Topic: {new_topic}):
{new_report_content}

COMPLETE LEARNING PLAN:
{chr(10).join([f"- {topic}" for topic in learning_plan])}

Your task is to create a comprehensive summary that:
1. Integrates the new content seamlessly with existing learning
2. Maintains the narrative flow and learning progression
3. Highlights key concepts and connections between topics
4. Provides a coherent overview of the user's learning journey so far
5. Keeps the summary concise but comprehensive (aim for 300-500 words)

Focus on:
- How the new topic fits into the broader learning plan
- Connections between previously learned concepts and the new topic
- The user's learning progression and depth of understanding
- Key insights and takeaways from the learning journey so far

Write the summary in a clear, educational tone that would help generate future reports that build upon this foundation."""
        
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert educational content curator who creates coherent learning summaries."},
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
        initial_prompt = f"""Create an initial learning context summary for a new user starting their learning journey.

MAIN TOPIC: {main_topic}
FIRST TOPIC COVERED: {first_topic}
COMPLETE LEARNING PLAN:
{chr(10).join([f"- {topic}" for topic in learning_plan])}

FIRST REPORT CONTENT:
{first_report_content}

Your task is to create an initial context summary that:
1. Establishes the foundation for the learning journey
2. Captures the key insights from the first report
3. Sets up the framework for future learning progression
4. Provides context for generating subsequent reports
5. Maintains a coherent narrative structure

The summary should:
- Introduce the main learning topic and its scope
- Highlight key concepts from the first report
- Establish the learning progression framework
- Set expectations for the learning journey ahead
- Be concise but comprehensive (aim for 200-300 words)

Write in a clear, educational tone that will help generate future reports that build upon this foundation."""
        
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert educational content curator who creates foundational learning summaries."},
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