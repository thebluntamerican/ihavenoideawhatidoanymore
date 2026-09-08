"""Email relay. Resend if a key is present, console otherwise.

The site never publishes anyone's address; it forwards messages to it.
"""
import os
import logging
import urllib.request
import urllib.error
import json

log = logging.getLogger("noidea.mail")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
MAIL_FROM = os.environ.get("MAIL_FROM", "hello@ihavenoideawhatidoanymore.com")
SITE_URL = os.environ.get("SITE_URL", "http://localhost:8000")


def send(to: str, subject: str, html: str, reply_to: str = "") -> bool:
    """Return True if the message was handed to a provider."""
    if not RESEND_API_KEY:
        log.warning("No RESEND_API_KEY set - email not sent.\nTo: %s\nSubject: %s\n%s",
                    to, subject, html)
        return False

    payload = {"from": MAIL_FROM, "to": [to], "subject": subject, "html": html}
    if reply_to:
        payload["reply_to"] = reply_to

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return 200 <= r.status < 300
    except urllib.error.HTTPError as e:
        log.error("Resend rejected the message (%s): %s", e.code, e.read()[:400])
    except Exception as e:  # network, DNS, timeout
        log.error("Could not reach Resend: %s", e)
    return False


def enquiry_email(profile, enquiry) -> str:
    org = f" ({enquiry.from_org})" if enquiry.from_org else ""
    body = enquiry.message.replace("&", "&amp;").replace("<", "&lt;")
    return f"""
    <div style="font-family:ui-sans-serif,system-ui,sans-serif;max-width:560px">
      <p style="font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:#8a8578">
        Someone wants to hire you</p>
      <h2 style="font-size:22px;margin:.2em 0 .6em">{enquiry.from_name}{org}</h2>
      <div style="white-space:pre-wrap;border-left:3px solid #FF4D2E;padding-left:14px;
                  font-size:15px;line-height:1.55;color:#1b1a17">{body}</div>
      <p style="font-size:14px;color:#5d584d;margin-top:22px">
        Reply straight to this email to reach them at
        <strong>{enquiry.from_email}</strong>.</p>
      <p style="font-size:12px;color:#8a8578;border-top:1px solid #e3ded2;padding-top:14px">
        Sent via <a href="{SITE_URL}" style="color:#FF4D2E">ihavenoideawhatidoanymore.com</a>
        &mdash; your address was never shown to them.</p>
    </div>"""


def welcome_email(profile) -> str:
    return f"""
    <div style="font-family:ui-sans-serif,system-ui,sans-serif;max-width:560px">
      <h2 style="font-size:22px;margin:.2em 0 .5em">You're in the directory.</h2>
      <p style="font-size:15px;line-height:1.6;color:#1b1a17">
        Your profile is live at
        <a href="{SITE_URL}/p/{profile.slug}" style="color:#FF4D2E">{SITE_URL}/p/{profile.slug}</a>
      </p>
      <p style="font-size:15px;line-height:1.6;color:#1b1a17">
        Keep this link to edit or delete it later &mdash; it's the only key,
        and we can't recover it for you:<br>
        <a href="{SITE_URL}/edit/{profile.slug}?token={profile.edit_token}"
           style="color:#FF4D2E;word-break:break-all">
           {SITE_URL}/edit/{profile.slug}?token={profile.edit_token}</a>
      </p>
      <p style="font-size:12px;color:#8a8578;border-top:1px solid #e3ded2;padding-top:14px">
        Your email address is not shown on the site. Messages get forwarded here.</p>
    </div>"""
