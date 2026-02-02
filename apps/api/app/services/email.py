"""
Email service using Resend for transactional emails.
"""
import logging
import resend
from typing import Optional
from ..config import settings

logger = logging.getLogger("pathway.email")


class EmailService:
    """Service for sending transactional emails."""

    def __init__(self):
        self._initialized = False

    def _ensure_initialized(self):
        if not self._initialized and settings.resend_api_key:
            resend.api_key = settings.resend_api_key
            self._initialized = True

    def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        from_email: Optional[str] = None,
    ) -> Optional[str]:
        """
        Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            html: HTML content of the email
            from_email: Sender email (defaults to configured sender)

        Returns:
            Email ID if successful, None otherwise
        """
        self._ensure_initialized()

        if not settings.resend_api_key:
            logger.info(f"[EMAIL MOCK] To: {to}, Subject: {subject}")
            return "mock-email-id"

        try:
            params = {
                "from": from_email or settings.email_from,
                "to": [to],
                "subject": subject,
                "html": html,
            }

            response = resend.Emails.send(params)
            return response.get("id")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return None

    def send_interview_complete_to_employer(
        self,
        employer_email: str,
        employer_name: str,
        candidate_name: str,
        job_title: str,
        interview_id: str,
        score: Optional[float] = None,
    ) -> Optional[str]:
        """Send notification to employer when interview is complete."""
        dashboard_url = f"{settings.frontend_url}/dashboard/interviews/{interview_id}"

        score_html = ""
        if score is not None:
            score_html = f"""
            <p style="font-size: 24px; color: #2563eb; font-weight: bold;">
                Overall Score: {score:.1f}/10
            </p>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 500; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">Interview Completed</h1>
                </div>
                <div class="content">
                    <p>Hi {employer_name},</p>

                    <p><strong>{candidate_name}</strong> has completed their video interview for the <strong>{job_title}</strong> position.</p>

                    {score_html}

                    <p>Review their responses and AI analysis in your dashboard:</p>

                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{dashboard_url}" class="button">View Interview</a>
                    </p>

                    <p>Best regards,<br>ZhiPin AI Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from ZhiPin AI.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=employer_email,
            subject=f"[ZhiPin AI] {candidate_name} completed interview for {job_title}",
            html=html,
        )

    def send_interview_complete_to_candidate(
        self,
        candidate_email: str,
        candidate_name: str,
        job_title: str,
        company_name: str,
    ) -> Optional[str]:
        """Send thank you email to candidate after interview."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">Thank You!</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Your interview has been submitted</p>
                </div>
                <div class="content">
                    <p>Hi {candidate_name},</p>

                    <p>Thank you for completing your video interview for the <strong>{job_title}</strong> position at <strong>{company_name}</strong>.</p>

                    <p>Your responses are now being reviewed by our AI system and the hiring team. Here's what happens next:</p>

                    <ul>
                        <li>Our AI will analyze your responses within the next few minutes</li>
                        <li>The hiring team at {company_name} will review your interview</li>
                        <li>If they'd like to proceed, they will contact you directly</li>
                    </ul>

                    <p>We appreciate your interest and wish you the best of luck!</p>

                    <p>Best regards,<br>ZhiPin AI Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from ZhiPin AI.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=candidate_email,
            subject=f"Thank you for your interview - {job_title} at {company_name}",
            html=html,
        )

    def send_invite_link(
        self,
        candidate_email: str,
        candidate_name: str,
        job_title: str,
        company_name: str,
        invite_url: str,
    ) -> Optional[str]:
        """Send interview invite link to candidate."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">You're Invited!</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Complete your video interview</p>
                </div>
                <div class="content">
                    <p>Hi {candidate_name or 'there'},</p>

                    <p><strong>{company_name}</strong> has invited you to complete a video interview for the <strong>{job_title}</strong> position.</p>

                    <p>This is an asynchronous video interview - you can complete it at any time that works for you. Here's what to expect:</p>

                    <ul>
                        <li>5 questions to answer on video</li>
                        <li>Up to 2 minutes per question</li>
                        <li>You can re-record your answers before submitting</li>
                        <li>Total time: approximately 15-20 minutes</li>
                    </ul>

                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{invite_url}" class="button">Start Interview</a>
                    </p>

                    <p><strong>Tips for success:</strong></p>
                    <ul>
                        <li>Find a quiet, well-lit space</li>
                        <li>Test your camera and microphone beforehand</li>
                        <li>Speak clearly and look at the camera</li>
                        <li>Be yourself and share specific examples</li>
                    </ul>

                    <p>Good luck!</p>

                    <p>Best regards,<br>ZhiPin AI Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from ZhiPin AI.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=candidate_email,
            subject=f"Interview Invitation: {job_title} at {company_name}",
            html=html,
        )


    def send_employer_message(
        self,
        candidate_email: str,
        candidate_name: str,
        employer_name: str,
        subject: str,
        body: str,
        job_title: Optional[str] = None,
        message_type: str = "custom",
    ) -> Optional[str]:
        """
        Send a message from employer to candidate.

        Args:
            candidate_email: Recipient email
            candidate_name: Candidate's name
            employer_name: Company/employer name
            subject: Message subject
            body: Message body (plain text or HTML)
            job_title: Related job title (optional)
            message_type: Type of message (interview_request, rejection, shortlist_notice, custom)
        """
        # Determine header color based on message type
        header_colors = {
            "interview_request": "#2563eb",  # Blue
            "shortlist_notice": "#10b981",   # Green
            "rejection": "#6b7280",          # Gray
            "custom": "#2563eb",             # Blue
        }
        header_color = header_colors.get(message_type, "#2563eb")

        # Determine header title based on message type
        header_titles = {
            "interview_request": "Interview Request",
            "shortlist_notice": "Good News!",
            "rejection": "Application Update",
            "custom": "Message from Employer",
        }
        header_title = header_titles.get(message_type, "Message from Employer")

        job_info = f" regarding <strong>{job_title}</strong>" if job_title else ""

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {header_color}; color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                .message-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e5e7eb; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">{header_title}</h1>
                </div>
                <div class="content">
                    <p>Hi {candidate_name},</p>

                    <p><strong>{employer_name}</strong> has sent you a message{job_info}:</p>

                    <div class="message-box">
                        <h3 style="margin-top: 0; color: #374151;">{subject}</h3>
                        <div style="white-space: pre-wrap;">{body}</div>
                    </div>

                    <p>If you have any questions, please reply directly to the employer.</p>

                    <p>Best regards,<br>The Pathway Team</p>
                </div>
                <div class="footer">
                    <p>This message was sent via Pathway career platform.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=candidate_email,
            subject=f"[{employer_name}] {subject}",
            html=html,
        )


    def send_verification_email(
        self,
        email: str,
        name: str,
        verification_token: str,
        user_type: str = "candidate",  # "candidate" or "employer"
    ) -> Optional[str]:
        """
        Send email verification link.

        Args:
            email: Recipient email address
            name: User's name
            verification_token: Unique verification token
            user_type: Type of user (candidate or employer)
        """
        verify_url = f"{settings.frontend_url}/verify-email?token={verification_token}&type={user_type}"

        # Use indigo/purple gradient for Pathway branding
        header_color = "#6366f1"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">Verify Your Email</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Welcome to Pathway</p>
                </div>
                <div class="content">
                    <p>Hi {name},</p>

                    <p>Thank you for joining Pathway! Please click the button below to verify your email address and complete your registration.</p>

                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{verify_url}" class="button">Verify Email</a>
                    </p>

                    <p style="color: #6b7280; font-size: 14px;">
                        If the button doesn't work, copy this link to your browser:<br>
                        <a href="{verify_url}" style="color: {header_color}; word-break: break-all;">{verify_url}</a>
                    </p>

                    <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                        This link will expire in 24 hours.
                    </p>

                    <p>Best regards,<br>The Pathway Team</p>
                </div>
                <div class="footer">
                    <p>If you didn't sign up for Pathway, please ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=email,
            subject="[Pathway] Verify Your Email",
            html=html,
        )


# Global instance
email_service = EmailService()
