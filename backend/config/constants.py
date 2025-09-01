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

# Payment configuration
PAYMENT_CONFIG = {
    'AMOUNT': '1.99',
    'CURRENCY': 'EUR',
    'DESCRIPTION': 'Bhai Jaan Academy Learning Plan',
    'MODE': 'live'  # 'sandbox' for testing, 'live' for production
}

# Feedback configuration
FEEDBACK_CONFIG = {
    'DISCORD_CHANNEL_URL': 'https://discord.gg/fcazNe43',
    'FEEDBACK_EMAIL': 'laughing.buddha.lab@gmail.com',
    'FEEDBACK_EMAIL_SUBJECT': 'How to make Bhai Jaan Academy better?'
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

# Discord configuration
DISCORD_CONFIG = {
    'WEBHOOK_URL': 'DISCORD_WEBHOOK_URL'  # Will be set via environment variable
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
- An interactive quiz at the end to test understanding of key concepts (see QUIZ_GENERATION instructions)
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
        'REPORT_GENERATOR': "You are an expert educator and science communicator who creates engaging, interactive learning experiences.",
        'CONTEXT_AWARE_GENERATOR': "You are an expert educator and science communicator who creates coherent, progressive learning experiences with interactive assessment.",
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
""",
    
    # Content expansion guidelines
    'CONTENT_EXPANSION': """
IMPORTANT: The report should be comprehensive and detailed:
- Aim for 5,000-8,000 words of content
- Provide extensive coverage of each concept
- Include detailed explanations and multiple perspectives
- Offer comprehensive real-world applications
- Include both theoretical foundations and practical implications
- Address both current state and future directions
""",
    
    # Advanced content requirements
    'ADVANCED_CONTENT': """
The report should also include:
- Advanced applications and current research frontiers
- Emerging technologies and future implications
- Cutting-edge developments in the field
- Research challenges and opportunities
- Industry trends and market dynamics
- Equal emphasis on both research frontiers and practical applications
""",
    
    # Enhanced concept coverage
    'ENHANCED_CONCEPTS': """
For each concept covered:
- Provide multiple examples and use cases
- Include step-by-step explanations where applicable
- Offer different perspectives and approaches
- Show practical implementation considerations
- Address common misconceptions and clarifications
""",
    
    # Analogies and metaphors
    'ANALOGIES_METAPHORS': """
Enhance understanding through:
- Multiple real-world analogies for each concept
- Creative metaphors that make abstract ideas concrete
- Historical anecdotes and famous examples
- Everyday scenarios that illustrate the concepts
- Visual and sensory analogies where helpful
""",
    
    # Concept connections
    'CONCEPT_CONNECTIONS': """
Emphasize connections by:
- Explicitly linking each concept to previously learned topics
- Showing how concepts build upon each other
- Highlighting interdisciplinary connections
- Demonstrating the progression of understanding
- Creating a coherent narrative thread throughout
""",
    
    # Interactive elements
    'INTERACTIVE_ELEMENTS': """
Include interactive elements for key concepts:
- "Think About This" sections with thought-provoking questions
- "Practice Problems" with detailed solutions
- "Common Misconceptions" sections with clarifications
- "Further Exploration" prompts for deeper learning
- "Self-Assessment" questions for key concepts
- "Key Takeaways" summaries at the end of each section
- A comprehensive quiz at the end to test understanding (see QUIZ_GENERATION instructions)
""",
    
    # Learning journey integration
    'LEARNING_JOURNEY_INTEGRATION': """
Integrate the learning journey by:
- Explicitly referencing the most relevant previously covered topics
- Showing how current topic fits into the broader learning plan
- Creating bridges between past and present concepts
- Maintaining the narrative flow of the user's learning progression
- Highlighting the user's growing expertise and understanding
""",

    # Quiz generation prompts
    'QUIZ_GENERATION': """
IMPORTANT: At the end of every report, generate an interactive quiz that tests the user's understanding of the key concepts covered.

QUIZ REQUIREMENTS:
- Create exactly FIVE quiz questions per report
- Each question should test understanding of different key concepts from the report
- Provide exactly 4 multiple-choice options (A, B, C, D) for each question
- Include detailed explanations for why each option is correct or incorrect
- Ensure the correct answer is clearly marked for each question
- Make questions appropriate for the user's current learning level
- IMPORTANT: Distribute correct answers randomly across A, B, C, D positions
- Avoid patterns - do not put the correct answer in the same position for multiple questions

QUIZ FORMAT:
Use this exact structure at the end of your report:

## Interactive Quiz: Test Your Understanding

**Question 1:** [Write a clear, specific question about the first key concept]

**Options:**
A) [First option text]
B) [Second option text] 
C) [Third option text]
D) [Fourth option text]

