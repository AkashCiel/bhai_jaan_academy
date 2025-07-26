from typing import List, Dict
import re

def extract_and_style_links(content: str) -> str:
    """
    Extract all URLs from content and convert them to styled links.
    Returns content with URLs replaced by styled <a> tags.
    """
    # Debug: Count URLs before processing
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls_found = re.findall(url_pattern, content)
    print(f"[DEBUG] Found {len(urls_found)} URLs: {urls_found}")
    
    # Replace URLs with styled links
    processed_content = re.sub(
        url_pattern, 
        r'<a href="\0" target="_blank" rel="noopener noreferrer" class="link-external">\0</a>', 
        content
    )
    
    # Debug: Count styled links after processing
    styled_links = re.findall(r'<a href="([^"]+)"[^>]*class="link-external"[^>]*>([^<]+)</a>', processed_content)
    print(f"[DEBUG] Created {len(styled_links)} styled links")
    
    return processed_content

def parse_ai_response_to_html(content):
    """
    Parse AI response with structural markers and convert to HTML
    """
    # Debug: Print original content to see what we're working with
    print(f"[DEBUG] Original content length: {len(content)}")
    print(f"[DEBUG] Content preview: {content[:200]}...")
    # Convert markdown-style headings to HTML
    content = re.sub(r'^## (.+):$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+):$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    
    # Convert bold text
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    
    # Convert bullet points
    content = re.sub(r'^- (.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
    
    # Convert section breaks
    content = re.sub(r'^---$', r'<hr>', content, flags=re.MULTILINE)
    
    # Extract and style all URLs in the content
    content = extract_and_style_links(content)
    
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
        f'<button class="w-full block py-3 px-4 mb-3 rounded bg-gray-200 text-gray-700 text-lg font-semibold shadow focus:outline-none cursor-not-allowed topic-button" aria-disabled="true">{t}</button>'
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
      <style>
        /* Background image from landing page */
        .plan-bg {{
          background-image: url('https://akashciel.github.io/bhai_jaan_academy/Bhai%20Jaan%20Academy.png');
          background-size: cover;
          background-position: center;
          background-repeat: no-repeat;
          background-attachment: fixed;
          min-height: 100vh;
        }}
        
        /* Foreground content with 60% opacity */
        .foreground-content {{
          background-color: rgba(255, 255, 255, 0.6) !important;
          backdrop-filter: blur(10px);
          border-radius: 12px;
          border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .topic-button {{
          transition: all 0.3s ease;
          border: 2px solid rgba(255, 255, 255, 0.3);
        }}
        
        .topic-button:hover {{
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        
        /* Mobile responsiveness */
        @media (max-width: 640px) {{
          .plan-bg {{
            background-image: url('https://akashciel.github.io/bhai_jaan_academy/Bhai%20Jaan%20Academy%20Mobile.png');
            background-attachment: scroll;
          }}
          
          .foreground-content {{
            margin: 1rem;
            padding: 1rem;
            border-radius: 8px;
          }}
          
          .mobile-header {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
          }}
          
          .mobile-subtitle {{
            font-size: 0.9rem;
            margin-bottom: 1rem;
          }}
        }}
        
        /* Desktop styles */
        @media (min-width: 641px) {{
          .foreground-content {{
            margin: 2rem auto;
            padding: 2rem;
            max-width: 800px;
          }}
        }}
      </style>
    </head>
    <body class=\"plan-bg text-gray-900 p-4 sm:p-6\">
      <div class=\"foreground-content\">
        <h1 class=\"text-2xl font-bold mb-4 mobile-header\">Learning Plan: {topic}</h1>
        <p class=\"mb-6 text-gray-700 mobile-subtitle\">User: {user_email}</p>
        <div class=\"flex flex-col gap-2\">
          {topics_html}
        </div>
        <footer class=\"mt-8 text-sm text-gray-600\">
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
                f'<a href="{report_links_int[idx]}" target="_blank" rel="noopener noreferrer" class="w-full block py-3 px-4 mb-3 rounded bg-gray-700 text-white text-lg font-semibold shadow hover:bg-gray-800 focus:outline-none transition-colors text-center topic-button">{t}</a>'
            )
        else:
            html_topics.append(
                f'<button class="w-full block py-3 px-4 mb-3 rounded bg-gray-200 text-gray-700 text-lg font-semibold shadow focus:outline-none cursor-not-allowed topic-button" aria-disabled="true">{t}</button>'
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
      <style>
        /* Background image from landing page */
        .plan-bg {{
          background-image: url('https://akashciel.github.io/bhai_jaan_academy/Bhai%20Jaan%20Academy.png');
          background-size: cover;
          background-position: center;
          background-repeat: no-repeat;
          background-attachment: fixed;
          min-height: 100vh;
        }}
        
        /* Foreground content with 60% opacity */
        .foreground-content {{
          background-color: rgba(255, 255, 255, 0.6) !important;
          backdrop-filter: blur(10px);
          border-radius: 12px;
          border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .topic-button {{
          transition: all 0.3s ease;
          border: 2px solid rgba(255, 255, 255, 0.3);
        }}
        
        .topic-button:hover {{
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        
        /* Mobile responsiveness */
        @media (max-width: 640px) {{
          .plan-bg {{
            background-image: url('https://akashciel.github.io/bhai_jaan_academy/Bhai%20Jaan%20Academy%20Mobile.png');
            background-attachment: scroll;
          }}
          
          .foreground-content {{
            margin: 1rem;
            padding: 1rem;
            border-radius: 8px;
          }}
          
          .mobile-header {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
          }}
          
          .mobile-subtitle {{
            font-size: 0.9rem;
            margin-bottom: 1rem;
          }}
        }}
        
        /* Desktop styles */
        @media (min-width: 641px) {{
          .foreground-content {{
            margin: 2rem auto;
            padding: 2rem;
            max-width: 800px;
          }}
        }}
      </style>
    </head>
    <body class=\"plan-bg text-gray-900 p-4 sm:p-6\">
      <div class=\"foreground-content\">
        <h1 class=\"text-2xl font-bold mb-4 mobile-header\">Learning Plan: {topic}</h1>
        <p class=\"mb-6 text-gray-700 mobile-subtitle\">User: {user_email}</p>
        <div class=\"flex flex-col gap-2\">
          {topics_html}
        </div>
        <footer class=\"mt-8 text-sm text-gray-600\">
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
      <!-- MathJax for mathematical formula rendering -->
      <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
      <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
      <script>
        window.MathJax = {{
          tex: {{
            inlineMath: [['$', '$'], ['\\(', '\\)']],
            displayMath: [['$$', '$$'], ['\\[', '\\]']],
            processEscapes: true,
            processEnvironments: true,
            packages: ['base', 'ams', 'noerrors', 'noundefined']
          }},
          options: {{
            skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
            ignoreHtmlClass: 'tex2jax_ignore',
            processHtmlClass: 'tex2jax_process'
          }},
          startup: {{
            pageReady: () => {{
              return MathJax.startup.defaultPageReady().then(() => {{
                console.log('MathJax processing completed');
              }});
            }}
          }}
        }};
      </script>
      <style>
        /* Background image from landing page */
        .report-bg {{
          background-image: url('https://akashciel.github.io/bhai_jaan_academy/Bhai%20Jaan%20Academy.png');
          background-size: cover;
          background-position: center;
          background-repeat: no-repeat;
          background-attachment: fixed;
          min-height: 100vh;
        }}
        
        /* Foreground content with 60% opacity */
        .foreground-content {{
          background-color: rgba(255, 255, 255, 0.6) !important;
          backdrop-filter: blur(10px);
          border-radius: 12px;
          border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .report-content h2 {{ 
          margin-top: 2rem; 
          margin-bottom: 1rem; 
          font-size: 1.5rem; 
          font-weight: bold; 
          color: #1f2937;
          border-bottom: 2px solid rgba(229, 231, 235, 0.8);
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
          color: #1f2937;
          font-weight: 500;
        }}
        .report-content ul {{ 
          margin-bottom: 1rem; 
          padding-left: 1.5rem; 
        }}
        .report-content li {{ 
          margin-bottom: 0.5rem; 
          color: #1f2937;
          font-weight: 500;
        }}
        .report-content hr {{ 
          margin: 2rem 0; 
          border: none; 
          border-top: 1px solid rgba(229, 231, 235, 0.8); 
        }}
        .report-content strong {{ 
          color: #111827; 
          font-weight: 700; 
        }}
        .report-content .link-external {{ 
          background: linear-gradient(135deg, #dc2626, #b91c1c);
          color: white;
          border: 2px solid #dc2626;
          border-radius: 8px;
          padding: 0.75rem 1rem;
          text-decoration: none;
          font-weight: 700;
          transition: all 0.3s ease;
          display: inline-block;
          margin: 0.75rem 0.25rem;
          box-shadow: 0 4px 6px rgba(220, 38, 38, 0.3);
          position: relative;
          overflow: hidden;
        }}
        .report-content .link-external:hover {{ 
          transform: translateY(-3px);
          box-shadow: 0 6px 12px rgba(220, 38, 38, 0.4);
          background: linear-gradient(135deg, #b91c1c, #991b1b);
        }}
        .report-content .link-external:before {{
          content: "🔗 ";
          margin-right: 0.5rem;
          font-size: 1.2em;
        }}
        
        /* Mobile responsiveness */
        @media (max-width: 640px) {{
          .report-bg {{
            background-image: url('https://akashciel.github.io/bhai_jaan_academy/Bhai%20Jaan%20Academy%20Mobile.png');
            background-attachment: scroll;
          }}
          
          .foreground-content {{
            margin: 1rem;
            padding: 1rem;
            border-radius: 8px;
          }}
          
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
            padding: 0.4rem 0.6rem;
          }}
          
          .mobile-header {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
          }}
          
          .mobile-subtitle {{
            font-size: 0.9rem;
            margin-bottom: 1rem;
          }}
        }}
        
        /* Desktop styles */
        @media (min-width: 641px) {{
          .foreground-content {{
            margin: 2rem auto;
            padding: 2rem;
            max-width: 800px;
          }}
        }}
      </style>
    </head>
    <body class="report-bg text-gray-900 p-4 sm:p-6">
      <div class="foreground-content">
        <h1 class="text-2xl font-bold mb-4 mobile-header">{topic}</h1>
        <p class="mb-6 text-gray-700 mobile-subtitle">Prepared for: {user_email}</p>
        <article class="report-content prose prose-lg tex2jax_process">
          {parsed_content}
        </article>
        <footer class="mt-8 text-sm text-gray-600">
          <p>Bhai Jaan Academy &copy; 2024</p>
        </footer>
      </div>
      
      <!-- Ensure MathJax processes the content -->
      <script>
        // Wait for MathJax to load and process
        window.addEventListener('load', function() {{
          if (window.MathJax) {{
            MathJax.typesetPromise().then(() => {{
              console.log('MathJax typesetting completed');
            }}).catch((err) => {{
              console.error('MathJax typesetting error:', err);
            }});
          }}
        }});
      </script>
    </body>
    </html>
    """ 