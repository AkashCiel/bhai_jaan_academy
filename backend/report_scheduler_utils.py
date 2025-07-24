import os
import json
import datetime
import traceback
import openai
import markdown
import requests
from html_generation import update_learning_plan_html, generate_topic_report_html
from report_uploads.github_report_uploader import upload_report

def load_users(users_file):
    with open(users_file, "r") as f:
        return json.load(f)

def save_users(users, users_file):
    with open(users_file, "w") as f:
        json.dump(users, f, indent=2)

def is_same_utc_day(dt1, dt2):
    return dt1.date() == dt2.date()

def get_next_report_topic(user):
    idx = user.get("current_index", 0)
    topics = user.get("learning_plan", [])
    if idx < len(topics):
        return idx, topics[idx]
    return None, None

def generate_report_content(topic, openai_client):
    prompt = f"""Write a comprehensive, beginner-friendly educational report on the topic: \"{topic}\".\nThe report should include:\n- An introduction to the topic\n- Key concepts and definitions\n- Real-world applications or examples\n- Common misconceptions or pitfalls\n- Further reading/resources (if appropriate)\nThe tone should be clear, engaging, and accessible to someone new to the subject."""
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert educator and science communicator."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1800,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def send_report_email(user, plan_url, report_url, topic, mailgun_api_key, mailgun_domain):
    if not mailgun_api_key or not mailgun_domain:
        print(f"[Scheduler] Email service not configured. Skipping email for {user['email']}")
        return
    subject = f"Your new learning report on {topic} is ready! - Bhai Jaan Academy"
    html_email_content = f"""
    <html>
    <body>
        <h2>Your new report is ready! 🎓</h2>
        <p>Hi {user['email']},</p>
        <p>Your next learning report on <strong>{topic}</strong> is now available.</p>
        <ul>
            <li><a href='{plan_url}'>View your full learning plan</a></li>
            <li><a href='{report_url}'>Read your new report: {topic}</a></li>
        </ul>
        <br>
        <p>Keep up the great work!</p>
        <p>— The Bhai Jaan Academy Team</p>
    </body>
    </html>
    """
    response = requests.post(
        f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
        auth=("api", mailgun_api_key),
        data={
            "from": f"Bhai Jaan Academy <mailgun@{mailgun_domain}>",
            "to": [user["email"]],
            "subject": subject,
            "html": html_email_content
        }
    )
    print(f"[Scheduler] Email sent to {user['email']}: {response.status_code}")

def process_user(user, openai_client, mailgun_api_key, mailgun_domain, users_file):
    now = datetime.datetime.now(datetime.timezone.utc)
    last_report_time = user.get("last_report_time")
    current_index = user.get("current_index", 0)
    # If current_index == 1 and last_report_time is today, skip
    if last_report_time:
        try:
            last_dt = datetime.datetime.fromisoformat(last_report_time)
        except Exception:
            last_dt = None
    else:
        last_dt = None
    if current_index == 1 and last_dt and is_same_utc_day(now, last_dt):
        print(f"[Scheduler] Skipping {user['email']} (already sent today)")
        return user  # No changes
    idx, topic = get_next_report_topic(user)
    if topic is None:
        print(f"[Scheduler] No more topics for {user['email']}")
        return user
    print(f"[Scheduler] Generating report for {user['email']} on topic: {topic}")
    try:
        report_content_md = generate_report_content(topic, openai_client)
        report_content_html = markdown.markdown(report_content_md)
        report_html = generate_topic_report_html(topic, user["email"], report_content_html)
        # Upload report
        plan_topic = user["main_topic"]
        report_url = upload_report(user["email"], plan_topic, report_html, filename=topic)
        # Update report_links
        report_links = {int(k): v for k, v in user.get("report_links", {}).items()}
        report_links[idx] = report_url
        # Update learning plan HTML
        print(f"[DEBUG] current_index={idx}, report_links={report_links}, should_have_links={idx in report_links}")
        updated_plan_html = update_learning_plan_html(
            topic=plan_topic,
            user_email=user["email"],
            topics=user["learning_plan"],
            report_links=report_links
        )
        plan_url = upload_report(user["email"], plan_topic, updated_plan_html)
        # Update user progress
        user["current_index"] = current_index + 1
        user["last_report_time"] = now.isoformat()
        user["plan_url"] = plan_url
        user["report_links"] = report_links
        # Add delay before sending email
        import time
        time.sleep(300)
        # Send email
        send_report_email(user, plan_url, report_url, topic, mailgun_api_key, mailgun_domain)
        print(f"[Scheduler] Report and email sent for {user['email']} on topic: {topic}")
    except Exception as e:
        print(f"[Scheduler] Error for {user['email']} on topic {topic}: {e}")
        traceback.print_exc()
    return user 