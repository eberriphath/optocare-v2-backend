def base_template(title, content):
    """
    Shared Optocare email layout.
    """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>{title}</title>

        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #f5f7f6;
                font-family: Arial, Helvetica, sans-serif;
                color: #1a1a1a;
            }}

            .wrapper {{
                width: 100%;
                padding: 40px 20px;
                box-sizing: border-box;
            }}

            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            }}

            .header {{
                background: #0f766e;
                padding: 28px 32px;
                text-align: center;
            }}

            .logo {{
                color: #ffffff;
                font-size: 28px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}

            .content {{
                padding: 36px 32px;
            }}

            h1 {{
                margin-top: 0;
                color: #163b36;
                font-size: 26px;
            }}

            p {{
                font-size: 16px;
                line-height: 1.7;
                color: #4b5563;
            }}

            .button {{
                display: inline-block;
                margin: 20px 0;
                padding: 13px 24px;
                background: #0f766e;
                color: #ffffff !important;
                text-decoration: none;
                border-radius: 7px;
                font-weight: bold;
            }}

            .notice {{
                margin: 24px 0;
                padding: 16px;
                background: #f0fdfa;
                border-left: 4px solid #0f766e;
                border-radius: 6px;
            }}

            .footer {{
                padding: 24px 32px;
                background: #f8fafc;
                text-align: center;
            }}

            .footer p {{
                margin: 4px 0;
                font-size: 13px;
                color: #6b7280;
            }}

            @media (max-width: 600px) {{
                .wrapper {{
                    padding: 20px 10px;
                }}

                .content {{
                    padding: 28px 20px;
                }}

                .header {{
                    padding: 24px 20px;
                }}
            }}
        </style>
    </head>

    <body>

        <div class="wrapper">

            <div class="container">

                <div class="header">
                    <div class="logo">
                        Optocare
                    </div>
                </div>

                <div class="content">
                    {content}
                </div>

                <div class="footer">
                    <p>© 2026 Optocare. All rights reserved.</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>

            </div>

        </div>

    </body>
    </html>
    """


def application_received_email(name):
    content = f"""
    <h1>Application received</h1>

    <p>Hello {name},</p>

    <p>
        Thank you for your interest in partnering with Optocare.
        We have successfully received your partner application.
    </p>

    <div class="notice">
        <strong>What happens next?</strong>
        <p>
            Our team will review your application and the information
            you provided. We will notify you once a decision has been made.
        </p>
    </div>

    <p>
        You don't need to submit another application while your current
        application is being reviewed.
    </p>

    <p>
        Thank you for choosing Optocare.
    </p>
    """

    return base_template(
        "Application Received | Optocare",
        content
    )


def new_application_admin_email(name, company_name):
    content = f"""
    <h1>New partner application</h1>

    <p>
        A new partner application has been submitted to Optocare.
    </p>

    <div class="notice">
        <strong>Applicant</strong>
        <p>{name}</p>

        <strong>Company</strong>
        <p>{company_name}</p>
    </div>

    <p>
        Log in to the Optocare administration dashboard to review
        the application.
    </p>
    """

    return base_template(
        "New Partner Application | Optocare",
        content
    )


def application_approved_email(name, activation_url):
    content = f"""
    <h1>Application approved</h1>

    <p>Hello {name},</p>

    <p>
        We're pleased to let you know that your application to become
        an Optocare partner has been approved.
    </p>

    <div class="notice">
        <strong>Your partner account is ready</strong>
        <p>
            Your Optocare partner account has been created successfully.
            Before you can sign in, you need to activate your account
            and create your password.
        </p>
    </div>

    <p style="text-align: center;">
        <a href="{activation_url}" class="button">
            Activate Your Account
        </a>
    </p>

    <p>
        This activation link is valid for 48 hours. If the link expires,
        you will need to request a new activation link.
    </p>

    <p>
        Welcome to Optocare.
    </p>
    """

    return base_template(
        "Application Approved | Optocare",
        content
    )


def application_rejected_email(name, review_notes):
    content = f"""
    <h1>Application update</h1>

    <p>Hello {name},</p>

    <p>
        Thank you for taking the time to apply to become an Optocare
        partner.
    </p>

    <p>
        After reviewing your application, we are unable to approve it
        at this time.
    </p>

    <div class="notice">
        <strong>Review notes</strong>
        <p>{review_notes}</p>
    </div>

    <p>
        Please review the information above and contact Optocare if
        you need further clarification.
    </p>
    """

    return base_template(
        "Application Update | Optocare",
        content
    )


def password_changed_email(name):
    content = f"""
    <h1>Password changed</h1>

    <p>Hello {name},</p>

    <p>
        Your Optocare account password has been successfully changed.
    </p>

    <div class="notice">
        <strong>Didn't make this change?</strong>
        <p>
            If you did not change your password, contact Optocare
            support immediately.
        </p>
    </div>

    <p>
        For your security, never share your password with anyone.
    </p>
    """

    return base_template(
        "Password Changed | Optocare",
        content
    )


def password_reset_email(name, reset_url):
    content = f"""
    <h1>Reset your password</h1>

    <p>Hello {name},</p>

    <p>
        We received a request to reset your Optocare account password.
    </p>

    <p style="text-align: center;">
        <a href="{reset_url}" class="button">
            Reset Password
        </a>
    </p>

    <p>
        This link is temporary and will expire for security reasons.
    </p>

    <div class="notice">
        <strong>Didn't request this?</strong>
        <p>
            You can safely ignore this email. Your password will not
            change unless you use the reset link.
        </p>
    </div>
    """

    return base_template(
        "Reset Your Password | Optocare",
        content
    )