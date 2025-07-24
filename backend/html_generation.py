from typing import List, Dict

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
    report_links: Dict[int, str]
) -> str:
    """
    Updates the homepage/learning plan HTML to include wide, clickable buttons for topics with report links, and non-clickable buttons otherwise.
    """
    html_topics = []
    for idx, t in enumerate(topics):
        if idx in report_links and report_links[idx]:
            html_topics.append(
                f'<a href="{report_links[idx]}" target="_blank" rel="noopener noreferrer" class="w-full block py-3 px-4 mb-3 rounded bg-gray-700 text-white text-lg font-semibold shadow hover:bg-gray-800 focus:outline-none transition-colors text-center">{t}</a>'
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

if __name__ == "__main__":
    # Dummy data
    topic = "Machine Learning"
    user_email = "test@example.com"
    topics = [
        "Introduction to ML",
        "Supervised Learning",
        "Unsupervised Learning",
        "Neural Networks",
        "Model Evaluation"
    ]
    report_links = {
        1: "https://example.com/reports/supervised-learning.html",
        3: "https://example.com/reports/neural-networks.html"
    }

    print("\n--- generate_learning_plan_html (no links) ---\n")
    print(generate_learning_plan_html(topic, user_email, topics))

    print("\n--- update_learning_plan_html (with links) ---\n")
    print(update_learning_plan_html(topic, user_email, topics, report_links)) 