from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import smtplib
from email.mime.text import MIMEText
import os

app = FastAPI()


# Define the expected JSON model
class EmailData(BaseModel):
    p_to: List[str]
    p_cc: List[str]
    p_subj: str
    p_body: str


@app.post("/v1/emailTrigger")
async def email_trigger(data: EmailData):

    msg = MIMEText(data.p_body, "html")
    msg["Subject"] = data.p_subj

    # Sender email address
    # Configure the actual email address using an environment variable.
    msg["From"] = os.getenv("EMAIL_FROM")

    msg["To"] = ", ".join(data.p_to)
    msg["Cc"] = ", ".join(data.p_cc)

    # SMTP sending
    try:
        # SMTP server and port should be configured
        # in the server environment.
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))

        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()

            # SMTP authentication
            server.login(
                smtp_username,
                smtp_password
            )

            server.sendmail(
                msg["From"],
                data.p_to + data.p_cc,
                msg.as_string()
            )

        return {
            "status": "success",
            "message": "Email sent"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
