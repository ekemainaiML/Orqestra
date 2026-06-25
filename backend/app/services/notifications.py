import logging
from email.message import EmailMessage

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self, host: str, port: int, username: str, password: str,
                 from_address: str, use_tls: bool = True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_address = from_address
        self.use_tls = use_tls

    async def send(self, to: str, subject: str, body: str) -> bool:
        try:
            import aiosmtplib
            msg = EmailMessage()
            msg["From"] = self.from_address
            msg["To"] = to
            msg["Subject"] = subject
            msg.set_content(body)
            await aiosmtplib.send(
                msg,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                start_tls=self.use_tls,
            )
            logger.info("Email sent to %s: %s", to, subject)
            return True
        except Exception as e:
            logger.warning("Failed to send email to %s: %s", to, e)
            return False


class SlackNotifier:
    def __init__(self, webhook_url: str | None = None):
        self.webhook_url = webhook_url

    async def send(self, message: str, webhook_url: str | None = None) -> bool:
        url = webhook_url or self.webhook_url
        if not url:
            logger.debug("No Slack webhook URL configured, skipping notification")
            return False
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json={"text": message})
                resp.raise_for_status()
            logger.info("Slack notification sent")
            return True
        except Exception as e:
            logger.warning("Failed to send Slack notification: %s", e)
            return False


EVENT_LABELS: dict[str, str] = {
    "case_created": "New Case",
    "case_escalated": "Case Escalated",
    "case_completed": "Case Completed",
    "case_rejected": "Case Rejected",
    "approval_pending": "Approval Required",
    "case_failed": "Case Failed",
    "challenge_issued": "Challenge Issued",
}

SLACK_COLORS: dict[str, str] = {
    "case_escalated": "#E74C3C",
    "case_rejected": "#E74C3C",
    "case_failed": "#E74C3C",
    "case_completed": "#2ECC71",
    "approval_pending": "#F39C12",
    "challenge_issued": "#9B59B6",
}


def _format_slack_message(event_type: str, case_id: str, actor: str,
                          summary: str, tenant_slug: str | None = None) -> str:
    label = EVENT_LABELS.get(event_type, event_type.replace("_", " ").title())
    color = SLACK_COLORS.get(event_type, "#3498DB")
    tenant_info = f" [*{tenant_slug}*]" if tenant_slug else ""
    return (
        f"{{\"attachments\": [{{"
        f"\"color\": \"{color}\","
        f"\"title\": \"{label}\","
        f"\"text\": \"*Case:* `{case_id}`\\n*Actor:* {actor}\\n*Summary:* {summary}{tenant_info}\""
        f"}}]}}"
    )


class NotificationService:
    def __init__(self, smtp_config: dict | None = None,
                 slack_webhook: str | None = None):
        self.email: EmailSender | None = None
        if smtp_config and smtp_config.get("host"):
            self.email = EmailSender(**smtp_config)
        self.slack = SlackNotifier(slack_webhook)

    async def notify(self, event_type: str, case_id: str, actor: str,
                     summary: str, recipient_email: str | None = None,
                     slack_webhook: str | None = None,
                     tenant_slug: str | None = None) -> None:
        slack_message = _format_slack_message(event_type, case_id, actor, summary, tenant_slug)
        slack_ok = await self.slack.send(slack_message, slack_webhook)

        email_ok = False
        if recipient_email and self.email:
            label = EVENT_LABELS.get(event_type, event_type.replace("_", " ").title())
            body = (
                f"Case: {case_id}\n"
                f"Event: {label}\n"
                f"Actor: {actor}\n"
                f"Summary: {summary}\n"
                f"Tenant: {tenant_slug or 'default'}\n"
            )
            email_ok = await self.email.send(
                recipient_email,
                f"[Orqestra] {label} — {case_id}",
                body,
            )

        if slack_ok or email_ok:
            logger.info("Notification sent for %s (case=%s)", event_type, case_id)


_global_notifier: NotificationService | None = None


async def _load_db_settings() -> dict:
    from sqlalchemy import select

    from app.models.notification_config import NotificationConfig
    from app.services.database import get_async_session
    try:
        async with get_async_session()() as session:
            cfg = await session.scalar(select(NotificationConfig).limit(1))
            if cfg:
                return {
                    "host": cfg.smtp_host,
                    "port": cfg.smtp_port,
                    "username": cfg.smtp_username,
                    "password": cfg.smtp_password,
                    "from_address": cfg.smtp_from,
                    "slack_webhook_url": cfg.slack_webhook_url,
                }
    except Exception:
        pass
    return {}


def get_notifier() -> NotificationService:
    global _global_notifier
    if _global_notifier is None:
        from app.services.settings import settings
        smtp = {}
        host = settings.smtp_host
        pw = settings.smtp_password
        slack_url = settings.slack_webhook_url
        if host:
            smtp = {
                "host": host,
                "port": settings.smtp_port,
                "username": settings.smtp_username,
                "password": pw,
                "from_address": settings.smtp_from,
            }
        _global_notifier = NotificationService(
            smtp_config=smtp,
            slack_webhook=slack_url,
        )
    return _global_notifier


NOTIFIABLE_EVENTS = {
    "case_escalated",
    "case_completed",
    "case_rejected",
    "case_failed",
    "approval_pending",
    "challenge_issued",
}


def should_notify(event_type: str) -> bool:
    return event_type in NOTIFIABLE_EVENTS
