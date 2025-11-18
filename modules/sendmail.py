import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
FOLDER_PATH = "screenshots"
PDF_NAME = "output.pdf"

def sendemail(working_domains, not_working_domains):
    try:
        pdf_path = os.path.join(FOLDER_PATH, PDF_NAME)
        if not os.path.exists(pdf_path):
            return "PDF not found. Nothing to send."

        # Compose email
        msg = EmailMessage()
        msg['Subject'] = 'Domain Verification Results'
        msg['From'] = SENDER_EMAIL
        msg['To'] = ['denverfds@gmail.com']  # Replace with actual recipients

        body = "This PDF contains screenshots of all working domains.\n\n"
        body += "List of Working Domains:\n" + "\n".join([d["domain_name"] for d in working_domains]) + "\n\n"
        body += "List of Not Working Domains:\n" + "\n".join([d["domain_name"] for d in not_working_domains])
        msg.set_content(body)

        # Attach the PDF
        with open(pdf_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=PDF_NAME)

        # Send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)

        return "Email sent successfully with all screenshots."

    except Exception as e:
        return f"Failed to send email: {e}"

