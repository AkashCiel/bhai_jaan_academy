# System Status Reports

This package handles automated Discord notifications for system status and daily reports.

## Features

- **Daily Reports**: Automated notifications after scheduled runs with success/failure metrics
- **Error Alerts**: Critical system failure notifications sent immediately
- **Discord Integration**: Rich formatted messages with embeds, colors, and structured data

## Setup

1. **Create Discord Webhook**:
   - Go to your Discord server settings → Integrations → Webhooks
   - Create a new webhook for a dedicated channel (e.g., #system-alerts)
   - Copy the webhook URL

2. **Configure Environment**:
   ```env
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-url
   ```

## Message Types

### Daily Report
- Sent after each scheduled run
- Shows users processed, success count, and any errors
- Color: Green (no errors) or Orange (with errors)

### Error Alert
- Sent immediately when critical failures occur
- Includes error type, details, and timestamp
- Color: Red

## Usage

```python
from services.notification_service import NotificationService

# Send daily report
notification_service = NotificationService()
notification_service.send_daily_report(15, 12, ["User A: API timeout", "User B: Email failed"])

# Send error alert
notification_service.send_error_alert("Database Connection Failed", "Unable to connect to PostgreSQL")
```

## Architecture

- **MessageBuilder**: Formats messages for Discord embeds
- **DiscordService**: Handles Discord webhook communication
- **NotificationService**: Unified interface for all notifications

## Future Extensions

Easy to add new message types by:
1. Adding new method to `MessageBuilder`
2. Adding corresponding method to `NotificationService`
3. Using the new notification type in your code
