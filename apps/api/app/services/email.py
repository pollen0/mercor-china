"""
Email service using Resend for transactional emails.
"""
import logging
import resend
from datetime import datetime
from typing import Optional
from ..config import settings

logger = logging.getLogger("pathway.email")


# ==================== SHARED EMAIL DESIGN SYSTEM ====================
# Matches the app's HEYTEA-inspired aesthetic:
# - System font stack with tight letter-spacing
# - Stone/teal palette, minimal color usage
# - Generous whitespace, clean borders
# - Rounded corners (12px cards, 8px buttons)
# - No heavy gradients - clean and refined

EMAIL_STYLES = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.7;
    color: #1c1917;
    letter-spacing: -0.01em;
    -webkit-font-smoothing: antialiased;
    margin: 0;
    padding: 0;
    background-color: #f5f5f4;
}
.wrapper {
    background-color: #f5f5f4;
    padding: 40px 20px;
}
.container {
    max-width: 560px;
    margin: 0 auto;
    background: #ffffff;
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid #e7e5e3;
}
.header {
    background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%);
    padding: 32px 40px;
    text-align: center;
}
.header h1 {
    margin: 0;
    font-size: 22px;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: #ffffff;
}
.header p {
    margin: 8px 0 0 0;
    font-size: 14px;
    color: rgba(255, 255, 255, 0.85);
    font-weight: 400;
}
.content {
    padding: 40px;
}
.content p {
    margin: 0 0 16px 0;
    font-size: 15px;
    color: #292524;
}
.content ul, .content ol {
    margin: 0 0 16px 0;
    padding-left: 20px;
    font-size: 15px;
    color: #292524;
}
.content li {
    margin-bottom: 8px;
}
.button {
    display: inline-block;
    background: #1c1917;
    color: #ffffff !important;
    padding: 12px 32px;
    text-decoration: none;
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
    letter-spacing: -0.01em;
}
.button-teal {
    display: inline-block;
    background: #0d9488;
    color: #ffffff !important;
    padding: 12px 32px;
    text-decoration: none;
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
    letter-spacing: -0.01em;
}
.details {
    background: #fafaf9;
    padding: 20px 24px;
    border-radius: 12px;
    margin: 24px 0;
    border: 1px solid #e7e5e3;
}
.details p {
    margin: 0 0 8px 0;
    font-size: 14px;
    color: #44403c;
}
.details p:last-child {
    margin-bottom: 0;
}
.callout {
    background: #f0fdfa;
    border: 1px solid #99f6e4;
    padding: 16px 20px;
    border-radius: 12px;
    margin: 24px 0;
    font-size: 14px;
    color: #134e4a;
}
.warning {
    background: #fffbeb;
    border: 1px solid #fde68a;
    padding: 16px 20px;
    border-radius: 12px;
    margin: 24px 0;
    font-size: 14px;
    color: #92400e;
}
.message-box {
    background: #fafaf9;
    padding: 20px 24px;
    border-radius: 12px;
    margin: 24px 0;
    border: 1px solid #e7e5e3;
}
.stat {
    text-align: center;
    padding: 24px;
    background: #fafaf9;
    border-radius: 12px;
    margin: 24px 0;
    border: 1px solid #e7e5e3;
}
.stat-number {
    font-size: 40px;
    font-weight: 600;
    color: #0d9488;
    letter-spacing: -0.03em;
    line-height: 1;
}
.stat-label {
    font-size: 13px;
    color: #78716c;
    margin-top: 6px;
    font-weight: 400;
}
.divider {
    height: 1px;
    background: #e7e5e3;
    margin: 32px 0;
    border: none;
}
.footer {
    padding: 24px 40px;
    border-top: 1px solid #e7e5e3;
    text-align: center;
}
.footer p {
    margin: 0;
    font-size: 12px;
    color: #a8a29e;
    letter-spacing: 0;
}
.footer a {
    color: #78716c;
    text-decoration: underline;
}
.muted {
    color: #78716c !important;
    font-size: 13px !important;
}
a.link {
    color: #0d9488;
    text-decoration: none;
}
.badge {
    display: inline-block;
    background: #f0fdfa;
    color: #0d9488;
    padding: 4px 14px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 500;
}
"""


def _email_template(header_title: str, header_subtitle: str | None, body: str, footer_text: str = "This is an automated notification from Pathway.") -> str:
    """Build a complete email HTML from components."""
    subtitle_html = f'<p>{header_subtitle}</p>' if header_subtitle else ""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{EMAIL_STYLES}</style>
</head>
<body>
    <div class="wrapper">
        <div class="container">
            <div class="header">
                <h1>{header_title}</h1>
                {subtitle_html}
            </div>
            <div class="content">
                {body}
            </div>
            <div class="footer">
                <p>{footer_text}</p>
            </div>
        </div>
    </div>
</body>
</html>"""


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
                <div class="stat">
                    <div class="stat-number">{score:.1f}</div>
                    <div class="stat-label">Overall Score (out of 10)</div>
                </div>
            """

        body = f"""
            <p>Hi {employer_name},</p>
            <p><strong>{candidate_name}</strong> has completed their video interview for the <strong>{job_title}</strong> position.</p>
            {score_html}
            <p>Review their responses and AI analysis in your dashboard:</p>
            <p style="text-align: center; margin: 32px 0;">
                <a href="{dashboard_url}" class="button">View Interview</a>
            </p>
            <p>Best regards,<br>The Pathway Team</p>
        """

        html = _email_template("Interview Completed", None, body)

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
        body = f"""
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
        """

        html = _email_template("Thank You!", "Your interview has been submitted", body)

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
        body = f"""
            <p>Hi {candidate_name or 'there'},</p>
            <p><strong>{company_name}</strong> has invited you to complete a video interview for the <strong>{job_title}</strong> position.</p>
            <p>This is an asynchronous video interview — you can complete it at any time that works for you. Here's what to expect:</p>
            <ul>
                <li>5 questions to answer on video</li>
                <li>Up to 2 minutes per question</li>
                <li>You can re-record your answers before submitting</li>
                <li>Total time: approximately 15–20 minutes</li>
            </ul>
            <p style="text-align: center; margin: 32px 0;">
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
        """

        html = _email_template("You're Invited!", "Complete your video interview", body)

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
        header_titles = {
            "interview_request": "Interview Request",
            "shortlist_notice": "Good News!",
            "rejection": "Application Update",
            "custom": "Message from Employer",
        }
        header_title = header_titles.get(message_type, "Message from Employer")
        job_info = f" regarding <strong>{job_title}</strong>" if job_title else ""

        email_body = f"""
            <p>Hi {candidate_name},</p>
            <p><strong>{employer_name}</strong> has sent you a message{job_info}:</p>
            <div class="message-box">
                <p style="margin-top: 0; font-weight: 500; color: #1c1917; font-size: 15px;">{subject}</p>
                <div style="white-space: pre-wrap; color: #44403c; font-size: 14px;">{body}</div>
            </div>
            <p>If you have any questions, please reply directly to the employer.</p>
            <p>Best regards,<br>The Pathway Team</p>
        """

        html = _email_template(header_title, None, email_body, "This message was sent via Pathway career platform.")

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

        body = f"""
            <p>Hi {name},</p>
            <p>Thank you for joining Pathway! Please click the button below to verify your email address and complete your registration.</p>
            <p style="text-align: center; margin: 32px 0;">
                <a href="{verify_url}" class="button">Verify Email</a>
            </p>
            <p class="muted">
                If the button doesn't work, copy this link to your browser:<br>
                <a href="{verify_url}" class="link" style="word-break: break-all; font-size: 13px;">{verify_url}</a>
            </p>
            <p class="muted" style="margin-top: 20px;">This link will expire in 24 hours.</p>
            <p>Best regards,<br>The Pathway Team</p>
        """

        html = _email_template("Verify Your Email", "Welcome to Pathway", body, "If you didn't sign up for Pathway, please ignore this email.")

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

        body = f"""
            <p>Hi {name},</p>
            <p>We received a request to reset your password. Click the button below to create a new password:</p>
            <p style="text-align: center; margin: 32px 0;">
                <a href="{reset_url}" class="button">Reset Password</a>
            </p>
            <div class="warning">
                <strong>This link will expire in 1 hour.</strong>
                If you didn't request a password reset, you can safely ignore this email.
            </div>
            <p class="muted">
                If the button doesn't work, copy this link to your browser:<br>
                <a href="{reset_url}" class="link" style="word-break: break-all; font-size: 13px;">{reset_url}</a>
            </p>
            <p>Best regards,<br>The Pathway Team</p>
        """

        html = _email_template("Reset Your Password", None, body, "If you didn't request this, please ignore this email.")

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
            steps = """
                <ol style="line-height: 2;">
                    <li><strong>Complete your profile</strong> — Add your education, upload your resume</li>
                    <li><strong>Connect GitHub</strong> — Showcase your projects and contributions</li>
                    <li><strong>Take your first interview</strong> — Answer 5 questions to get your score</li>
                    <li><strong>Get matched</strong> — Employers will find you based on your trajectory</li>
                </ol>
            """
            cta_text = "Go to Dashboard"
            tip = """
                <div class="callout">
                    <strong>Pro tip:</strong> Students who complete their profile within 24 hours are 3x more likely to get matched with employers.
                </div>
            """
            intro = "Welcome to <strong>Pathway</strong>! We're excited to help you land your first job."
            subject = "Welcome to Pathway - Let's Get Started!"
        else:
            dashboard_url = f"{settings.frontend_url}/employer/dashboard"
            steps = """
                <ol style="line-height: 2;">
                    <li><strong>Browse the talent pool</strong> — See candidates ranked by AI-scored interviews</li>
                    <li><strong>Create job postings</strong> — Get auto-matched with relevant candidates</li>
                    <li><strong>Review interviews</strong> — Watch video responses and see detailed scoring</li>
                    <li><strong>Contact candidates</strong> — Reach out to your top picks directly</li>
                </ol>
            """
            cta_text = "Explore Talent Pool"
            tip = """
                <div class="callout">
                    <strong>What makes Pathway different:</strong> Unlike traditional resumes, you can see candidates' growth over time. Watch how they improve interview-to-interview over 2-4 years of college.
                </div>
            """
            intro = "Welcome to <strong>Pathway</strong>! We're excited to help you find exceptional early-career talent."
            subject = "Welcome to Pathway - Find Your Next Hire"

        body = f"""
            <p>Hi {name},</p>
            <p>{intro}</p>
            <p>Here's how to get started:</p>
            {steps}
            <p style="text-align: center; margin: 32px 0;">
                <a href="{dashboard_url}" class="button">{cta_text}</a>
            </p>
            {tip}
            <p>Questions? Just reply to this email — we're here to help!</p>
            <p>Best regards,<br>The Pathway Team</p>
        """

        html = _email_template("Welcome to Pathway", "Show your growth, land your first job", body, "You're receiving this because you signed up for Pathway.")

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

        body = f"""
            <p>Hi {name},</p>
            <p>You signed up for Pathway {days_since_signup} days ago, but haven't completed your first interview yet.</p>
            <div class="stat">
                <div class="stat-number">15</div>
                <div class="stat-label">minutes to complete</div>
            </div>
            <p>Your first interview is just 5 video questions. Once complete:</p>
            <ul>
                <li>Get your AI-scored profile</li>
                <li>Become visible to employers</li>
                <li>Start tracking your growth over time</li>
            </ul>
            <p style="text-align: center; margin: 32px 0;">
                <a href="{dashboard_url}" class="button">Start Interview Now</a>
            </p>
            <p>Best regards,<br>The Pathway Team</p>
        """

        html = _email_template(
            "You're Almost There!", None, body,
            f'Don\'t want these reminders? <a href="{settings.frontend_url}/unsubscribe" style="color: #78716c;">Unsubscribe</a>'
        )

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

        body = f"""
            <p>Hi {name},</p>
            <p><strong>{employer_name}</strong> viewed your profile{job_info}.</p>
            <p>This is a good sign! Make sure your profile is complete and up-to-date to increase your chances of getting contacted.</p>
            <p style="text-align: center; margin: 32px 0;">
                <a href="{dashboard_url}" class="button">View Your Profile</a>
            </p>
            <p>Best regards,<br>The Pathway Team</p>
        """

        html = _email_template(
            "Someone's Interested!", None, body,
            f'Manage notification preferences in your <a href="{settings.frontend_url}/candidate/settings" style="color: #78716c;">settings</a>.'
        )

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
                <div class="callout">
                    <strong>You're eligible for a new monthly interview!</strong>
                    <br>Take it to show your growth and improve your score.
                </div>
            """

        body = f"""
            <p>Hi {name},</p>
            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 24px 0;">
                <tr>
                    <td width="50%" style="padding: 0 6px 0 0;">
                        <div class="stat" style="margin: 0;">
                            <div class="stat-number">{profile_views}</div>
                            <div class="stat-label">Profile Views</div>
                        </div>
                    </td>
                    <td width="50%" style="padding: 0 0 0 6px;">
                        <div class="stat" style="margin: 0;">
                            <div class="stat-number">{new_matches}</div>
                            <div class="stat-label">New Matches</div>
                        </div>
                    </td>
                </tr>
            </table>
            {interview_cta}
            <p style="text-align: center; margin: 32px 0;">
                <a href="{dashboard_url}" class="button">View Dashboard</a>
            </p>
            <p>Keep showing your growth!</p>
            <p>Best regards,<br>The Pathway Team</p>
        """

        html = _email_template(
            "Your Weekly Update", "Here's what happened this week", body,
            f'Manage notification preferences in your <a href="{settings.frontend_url}/candidate/settings" style="color: #78716c;">settings</a>.'
        )

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
                <p style="text-align: center; margin: 24px 0;">
                    <a href="{google_meet_link}" class="button-teal">Join Google Meet</a>
                </p>
                <p class="muted" style="text-align: center;">
                    Meeting link: <a href="{google_meet_link}" class="link" style="font-size: 13px;">{google_meet_link}</a>
                </p>
            """

        body = f"""
            <p>Hi {candidate_name},</p>
            <p>This is a reminder that your interview with <strong>{company_name}</strong> is coming up {time_text}.</p>
            <div class="details">
                <p><strong>Interview:</strong> {interview_title}</p>
                <p><strong>Date:</strong> {formatted_date}</p>
                <p><strong>Time:</strong> {formatted_time}</p>
                <p><strong>Duration:</strong> {duration_minutes} minutes</p>
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
        """

        html = _email_template("Interview Reminder", f"Your interview is {time_text}", body)

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
                <p style="text-align: center; margin: 24px 0;">
                    <a href="{google_meet_link}" class="button-teal">Join Google Meet</a>
                </p>
            """

        body = f"""
            <p>Hi,</p>
            <p>This is a reminder that you have an interview scheduled {time_text}.</p>
            <div class="details">
                <p><strong>Candidate:</strong> {candidate_name}</p>
                <p><strong>Interview:</strong> {interview_title}</p>
                <p><strong>Date:</strong> {formatted_date}</p>
                <p><strong>Time:</strong> {formatted_time}</p>
                <p><strong>Duration:</strong> {duration_minutes} minutes</p>
            </div>
            {meet_link_html}
            <p>Best regards,<br>The Pathway Team</p>
        """

        html = _email_template("Interview Reminder", f"Upcoming interview {time_text}", body)

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
                <p style="text-align: center; margin: 24px 0;">
                    <a href="{google_meet_link}" class="button-teal">Add to Calendar</a>
                </p>
                <p class="muted" style="text-align: center;">
                    Google Meet link: <a href="{google_meet_link}" class="link" style="font-size: 13px;">{google_meet_link}</a>
                </p>
            """

        body = f"""
            <p>Hi {candidate_name},</p>
            <p>Great news! Your interview with <strong>{company_name}</strong> has been confirmed.</p>
            <div class="details">
                <p><strong>Interview:</strong> {interview_title}</p>
                <p><strong>Date:</strong> {formatted_date}</p>
                <p><strong>Time:</strong> {formatted_time}</p>
                <p><strong>Duration:</strong> {duration_minutes} minutes</p>
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
        """

        html = _email_template("Interview Confirmed!", "Your interview has been scheduled", body, f"Need to reschedule? Please contact {company_name} directly.")

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
                <p style="text-align: center; margin: 24px 0;">
                    <a href="{dashboard_url}" class="button">View in Dashboard</a>
                </p>
            """

        body = f"""
            <p>Hi,</p>
            <p>A new interview has been scheduled with a candidate.</p>
            <div class="details">
                <p><strong>Candidate:</strong> {candidate_name}</p>
                <p><strong>Email:</strong> {candidate_email}</p>
                <p><strong>Interview:</strong> {interview_title}</p>
                <p><strong>Date:</strong> {formatted_date}</p>
                <p><strong>Time:</strong> {formatted_time}</p>
                <p><strong>Duration:</strong> {duration_minutes} minutes</p>
            </div>
            {dashboard_html}
            <p>A calendar invite has been sent to your email.</p>
            <p>Best regards,<br>The Pathway Team</p>
        """

        html = _email_template("New Interview Scheduled", None, body)

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
        custom_message = f'<div class="message-box"><div style="white-space: pre-wrap; font-size: 14px; color: #44403c;">{message}</div></div>' if message else ""

        body = f"""
            <p>Hi {candidate_name or 'there'},</p>
            <p><strong>{company_name}</strong> would like to schedule an interview with you{job_info}.</p>
            {custom_message}
            <p>Please use the link below to select a time that works best for you:</p>
            <p style="text-align: center; margin: 32px 0;">
                <a href="{schedule_url}" class="button">Schedule Interview</a>
            </p>
            <p class="muted">
                Or copy this link: <a href="{schedule_url}" class="link" style="font-size: 13px;">{schedule_url}</a>
            </p>
            <p>We look forward to speaking with you!</p>
            <p>Best regards,<br>The {company_name} Team</p>
        """

        html = _email_template("Schedule Your Interview", "Pick a time that works for you", body, "This invitation was sent via Pathway.")

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

        body = f"""
            <p>Hi there,</p>
            <p><strong>{inviter_name}</strong> has invited you to join <strong>{organization_name}</strong> on Pathway.</p>
            <p>
                Your role: <span class="badge">{role.replace('_', ' ').title()}</span>
                <br>
                <span class="muted">{role_desc}</span>
            </p>
            <p>Pathway is a collaborative recruiting platform that helps teams find and hire top talent from college students.</p>
            <p style="text-align: center; margin: 32px 0;">
                <a href="{invite_url}" class="button">Accept Invitation</a>
            </p>
            <p class="muted">This invitation expires in 7 days. If you didn't expect this email, you can safely ignore it.</p>
        """

        html = _email_template("You're Invited!", None, body, "Pathway — Collaborative Recruiting Platform")

        return self.send_email(
            to=to_email,
            subject=f"[Pathway] {inviter_name} invited you to join {organization_name}",
            html=html,
        )

    def send_profile_nudge(
        self,
        to: str,
        candidate_name: str,
        nudge_type: str,  # "resume", "github", or "transcript"
    ) -> Optional[str]:
        """
        Send a nudge email to a candidate to complete their profile.

        Args:
            to: Candidate's email address
            candidate_name: Candidate's name
            nudge_type: Type of nudge - "resume", "github", or "transcript"

        Returns:
            Email ID if successful, None otherwise
        """
        dashboard_url = f"{settings.frontend_url}/candidate/dashboard"

        # Content based on nudge type
        nudge_content = {
            "resume": {
                "subject": "Complete your profile - Upload your resume",
                "header_title": "Upload Your Resume",
                "header_subtitle": "Stand out to top employers",
                "action_text": "Upload Resume",
                "benefit": "Candidates with resumes are <strong>3x more likely</strong> to be contacted by recruiters.",
                "details": [
                    "Takes less than 2 minutes",
                    "Auto-extracts your skills and experience",
                    "Makes you visible to our employer partners",
                ],
            },
            "github": {
                "subject": "Complete your profile - Connect your GitHub",
                "header_title": "Connect Your GitHub",
                "header_subtitle": "Showcase your coding skills",
                "action_text": "Connect GitHub",
                "benefit": "Candidates with GitHub profiles get <strong>2x higher</strong> interview scores on average.",
                "details": [
                    "One-click OAuth connection",
                    "We analyze your code quality and contributions",
                    "Shows employers your real-world experience",
                ],
            },
            "transcript": {
                "subject": "Complete your profile - Upload your transcript",
                "header_title": "Upload Your Transcript",
                "header_subtitle": "Verify your academic excellence",
                "action_text": "Upload Transcript",
                "benefit": "Verified transcripts help you stand out for <strong>competitive roles</strong>.",
                "details": [
                    "Unofficial transcripts are accepted",
                    "We extract GPA and relevant coursework",
                    "Helps match you with the right opportunities",
                ],
            },
        }

        content = nudge_content.get(nudge_type)
        if not content:
            logger.error(f"Invalid nudge type: {nudge_type}")
            return None

        first_name = candidate_name.split()[0] if candidate_name else "there"

        details_html = "".join([f"<li>{d}</li>" for d in content["details"]])

        body = f"""
            <p>Hi {first_name},</p>

            <p>We noticed your Pathway profile is missing your {nudge_type}. Adding it takes just a few minutes and can significantly boost your chances of landing great opportunities!</p>

            <div class="callout">
                <strong>Why it matters:</strong><br>
                {content["benefit"]}
            </div>

            <p><strong>It's quick and easy:</strong></p>
            <ul>
                {details_html}
            </ul>

            <p style="text-align: center; margin: 32px 0;">
                <a href="{dashboard_url}" class="button-teal">{content["action_text"]}</a>
            </p>

            <hr class="divider">

            <p class="muted">Companies are actively searching for candidates like you. Don't miss out on opportunities because of an incomplete profile!</p>
        """

        html = _email_template(
            content["header_title"],
            content["header_subtitle"],
            body,
            "Pathway — Your Career, Your Way"
        )

        return self.send_email(
            to=to,
            subject=f"[Pathway] {content['subject']}",
            html=html,
        )


# Global instance
email_service = EmailService()
