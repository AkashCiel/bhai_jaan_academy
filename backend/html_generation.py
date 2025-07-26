from typing import List, Dict
import re

def parse_ai_response_to_html(content):
    """
    Parse AI response with structural markers and convert to HTML
    """
    # Convert markdown-style headings to HTML
    content = re.sub(r'^## (.+):$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+):$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    
    # Convert bold text
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    
    # Convert bullet points
    content = re.sub(r'^- (.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
    
    # Convert section breaks
    content = re.sub(r'^---$', r'<hr>', content, flags=re.MULTILINE)
    
    # Convert links (format: **Link: [text](url)**)
    content = re.sub(r'\*\*Link: \[([^\]]+)\]\(([^)]+)\)\*\*', r'<a href="\2" target="_blank" rel="noopener noreferrer" class="link-external">\1</a>', content)
    
    # Also handle regular markdown links [text](url) that might appear
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener noreferrer" class="link-external">\1</a>', content)
    
    # Handle bare URLs and convert them to links
    content = re.sub(r'(?<!["\'])(https?://[^\s<>"{}|\\^`\[\]]+)(?!["\'])', r'<a href="\1" target="_blank" rel="noopener noreferrer" class="link-external">\1</a>', content)
    
    # Wrap consecutive <li> elements in <ul> tags
    lines = content.split('\n')
    processed_lines = []
    in_list = False
    
    for line in lines:
        if line.strip().startswith('<li>'):
            if not in_list:
                processed_lines.append('<ul>')
                in_list = True
            processed_lines.append(line)
        else:
            if in_list:
                processed_lines.append('</ul>')
                in_list = False
            processed_lines.append(line)
    
    # Close any open list
    if in_list:
        processed_lines.append('</ul>')
    
    content = '\n'.join(processed_lines)
    
    # Wrap non-HTML lines in <p> tags
    lines = content.split('\n')
    final_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if not (line.startswith('<h') or line.startswith('<li>') or line.startswith('<ul>') or 
                line.startswith('</ul>') or line.startswith('<hr>') or line.startswith('<a')):
            final_lines.append(f'<p>{line}</p>')
        else:
            final_lines.append(line)
    
    return '\n'.join(final_lines)

def generate_learning_plan_html(
    topic: str,
    user_email: str,
    topics: List[str]
) -> str:
    """
    Generates the initial learning plan HTML with a list of topics as wide, non-clickable buttons (no report links).
    """
    html_topics = [
        f'<button class="w-full block py-3 px-4 mb-3 rounded bg-gray-200 text-gray-700 text-lg font-semibold shadow focus:outline-none cursor-not-allowed" aria-disabled="true">{t}</button>'
        for t in topics
    ]
    topics_html = "\n".join(html_topics)
    return f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
      <meta charset=\"UTF-8\">
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
      <title>Learning Plan for {topic}</title>
      <link href=\"https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css\" rel=\"stylesheet\">
    </head>
    <body class=\"bg-gray-50 text-gray-900 p-4 sm:p-6\">
      <div class=\"max-w-2xl w-full mx-auto bg-white rounded shadow p-4 sm:p-8\">
        <h1 class=\"text-2xl font-bold mb-4\">Learning Plan: {topic}</h1>
        <p class=\"mb-6 text-gray-600\">User: {user_email}</p>
        <div class=\"flex flex-col gap-2\">
          {topics_html}
        </div>
        <footer class=\"mt-8 text-sm text-gray-500\">
          <p>Bhai Jaan Academy &copy; 2024</p>
        </footer>
      </div>
    </body>
    </html>
    """

def update_learning_plan_html(
    topic: str,
    user_email: str,
    topics: List[str],
    report_links: Dict[str, str]
) -> str:
    """
    Updates the homepage/learning plan HTML to include wide, clickable buttons for topics with report links, and non-clickable buttons otherwise.
    """
    # Convert keys to int for internal use
    report_links_int = {int(k): v for k, v in report_links.items()}
    html_topics = []
    for idx, t in enumerate(topics):
        if idx in report_links_int and report_links_int[idx]:
            html_topics.append(
                f'<a href="{report_links_int[idx]}" target="_blank" rel="noopener noreferrer" class="w-full block py-3 px-4 mb-3 rounded bg-gray-700 text-white text-lg font-semibold shadow hover:bg-gray-800 focus:outline-none transition-colors text-center">{t}</a>'
            )
        else:
            html_topics.append(
                f'<button class="w-full block py-3 px-4 mb-3 rounded bg-gray-200 text-gray-700 text-lg font-semibold shadow focus:outline-none cursor-not-allowed" aria-disabled="true">{t}</button>'
            )
    topics_html = "\n".join(html_topics)
    return f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
      <meta charset=\"UTF-8\">
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
      <title>Learning Plan for {topic}</title>
      <link href=\"https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css\" rel=\"stylesheet\">
    </head>
    <body class=\"bg-gray-50 text-gray-900 p-4 sm:p-6\">
      <div class=\"max-w-2xl w-full mx-auto bg-white rounded shadow p-4 sm:p-8\">
        <h1 class=\"text-2xl font-bold mb-4\">Learning Plan: {topic}</h1>
        <p class=\"mb-6 text-gray-600\">User: {user_email}</p>
        <div class=\"flex flex-col gap-2\">
          {topics_html}
        </div>
        <footer class=\"mt-8 text-sm text-gray-500\">
          <p>Bhai Jaan Academy &copy; 2024</p>
        </footer>
      </div>
    </body>
    </html>
    """

def generate_topic_report_html(
    topic: str,
    user_email: str,
    report_content: str
) -> str:
    """
    Generates a well-structured HTML report for a topic using Tailwind CSS.
    """
    # Parse the AI response to convert structural markers to HTML
    parsed_content = parse_ai_response_to_html(report_content)
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Report: {topic}</title>
      <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
      <style>
        .report-content h2 {{ 
          margin-top: 2rem; 
          margin-bottom: 1rem; 
          font-size: 1.5rem; 
          font-weight: bold; 
          color: #1f2937;
          border-bottom: 2px solid #e5e7eb;
          padding-bottom: 0.5rem;
        }}
        .report-content h3 {{ 
          margin-top: 1.5rem; 
          margin-bottom: 0.75rem; 
          font-size: 1.25rem; 
          font-weight: bold; 
          color: #374151;
        }}
        .report-content p {{ 
          margin-bottom: 1rem; 
          line-height: 1.6; 
          color: #4b5563;
        }}
        .report-content ul {{ 
          margin-bottom: 1rem; 
          padding-left: 1.5rem; 
        }}
        .report-content li {{ 
          margin-bottom: 0.5rem; 
          color: #4b5563;
        }}
        .report-content hr {{ 
          margin: 2rem 0; 
          border: none; 
          border-top: 1px solid #e5e7eb; 
        }}
        .report-content strong {{ 
          color: #1f2937; 
          font-weight: 600; 
        }}
        .report-content .link-external {{ 
          color: #dc2626; 
          background-color: #fef2f2;
          border: 2px solid #fecaca;
          border-radius: 6px;
          padding: 0.5rem 0.75rem;
          text-decoration: none;
          font-weight: 600;
          transition: all 0.3s ease;
          display: inline-block;
          margin: 0.5rem 0.25rem;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .report-content .link-external:hover {{ 
          color: #991b1b; 
          background-color: #fee2e2;
          border-color: #fca5a5;
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        .report-content .link-external:before {{
          content: "🔗 ";
          margin-right: 0.5rem;
          font-size: 1.1em;
        }}
        
        /* Mobile responsiveness */
        @media (max-width: 640px) {{
          .report-content h2 {{
            font-size: 1.25rem;
            margin-top: 1.5rem;
          }}
          .report-content h3 {{
            font-size: 1.1rem;
            margin-top: 1rem;
          }}
          .report-content p {{
            font-size: 0.95rem;
            line-height: 1.5;
          }}
          .report-content ul {{
            padding-left: 1rem;
          }}
          .report-content li {{
            font-size: 0.95rem;
          }}
          .report-content .link-external {{
            font-size: 0.9rem;
            word-break: break-word;
          }}
        }}
      </style>
    </head>
    <body class="bg-gray-50 text-gray-900 p-4 sm:p-6">
      <div class="max-w-2xl w-full mx-auto bg-white rounded shadow p-4 sm:p-8">
        <h1 class="text-2xl font-bold mb-4">{topic}</h1>
        <p class="mb-6 text-gray-600">Prepared for: {user_email}</p>
        <article class="report-content prose prose-lg">
          {parsed_content}
        </article>
        <footer class="mt-8 text-sm text-gray-500">
          <p>Bhai Jaan Academy &copy; 2024</p>
        </footer>
      </div>
    </body>
    </html>
    """ 