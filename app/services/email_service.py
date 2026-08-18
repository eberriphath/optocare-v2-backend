import resend
from flask import current_app

from app.services.email_templates import (
    application_received_email,
    new_application_admin_email,
    application_approved_email,
    application_rejected_email,
    password_changed_email,
    password_reset_email,
)


def send_email(
    to,
    subject,
    html,
    text=None
):
    """
    Send an email through Resend.

    Args:
        to: Recipient email address.
        subject: Email subject.
        html: HTML email body.
        text: Optional plain-text fallback.
    """

    api_key = current_app.config.get("RESEND_API_KEY")

    if not api_key:
        raise RuntimeError(
            "RESEND_API_KEY is not configured"
        )

    resend.api_key = api_key

    params = {
        "from": (
            f"{current_app.config['MAIL_FROM_NAME']} "
            f"<{current_app.config['MAIL_FROM_EMAIL']}>"
        ),
        "to": [to],
        "subject": subject,
        "html": html,
    }

    if text:
        params["text"] = text

    response = resend.Emails.send(params)

    return response


def send_application_received_email(
    recipient,
    name
):
    html = application_received_email(name)

    return send_email(
        to=recipient,
        subject="Application Received | Optocare",
        html=html,
        text=(
            f"Hello {name},\n\n"
            "Thank you for your interest in partnering with Optocare. "
            "We have successfully received your application.\n\n"
            "Our team will review your application and notify you "
            "once a decision has been made.\n\n"
            "Thank you,\n"
            "Optocare"
        )
    )


def send_new_application_admin_email(
    recipient,
    name,
    company_name
):
    html = new_application_admin_email(
        name,
        company_name
    )

    return send_email(
        to=recipient,
        subject="New Partner Application | Optocare",
        html=html,
        text=(
            "A new partner application has been submitted.\n\n"
            f"Applicant: {name}\n"
            f"Company: {company_name}\n\n"
            "Please log in to the Optocare administration dashboard "
            "to review the application."
        )
    )


def send_application_approved_email(
    recipient,
    name,
    activation_url
):
    html = application_approved_email(
        name,
        activation_url
    )

    return send_email(
        to=recipient,
        subject="Application Approved | Optocare",
        html=html,
        text=(
            f"Hello {name},\n\n"
            "We're pleased to let you know that your application "
            "to become an Optocare partner has been approved.\n\n"
            "Your partner account has been created. "
            "Please activate your account and set your password "
            "using the following link:\n\n"
            f"{activation_url}\n\n"
            "This activation link expires in 48 hours.\n\n"
            "Welcome to Optocare."
        )
    )


def send_application_rejected_email(
    recipient,
    name,
    review_notes
):
    html = application_rejected_email(
        name,
        review_notes
    )

    return send_email(
        to=recipient,
        subject="Application Update | Optocare",
        html=html,
        text=(
            f"Hello {name},\n\n"
            "After reviewing your application, we are unable to "
            "approve it at this time.\n\n"
            "Review notes:\n"
            f"{review_notes}\n\n"
            "Thank you,\n"
            "Optocare"
        )
    )


def send_password_changed_email(
    recipient,
    name
):
    html = password_changed_email(name)

    return send_email(
        to=recipient,
        subject="Password Changed | Optocare",
        html=html,
        text=(
            f"Hello {name},\n\n"
            "Your Optocare account password has been successfully "
            "changed.\n\n"
            "If you did not make this change, contact Optocare "
            "support immediately."
        )
    )


def send_password_reset_email(
    recipient,
    name,
    reset_url
):
    html = password_reset_email(
        name,
        reset_url
    )

    return send_email(
        to=recipient,
        subject="Reset Your Password | Optocare",
        html=html,
        text=(
            f"Hello {name},\n\n"
            "We received a request to reset your Optocare password.\n\n"
            f"Reset your password here:\n{reset_url}\n\n"
            "If you did not request this, you can safely ignore "
            "this email."
        )
    )