**Correct Answer:** [Letter of correct option]

**Explanations:**
- **Option A:** [Explain why this is correct or incorrect, with specific details from the report]
- **Option B:** [Explain why this is correct or incorrect, with specific details from the report]
- **Option C:** [Explain why this is correct or incorrect, with specific details from the report]
- **Option D:** [Explain why this is correct or incorrect, with specific details from the report]

**Question 2:** [Write a clear, specific question about the second key concept]

**Options:**
A) [First option text]
B) [Second option text] 
C) [Third option text]
D) [Fourth option text]

**Correct Answer:** [Letter of correct option]

**Explanations:**
- **Option A:** [Explain why this is correct or incorrect, with specific details from the report]
- **Option B:** [Explain why this is correct or incorrect, with specific details from the report]
- **Option C:** [Explain why this is correct or incorrect, with specific details from the report]
- **Option D:** [Explain why this is correct or incorrect, with specific details from the report]

**Question 3:** [Write a clear, specific question about the third key concept]

**Options:**
A) [First option text]
B) [Second option text] 
C) [Third option text]
D) [Fourth option text]

**Correct Answer:** [Letter of correct option]

**Explanations:**
- **Option A:** [Explain why this is correct or incorrect, with specific details from the report]
- **Option B:** [Explain why this is correct or incorrect, with specific details from the report]
- **Option C:** [Explain why this is correct or incorrect, with specific details from the report]
- **Option D:** [Explain why this is correct or incorrect, with specific details from the report]

**Question 4:** [Write a clear, specific question about the fourth key concept]

**Options:**
A) [First option text]
B) [Second option text] 
C) [Third option text]
D) [Fourth option text]

**Correct Answer:** [Letter of correct option]

**Explanations:**
- **Option A:** [Explain why this is correct or incorrect, with specific details from the report]
- **Option B:** [Explain why this is correct or incorrect, with specific details from the report]
- **Option C:** [Explain why this is correct or incorrect, with specific details from the report]
- **Option D:** [Explain why this is correct or incorrect, with specific details from the report]

**Question 5:** [Write a clear, specific question about the fifth key concept]

**Options:**
A) [First option text]
B) [Second option text] 
C) [Third option text]
D) [Fourth option text]

**Correct Answer:** [Letter of correct option]

**Explanations:**
- **Option A:** [Explain why this is correct or incorrect, with specific details from the report]
- **Option B:** [Explain why this is correct or incorrect, with specific details from the report]
- **Option C:** [Explain why this is correct or incorrect, with specific details from the report]
- **Option D:** [Explain why this is correct or incorrect, with specific details from the report]

**Why This Matters:** [Brief explanation of why understanding these concepts is important for the user's learning journey]
""",

    'QUIZ_CONTENT_GUIDELINES': """
QUIZ CONTENT GUIDELINES:
- Questions should test conceptual understanding, not just memorization
- All options should be plausible but clearly distinguishable
- Explanations should reference specific content from the report
- Difficulty should match the user's current learning stage
- Questions should encourage critical thinking about the material
- Avoid "trick questions" - focus on genuine learning assessment
- Ensure explanations are educational and help reinforce learning
""",

    'QUIZ_INTEGRATION': """
QUIZ INTEGRATION INSTRUCTIONS:
- Place the quiz at the very end of the report, after all content
- The quiz should feel like a natural conclusion to the learning material
- Use the quiz to reinforce key takeaways from the report
- Ensure each question connects directly to different main concepts covered
- Make the quiz engaging and motivating for continued learning
- Present all 5 questions together for comprehensive assessment
"""
}