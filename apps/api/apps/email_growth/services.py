from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.text import slugify

from apps.email_growth.models import EmailCampaign, EmailSendLog, NewsletterSubscriber

logger = logging.getLogger("toolverse.email_growth")


def subscribe_newsletter(email: str, *, locale: str = "en", source: str = "web") -> NewsletterSubscriber:
    email = email.strip().lower()
    sub, created = NewsletterSubscriber.objects.get_or_create(
        email=email,
        defaults={"locale": locale[:10], "source": source[:64], "is_active": True},
    )
    if not created and not sub.is_active:
        sub.is_active = True
        sub.unsubscribed_at = None
        sub.locale = locale[:10]
        sub.save(update_fields=["is_active", "unsubscribed_at", "locale", "updated_at"])
    return sub


def _smtp_configured() -> bool:
    return bool(getattr(settings, "EMAIL_HOST", "") or "")


def send_campaign_test(campaign: EmailCampaign, to_email: str) -> EmailSendLog:
    subject = f"[TEST] {campaign.subject}"
    body = campaign.body_text or campaign.body_html or campaign.subject
    log = EmailSendLog.objects.create(
        campaign=campaign,
        email=to_email,
        status=EmailSendLog.Status.QUEUED,
        meta={"test": True},
    )
    if not _smtp_configured():
        logger.info("SMTP not configured; test send logged only to=%s campaign=%s", to_email, campaign.slug)
        log.status = EmailSendLog.Status.SKIPPED
        log.meta = {**log.meta, "reason": "no_smtp"}
        log.save(update_fields=["status", "meta"])
        return log
    try:
        send_mail(
            subject,
            body,
            getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@toolverse.ai"),
            [to_email],
            fail_silently=False,
            html_message=campaign.body_html or None,
        )
        log.status = EmailSendLog.Status.SENT
        log.save(update_fields=["status"])
    except Exception as exc:  # noqa: BLE001
        log.status = EmailSendLog.Status.FAILED
        log.error = str(exc)[:2000]
        log.save(update_fields=["status", "error"])
    return log


def send_weekly_digest() -> dict[str, Any]:
    """
    Weekly digest to active subscribers. No-ops with logging when SMTP is absent.
    """
    subscribers = list(NewsletterSubscriber.objects.filter(is_active=True)[:5000])
    subject = "ToolVerse Weekly Digest"
    body_text = (
        "Here is your weekly ToolVerse AI digest: new tools, guides, and tips.\n"
        "Visit https://toolverse.ai to explore.\n"
    )
    campaign, _ = EmailCampaign.objects.get_or_create(
        slug=slugify(f"weekly-digest-{timezone.now().date()}")[:120],
        defaults={
            "subject": subject,
            "body_text": body_text,
            "body_html": f"<p>{body_text.replace(chr(10), '<br/>')}</p>",
            "status": EmailCampaign.Status.SENDING,
        },
    )

    if not _smtp_configured():
        logger.info(
            "send_weekly_digest: SMTP not configured; skipping live send "
            "(subscribers=%s campaign=%s)",
            len(subscribers),
            campaign.slug,
        )
        for sub in subscribers[:50]:
            EmailSendLog.objects.create(
                campaign=campaign,
                subscriber=sub,
                email=sub.email,
                status=EmailSendLog.Status.SKIPPED,
                meta={"reason": "no_smtp", "digest": True},
            )
        campaign.status = EmailCampaign.Status.SENT
        campaign.sent_at = timezone.now()
        campaign.save(update_fields=["status", "sent_at", "updated_at"])
        return {"sent": 0, "skipped": len(subscribers), "reason": "no_smtp"}

    sent = failed = 0
    for sub in subscribers:
        log = EmailSendLog.objects.create(
            campaign=campaign,
            subscriber=sub,
            email=sub.email,
            status=EmailSendLog.Status.QUEUED,
            meta={"digest": True},
        )
        try:
            send_mail(
                subject,
                body_text,
                getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@toolverse.ai"),
                [sub.email],
                fail_silently=False,
                html_message=campaign.body_html or None,
            )
            log.status = EmailSendLog.Status.SENT
            log.save(update_fields=["status"])
            sent += 1
        except Exception as exc:  # noqa: BLE001
            log.status = EmailSendLog.Status.FAILED
            log.error = str(exc)[:2000]
            log.save(update_fields=["status", "error"])
            failed += 1

    campaign.status = EmailCampaign.Status.SENT
    campaign.sent_at = timezone.now()
    campaign.save(update_fields=["status", "sent_at", "updated_at"])
    return {"sent": sent, "failed": failed, "subscribers": len(subscribers)}
