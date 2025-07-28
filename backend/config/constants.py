# File extensions
FILE_EXTENSIONS = {
    'HTML': '.html',
    'JSON': '.json',
    'USERS_FILE': 'users.json'
}

# Email template paths
EMAIL_TEMPLATES = {
    'WELCOME': 'templates/welcome_email.html',
    'REPORT': 'templates/report_email.html'
}

# AI model configurations
AI_MODELS = {
    'DEFAULT': 'gpt-4o-mini',
    'TEMPERATURE': 0.7,
    'TIMEOUT': 120
}

# Time delays (in seconds)
DELAYS = {
    'EMAIL_DEPLOYMENT': 5,  # Reduced from 300 to 5 seconds
}

# GitHub configuration for reports repository
GITHUB_CONFIG = {
    'REPO_OWNER': 'AkashCiel',
    'REPO_NAME': 'bhai_jaan_academy_reports',
    'BRANCH': 'main'
}

# GitHub configuration for main repository (for users.json sync)
MAIN_REPO_CONFIG = {
    'REPO_OWNER': 'AkashCiel',
    'REPO_NAME': 'bhai_jaan_academy',
    'BRANCH': 'main'
}

# AI Prompt components for modular prompt construction
AI_PROMPTS = {
    # Core report structure
    'REPORT_STRUCTURE': """
The report should include:
- An introduction to the topic
- Key concepts and definitions
- Real-world applications or examples
- A rich narrative that connects the concepts to each other and to real-world applications. Its best if this narrative is presented as one or multiple stories.
- A conclusion that summarizes the key takeaways and provides a call to action for the user to explore the topic further.
""",
    
    # Content composition guidelines
    'CONTENT_GUIDELINES': """
IMPORTANT: Carefully follow these instructions while composing the report:
- The report should not assume any prior knowledge on part of the user. 
- At the same time, it should be comprehensive and self-sufficient as a reading resource for the user.
- Provide standard definitions of the terms but also expand on them with example if they are too abstract.
- Provide metaphors, famous anecdotes, historical facts, and other interesting details to keep the reader engaged. However, do not overdo it.
- Include relevant links, whenever applicable, to allow the reader to explore the topic further.
""",
    
    # Formatting instructions
    'FORMATTING_INSTRUCTIONS': """
FORMATTING: Format your response with clear structural markers:
- Use "## Heading:" for main sections (e.g., "## Introduction:", "## Key Concepts:", "## Real-World Applications:")
- Use "### Subheading:" for subsections
- Use "**Bold text**" for emphasis and important terms
- Use "- " for bullet points
- Use "---" for section breaks
- Use "**Link: [text](url)**" for any relevant links. IMPORTANT: Only include links to real, working websites and resources. Verify that all URLs are valid and accessible.
""",
    
    # Link formatting
    'LINK_FORMATTING': """
IMPORTANT: For links, use this exact format: **Link: [Resource Name](URL)**
Example: **Link: [IBM Quantum Experience](https://quantum-computing.ibm.com/)**
Only include links to real, working websites and resources. Verify that all URLs are valid and accessible.
""",
    
    # Mathematical formatting
    'MATH_FORMATTING': """
For mathematical formulas, use proper LaTeX syntax:
- Inline math: $formula$ or \\(formula\\)
- Display math: $$formula$$ or \\[formula\\]
- Examples: $|\\psi\\rangle = \\alpha |0\\rangle + \\beta |1\\rangle$ for quantum states
- Use proper notation for quantum computing: $|0\\rangle$, $|1\\rangle$, $\\langle\\psi|$, etc.
""",
    
    # Context handling instructions
    'CONTEXT_HANDLING': """
How to use the context referenced above:
- Build upon the user's previous learning
- When referring to a concept previously covered, briefly remind the user of its core idea.
- Take care to not repeat concepts or ideas already covered.
- Introduce new concepts, relevant to the current topic, that build upon one or more of the previously learned concepts.
- Include references to previously learned concepts where relevant
- Continue the progressive learning structure
""",
    
    # Tone and style
    'TONE_STYLE': """
The tone should be clear, engaging, and accessible to someone new to the subject. If there are domain specific terms, define them. 
Include relevant links, whenever applicable, to allow the reader to explore the topic further.
""",
    
    # Context-aware tone
    'CONTEXT_TONE_STYLE': """
The tone should be clear, engaging, and accessible to someone new to the subject. Include at least 3-5 relevant links throughout the report. 
""",
    
    # System messages
    'SYSTEM_MESSAGES': {
        'REPORT_GENERATOR': "You are an expert educator and science communicator.",
        'CONTEXT_AWARE_GENERATOR': "You are an expert educator and science communicator who creates coherent, progressive learning experiences.",
        'SUMMARY_GENERATOR': "You are an expert educational content curator who creates coherent learning summaries.",
        'INITIAL_SUMMARY_GENERATOR': "You are an expert educational content curator who creates foundational learning summaries."
    },
    
    # Summary generation prompts
    'SUMMARY_TASK': """
Your task is to create a comprehensive summary that:
1. Integrates the new content seamlessly with existing learning
2. Maintains the narrative flow and learning progression
3. Highlights key concepts and connections between topics
4. Summarises all the concepts and ideas covered so far
5. Provides a coherent overview of the user's learning journey so far
6. Keeps the summary concise but comprehensive (aim for upto 1000 words)
""",
    
    'SUMMARY_FOCUS': """
Focus on:
- How the new topic fits into the broader learning plan
- Connections between previously learned concepts and the new topic
- The user's learning progression and depth of understanding
- Key insights and takeaways from the learning journey so far
""",
    
    'SUMMARY_TONE': """
Write the summary in a clear, educational tone that would help generate future reports that build upon this foundation.
""",
    
    'INITIAL_SUMMARY_TASK': """
Your task is to create an initial context summary that:
1. Establishes the foundation for the learning journey
2. Captures the key insights from the first report
3. Sets up the framework for future learning progression
4. Provides context for generating subsequent reports
5. Maintains a coherent narrative structure
""",
    
    'INITIAL_SUMMARY_REQUIREMENTS': """
The summary should:
- Introduce the main learning topic and its scope
- Highlight key concepts from the first report
- Establish the learning progression framework
- Set expectations for the learning journey ahead
- Be concise but comprehensive (aim for 1000 words)
""",
    
    'INITIAL_SUMMARY_TONE': """
Write in a clear, educational tone that will help generate future reports that build upon this foundation.
"""
} 