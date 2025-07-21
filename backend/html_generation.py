from typing import List, Dict

def generate_learning_plan_html(
    topic: str,
    user_email: str,
    topics: List[str]
) -> str:
    """
    Generates the initial learning plan HTML with a list of topics (no report links).
    """
    html_topics = [f'<li class="mb-2 text-gray-700">{t}</li>' for t in topics]
    topics_html = "\n".join(html_topics)
    return f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
      <meta charset=\"UTF-8\">
      <title>Learning Plan for {topic}</title>
      <link href=\"https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css\" rel=\"stylesheet\">
    </head>
    <body class=\"bg-gray-50 text-gray-900 p-6\">
      <div class=\"max-w-2xl mx-auto bg-white rounded shadow p-8\">
        <h1 class=\"text-2xl font-bold mb-4\">Learning Plan: {topic}</h1>
        <p class=\"mb-6 text-gray-600\">User: {user_email}</p>
        <ol class=\"list-decimal pl-6\">
          {topics_html}
        </ol>
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
    report_links: Dict[int, str]
) -> str:
    """
    Updates the homepage/learning plan HTML to include links to reports where available.
    """
    html_topics = []
    for idx, t in enumerate(topics):
        if idx in report_links and report_links[idx]:
            html_topics.append(f'<li class="mb-2"><a href="{report_links[idx]}" class="text-blue-600 underline">{t}</a></li>')
        else:
            html_topics.append(f'<li class="mb-2 text-gray-700">{t}</li>')
    topics_html = "\n".join(html_topics)
    return f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
      <meta charset=\"UTF-8\">
      <title>Learning Plan for {topic}</title>
      <link href=\"https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css\" rel=\"stylesheet\">
    </head>
    <body class=\"bg-gray-50 text-gray-900 p-6\">
      <div class=\"max-w-2xl mx-auto bg-white rounded shadow p-8\">
        <h1 class=\"text-2xl font-bold mb-4\">Learning Plan: {topic}</h1>
        <p class=\"mb-6 text-gray-600\">User: {user_email}</p>
        <ol class=\"list-decimal pl-6\">
          {topics_html}
        </ol>
        <footer class=\"mt-8 text-sm text-gray-500\">
          <p>Bhai Jaan Academy &copy; 2024</p>
        </footer>
      </div>
    </body>
    </html>
    """ 