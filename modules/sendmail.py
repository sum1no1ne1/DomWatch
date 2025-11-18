import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()   # Load .env both locally & on Render

# Read environment variables
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

folder_path = "screenshots"

def sendemail(wmail, nwmail):
    try:
        # Login to SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)

            msg = EmailMessage()
            msg['Subject'] = 'List of Working Domains'
            msg['From'] = SENDER_EMAIL
            
            # You can keep these static OR move them to .env later
            msg['To'] = [
                'denverfds@gmail.com',
                'shanicefdes14@gmail.com',
                'bhaveshdeshmukh17@gmail.com'
            ]

            # Convert domain dicts → lists
            working_list = [item["domain_name"] for item in wmail]
            not_working_list = [item["domain_name"] for item in nwmail]

            # Email body
            body = "This PDF contains images of the domains that are working.\n\n"
            body += "List of Working Domains:\n" + "\n".join(working_list) + "\n\n"
            body += "List of Not Working Domains:\n" + "\n".join(not_working_list) + "\n"

            msg.set_content(body)

            # Attach PDFs from screenshots folder
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    if filename.lower().endswith(".pdf"):
                        file_path = os.path.join(folder_path, filename)
                        with open(file_path, "rb") as f:
                            msg.add_attachment(
                                f.read(),
                                maintype="application",
                                subtype="pdf",
                                filename=filename
                            )

            smtp.send_message(msg)
            return "Email sent successfully!"

    except Exception as e:
        return f"Failed to send email: {e}"
