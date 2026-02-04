"""
Email service using Resend for transactional emails.
"""
import logging
import resend
from datetime import datetime
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
            <p style="font-size: 24px; color: #0d9488; font-weight: bold;">
                Overall Score: {score:.1f}/10
            </p>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #1c1917; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 500; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
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

                    <p>Best regards,<br>The Pathway Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from Pathway.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=employer_email,
            subject=f"[Pathway] {candidate_name} completed interview for {job_title}",
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
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
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

                    <p>Best regards,<br>The Pathway Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from Pathway.</p>
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
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #1c1917; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
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

                    <p>Best regards,<br>The Pathway Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from Pathway.</p>
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
            "interview_request": "#0d9488",  # Teal
            "shortlist_notice": "#0d9488",   # Teal
            "rejection": "#78716c",          # Stone-500
            "custom": "#0d9488",             # Teal
        }
        header_color = header_colors.get(message_type, "#0d9488")

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
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {header_color}; color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .message-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e7e5e3; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
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
                        <h3 style="margin-top: 0; color: #292524;">{subject}</h3>
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

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #1c1917; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
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

                    <p style="color: #78716c; font-size: 14px;">
                        If the button doesn't work, copy this link to your browser:<br>
                        <a href="{verify_url}" style="color: #0d9488; word-break: break-all;">{verify_url}</a>
                    </p>

                    <p style="color: #78716c; font-size: 14px; margin-top: 20px;">
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


    def send_password_reset_email(
        self,
        email: str,
        name: str,
        reset_token: str,
        user_type: str = "candidate",  # "candidate" or "employer"
    ) -> Optional[str]:
        """
        Send password reset link.

        Args:
            email: Recipient email address
            name: User's name
            reset_token: Unique reset token
            user_type: Type of user (candidate or employer)
        """
        reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}&type={user_type}"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #1c1917; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
                .warning {{ background: #fef3c7; border: 1px solid #f59e0b; padding: 12px; border-radius: 6px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">Reset Your Password</h1>
                </div>
                <div class="content">
                    <p>Hi {name},</p>

                    <p>We received a request to reset your password. Click the button below to create a new password:</p>

                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>

                    <div class="warning">
                        <strong>This link will expire in 1 hour.</strong>
                        If you didn't request a password reset, you can safely ignore this email.
                    </div>

                    <p style="color: #78716c; font-size: 14px;">
                        If the button doesn't work, copy this link to your browser:<br>
                        <a href="{reset_url}" style="color: #0d9488; word-break: break-all;">{reset_url}</a>
                    </p>

                    <p>Best regards,<br>The Pathway Team</p>
                </div>
                <div class="footer">
                    <p>If you didn't request this, please ignore this email or contact support.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=email,
            subject="[Pathway] Reset Your Password",
            html=html,
        )

    def send_welcome_email(
        self,
        email: str,
        name: str,
        user_type: str = "candidate",  # "candidate" or "employer"
    ) -> Optional[str]:
        """
        Send welcome/onboarding email to new users.

        Args:
            email: Recipient email address
            name: User's name
            user_type: Type of user (candidate or employer)
        """
        if user_type == "candidate":
            dashboard_url = f"{settings.frontend_url}/candidate/dashboard"
            content = f"""
                <p>Hi {name},</p>

                <p>Welcome to <strong>Pathway</strong>! We're excited to help you land your first job.</p>

                <p>Here's how to get started:</p>

                <ol style="line-height: 2;">
                    <li><strong>Complete your profile</strong> - Add your education, upload your resume</li>
                    <li><strong>Connect GitHub</strong> - Showcase your projects and contributions</li>
                    <li><strong>Take your first interview</strong> - Answer 5 questions to get your score</li>
                    <li><strong>Get matched</strong> - Employers will find you based on your trajectory</li>
                </ol>

                <p style="text-align: center; margin: 30px 0;">
                    <a href="{dashboard_url}" class="button">Go to Dashboard</a>
                </p>

                <p><strong>Pro tip:</strong> Students who complete their profile within 24 hours are 3x more likely to get matched with employers.</p>
            """
            subject = "Welcome to Pathway - Let's Get Started!"
        else:
            dashboard_url = f"{settings.frontend_url}/employer/dashboard"
            content = f"""
                <p>Hi {name},</p>

                <p>Welcome to <strong>Pathway</strong>! We're excited to help you find exceptional early-career talent.</p>

                <p>Here's how to get started:</p>

                <ol style="line-height: 2;">
                    <li><strong>Browse the talent pool</strong> - See candidates ranked by AI-scored interviews</li>
                    <li><strong>Create job postings</strong> - Get auto-matched with relevant candidates</li>
                    <li><strong>Review interviews</strong> - Watch video responses and see detailed scoring</li>
                    <li><strong>Contact candidates</strong> - Reach out to your top picks directly</li>
                </ol>

                <p style="text-align: center; margin: 30px 0;">
                    <a href="{dashboard_url}" class="button">Explore Talent Pool</a>
                </p>

                <p><strong>What makes Pathway different:</strong> Unlike traditional resumes, you can see candidates' growth over time. Watch how they improve interview-to-interview over 2-4 years of college.</p>
            """
            subject = "Welcome to Pathway - Find Your Next Hire"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); color: white; padding: 40px 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .logo {{ font-size: 32px; font-weight: bold; margin-bottom: 10px; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #1c1917; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
                .tip {{ background: #f0fdfa; border: 1px solid #0d9488; padding: 12px; border-radius: 6px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">Pathway</div>
                    <p style="margin: 0; opacity: 0.9;">Show your growth, land your first job</p>
                </div>
                <div class="content">
                    {content}

                    <p>Questions? Just reply to this email - we're here to help!</p>

                    <p>Best regards,<br>The Pathway Team</p>
                </div>
                <div class="footer">
                    <p>You're receiving this because you signed up for Pathway.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=email,
            subject=f"[Pathway] {subject}",
            html=html,
        )

    def send_interview_reminder(
        self,
        email: str,
        name: str,
        days_since_signup: int = 3,
    ) -> Optional[str]:
        """
        Send reminder to complete first interview.
        """
        dashboard_url = f"{settings.frontend_url}/candidate/dashboard"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #1c1917; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
                .stat {{ text-align: center; padding: 20px; background: white; border-radius: 8px; margin: 20px 0; }}
                .stat-number {{ font-size: 48px; font-weight: bold; color: #0d9488; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">You're Almost There!</h1>
                </div>
                <div class="content">
                    <p>Hi {name},</p>

                    <p>You signed up for Pathway {days_since_signup} days ago, but haven't completed your first interview yet.</p>

                    <div class="stat">
                        <div class="stat-number">15</div>
                        <div>minutes to complete</div>
                    </div>

                    <p>Your first interview is just 5 video questions. Once complete:</p>
                    <ul>
                        <li>Get your AI-scored profile</li>
                        <li>Become visible to employers</li>
                        <li>Start tracking your growth over time</li>
                    </ul>

                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{dashboard_url}" class="button">Start Interview Now</a>
                    </p>

                    <p>Best regards,<br>The Pathway Team</p>
                </div>
                <div class="footer">
                    <p>Don't want these reminders? <a href="{settings.frontend_url}/unsubscribe" style="color: #0d9488;">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=email,
            subject="[Pathway] Complete your first interview (15 min)",
            html=html,
        )

    def send_profile_view_notification(
        self,
        email: str,
        name: str,
        employer_name: str,
        job_title: Optional[str] = None,
    ) -> Optional[str]:
        """
        Notify candidate when an employer views their profile.
        """
        dashboard_url = f"{settings.frontend_url}/candidate/dashboard"
        job_info = f" for the <strong>{job_title}</strong> position" if job_title else ""

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #1c1917; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">Someone's Interested!</h1>
                </div>
                <div class="content">
                    <p>Hi {name},</p>

                    <p><strong>{employer_name}</strong> viewed your profile{job_info}.</p>

                    <p>This is a good sign! Make sure your profile is complete and up-to-date to increase your chances of getting contacted.</p>

                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{dashboard_url}" class="button">View Your Profile</a>
                    </p>

                    <p>Best regards,<br>The Pathway Team</p>
                </div>
                <div class="footer">
                    <p>Manage notification preferences in your <a href="{settings.frontend_url}/candidate/settings" style="color: #0d9488;">settings</a>.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=email,
            subject=f"[Pathway] {employer_name} viewed your profile",
            html=html,
        )

    def send_weekly_digest(
        self,
        email: str,
        name: str,
        profile_views: int,
        new_matches: int,
        next_interview_eligible: bool,
    ) -> Optional[str]:
        """
        Send weekly activity digest to candidates.
        """
        dashboard_url = f"{settings.frontend_url}/candidate/dashboard"

        interview_cta = ""
        if next_interview_eligible:
            interview_cta = """
            <div style="background: #f0fdfa; border: 1px solid #0d9488; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <strong>You're eligible for a new monthly interview!</strong>
                <p style="margin: 5px 0 0 0;">Take it to show your growth and improve your score.</p>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #1c1917; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat {{ text-align: center; padding: 15px; background: white; border-radius: 8px; flex: 1; margin: 0 5px; }}
                .stat-number {{ font-size: 32px; font-weight: bold; color: #0d9488; }}
                .stat-label {{ font-size: 14px; color: #78716c; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">Your Weekly Update</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Here's what happened this week</p>
                </div>
                <div class="content">
                    <p>Hi {name},</p>

                    <div class="stats">
                        <div class="stat">
                            <div class="stat-number">{profile_views}</div>
                            <div class="stat-label">Profile Views</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">{new_matches}</div>
                            <div class="stat-label">New Matches</div>
                        </div>
                    </div>

                    {interview_cta}

                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{dashboard_url}" class="button">View Dashboard</a>
                    </p>

                    <p>Keep showing your growth!</p>

                    <p>Best regards,<br>The Pathway Team</p>
                </div>
                <div class="footer">
                    <p>Manage notification preferences in your <a href="{settings.frontend_url}/candidate/settings" style="color: #0d9488;">settings</a>.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=email,
            subject="[Pathway] Your weekly update",
            html=html,
        )


    def send_interview_reminder_candidate(
        self,
        to_email: str,
        candidate_name: str,
        company_name: str,
        interview_title: str,
        scheduled_at: datetime,
        duration_minutes: int,
        google_meet_link: Optional[str] = None,
        time_text: str = "soon",
    ) -> Optional[str]:
        """Send interview reminder to candidate."""
        from datetime import datetime

        formatted_date = scheduled_at.strftime("%A, %B %d, %Y")
        formatted_time = scheduled_at.strftime("%I:%M %p")

        meet_link_html = ""
        if google_meet_link:
            meet_link_html = f"""
            <p style="text-align: center; margin: 20px 0;">
                <a href="{google_meet_link}" class="button">Join Google Meet</a>
            </p>
            <p style="color: #78716c; font-size: 14px; text-align: center;">
                Meeting link: <a href="{google_meet_link}" style="color: #0d9488;">{google_meet_link}</a>
            </p>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #1c1917; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }}
                .details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e7e5e3; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">Interview Reminder</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Your interview is {time_text}</p>
                </div>
                <div class="content">
                    <p>Hi {candidate_name},</p>

                    <p>This is a reminder that your interview with <strong>{company_name}</strong> is coming up {time_text}.</p>

                    <div class="details">
                        <p style="margin: 0;"><strong>Interview:</strong> {interview_title}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Date:</strong> {formatted_date}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Time:</strong> {formatted_time}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Duration:</strong> {duration_minutes} minutes</p>
                    </div>

                    {meet_link_html}

                    <p><strong>Tips for your interview:</strong></p>
                    <ul>
                        <li>Test your camera and microphone beforehand</li>
                        <li>Find a quiet, well-lit space</li>
                        <li>Have a copy of your resume handy</li>
                        <li>Prepare questions for the interviewer</li>
                    </ul>

                    <p>Good luck!</p>

                    <p>Best regards,<br>The Pathway Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated reminder from Pathway.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=to_email,
            subject=f"Reminder: Your interview with {company_name} is {time_text}",
            html=html,
        )

    def send_interview_reminder_interviewer(
        self,
        to_email: str,
        candidate_name: str,
        interview_title: str,
        scheduled_at: datetime,
        duration_minutes: int,
        google_meet_link: Optional[str] = None,
        time_text: str = "soon",
    ) -> Optional[str]:
        """Send interview reminder to interviewer."""
        from datetime import datetime

        formatted_date = scheduled_at.strftime("%A, %B %d, %Y")
        formatted_time = scheduled_at.strftime("%I:%M %p")

        meet_link_html = ""
        if google_meet_link:
            meet_link_html = f"""
            <p style="text-align: center; margin: 20px 0;">
                <a href="{google_meet_link}" class="button">Join Google Meet</a>
            </p>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #1c1917; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }}
                .details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e7e5e3; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">Interview Reminder</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Upcoming interview {time_text}</p>
                </div>
                <div class="content">
                    <p>Hi,</p>

                    <p>This is a reminder that you have an interview scheduled {time_text}.</p>

                    <div class="details">
                        <p style="margin: 0;"><strong>Candidate:</strong> {candidate_name}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Interview:</strong> {interview_title}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Date:</strong> {formatted_date}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Time:</strong> {formatted_time}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Duration:</strong> {duration_minutes} minutes</p>
                    </div>

                    {meet_link_html}

                    <p>Best regards,<br>The Pathway Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated reminder from Pathway.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=to_email,
            subject=f"Interview Reminder: {candidate_name} - {time_text}",
            html=html,
        )

    def send_interview_scheduled_candidate(
        self,
        to_email: str,
        candidate_name: str,
        company_name: str,
        interview_title: str,
        scheduled_at: datetime,
        duration_minutes: int,
        google_meet_link: Optional[str] = None,
    ) -> Optional[str]:
        """Send interview confirmation to candidate after booking."""
        from datetime import datetime

        formatted_date = scheduled_at.strftime("%A, %B %d, %Y")
        formatted_time = scheduled_at.strftime("%I:%M %p")

        meet_link_html = ""
        if google_meet_link:
            meet_link_html = f"""
            <p style="text-align: center; margin: 20px 0;">
                <a href="{google_meet_link}" class="button">Add to Calendar</a>
            </p>
            <p style="color: #78716c; font-size: 14px; text-align: center;">
                Google Meet link: <a href="{google_meet_link}" style="color: #0d9488;">{google_meet_link}</a>
            </p>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #1c1917; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }}
                .details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e7e5e3; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">Interview Confirmed!</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Your interview has been scheduled</p>
                </div>
                <div class="content">
                    <p>Hi {candidate_name},</p>

                    <p>Great news! Your interview with <strong>{company_name}</strong> has been confirmed.</p>

                    <div class="details">
                        <p style="margin: 0;"><strong>Interview:</strong> {interview_title}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Date:</strong> {formatted_date}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Time:</strong> {formatted_time}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Duration:</strong> {duration_minutes} minutes</p>
                    </div>

                    {meet_link_html}

                    <p>We'll send you reminders before the interview. In the meantime, here are some tips:</p>

                    <ul>
                        <li>Research the company and the role</li>
                        <li>Prepare examples of your work and accomplishments</li>
                        <li>Test your technology setup (camera, microphone, internet)</li>
                        <li>Prepare thoughtful questions for the interviewer</li>
                    </ul>

                    <p>Good luck!</p>

                    <p>Best regards,<br>The Pathway Team</p>
                </div>
                <div class="footer">
                    <p>Need to reschedule? Please contact {company_name} directly.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=to_email,
            subject=f"Interview Confirmed: {interview_title} at {company_name}",
            html=html,
        )

    def send_interview_scheduled_interviewer(
        self,
        to_email: str,
        candidate_name: str,
        candidate_email: str,
        interview_title: str,
        scheduled_at: datetime,
        duration_minutes: int,
        google_meet_link: Optional[str] = None,
        dashboard_url: Optional[str] = None,
    ) -> Optional[str]:
        """Send interview notification to interviewer."""
        from datetime import datetime

        formatted_date = scheduled_at.strftime("%A, %B %d, %Y")
        formatted_time = scheduled_at.strftime("%I:%M %p")

        dashboard_html = ""
        if dashboard_url:
            dashboard_html = f"""
            <p style="text-align: center; margin: 20px 0;">
                <a href="{dashboard_url}" class="button">View in Dashboard</a>
            </p>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #1c1917; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }}
                .details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e7e5e3; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">New Interview Scheduled</h1>
                </div>
                <div class="content">
                    <p>Hi,</p>

                    <p>A new interview has been scheduled with a candidate.</p>

                    <div class="details">
                        <p style="margin: 0;"><strong>Candidate:</strong> {candidate_name}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Email:</strong> {candidate_email}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Interview:</strong> {interview_title}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Date:</strong> {formatted_date}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Time:</strong> {formatted_time}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Duration:</strong> {duration_minutes} minutes</p>
                    </div>

                    {dashboard_html}

                    <p>A calendar invite has been sent to your email.</p>

                    <p>Best regards,<br>The Pathway Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from Pathway.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=to_email,
            subject=f"New Interview: {candidate_name} - {interview_title}",
            html=html,
        )

    def send_self_schedule_invitation(
        self,
        to_email: str,
        candidate_name: str,
        company_name: str,
        job_title: Optional[str],
        schedule_url: str,
        message: Optional[str] = None,
    ) -> Optional[str]:
        """Send self-scheduling link invitation to candidate."""
        job_info = f" for the <strong>{job_title}</strong> position" if job_title else ""
        custom_message = f'<div style="background: #f5f5f4; padding: 15px; border-radius: 8px; margin: 20px 0;"><p style="margin: 0; white-space: pre-wrap;">{message}</p></div>' if message else ""

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #1c1917; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">Schedule Your Interview</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Pick a time that works for you</p>
                </div>
                <div class="content">
                    <p>Hi {candidate_name or 'there'},</p>

                    <p><strong>{company_name}</strong> would like to schedule an interview with you{job_info}.</p>

                    {custom_message}

                    <p>Please use the link below to select a time that works best for you:</p>

                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{schedule_url}" class="button">Schedule Interview</a>
                    </p>

                    <p style="color: #78716c; font-size: 14px;">
                        Or copy this link: <a href="{schedule_url}" style="color: #0d9488;">{schedule_url}</a>
                    </p>

                    <p>We look forward to speaking with you!</p>

                    <p>Best regards,<br>The {company_name} Team</p>
                </div>
                <div class="footer">
                    <p>This invitation was sent via Pathway.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=to_email,
            subject=f"[{company_name}] Schedule Your Interview",
            html=html,
        )

    async def send_organization_invite(
        self,
        to_email: str,
        organization_name: str,
        inviter_name: str,
        role: str,
        invite_url: str,
    ) -> Optional[str]:
        """
        Send invitation to join an organization/team.
        """
        role_descriptions = {
            "owner": "Full access including billing and team management",
            "admin": "Manage team members, jobs, and settings",
            "recruiter": "Manage jobs and contact candidates",
            "hiring_manager": "View candidates and provide feedback",
            "interviewer": "View assigned candidates",
        }
        role_desc = role_descriptions.get(role, "Team member")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #292524; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #fafaf9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #1c1917; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #78716c; font-size: 14px; }}
                .role-badge {{ display: inline-block; background: #f0fdfa; color: #0d9488; padding: 4px 12px; border-radius: 9999px; font-size: 14px; font-weight: 500; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">You're Invited!</h1>
                </div>
                <div class="content">
                    <p>Hi there,</p>

                    <p><strong>{inviter_name}</strong> has invited you to join <strong>{organization_name}</strong> on Pathway.</p>

                    <p>
                        Your role: <span class="role-badge">{role.replace('_', ' ').title()}</span>
                        <br>
                        <small style="color: #78716c;">{role_desc}</small>
                    </p>

                    <p>Pathway is a collaborative recruiting platform that helps teams find and hire top talent from college students.</p>

                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{invite_url}" class="button">Accept Invitation</a>
                    </p>

                    <p style="color: #78716c; font-size: 14px;">
                        This invitation expires in 7 days. If you didn't expect this email, you can safely ignore it.
                    </p>
                </div>
                <div class="footer">
                    <p>Pathway - Collaborative Recruiting Platform</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to=to_email,
            subject=f"[Pathway] {inviter_name} invited you to join {organization_name}",
            html=html,
        )


# Global instance
email_service = EmailService()
