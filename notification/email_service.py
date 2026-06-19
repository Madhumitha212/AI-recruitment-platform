import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailService:

    @staticmethod
    def send_shortlist_email(
        candidate_email: str,
        candidate_name: str,
        match_percentage: float
    ):

        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")

        if not sender_email or not sender_password:
            print("Email credentials missing")
            return

        subject = "Application Status Update"

        body = f"""
            Hello {candidate_name},

            Congratulations!

            Your profile has been shortlisted for the next stage of the recruitment process.

            Match Score: {match_percentage}%

            Our team will contact you soon regarding further rounds.

            Best Regards,
            AI Recruitment Team
            """

        try:

            msg = MIMEMultipart()

            msg["From"] = sender_email
            msg["To"] = candidate_email
            msg["Subject"] = subject

            msg.attach(
                MIMEText(body, "plain")
            )

            server = smtplib.SMTP(
                "smtp.gmail.com",
                587
            )

            server.starttls()

            server.login(
                sender_email,
                sender_password
            )

            server.sendmail(
                sender_email,
                candidate_email,
                msg.as_string()
            )

            server.quit()

            print(
                f"Email sent to {candidate_email}"
            )

        except Exception as e:

            print(
                f"Email sending failed: {e}"
            )