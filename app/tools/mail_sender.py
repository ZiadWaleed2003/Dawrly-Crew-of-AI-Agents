import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv

def send_email(to_email,html_file_path="./results/final_result.html"):

    """
        this function is used to send an email to the user containing the results of the Dawrly Crew 
        it send it as an HTML to be directly rendered from the user
        and it send the actual file aswell !
    """

    # loading password and email from the .env file 
    load_dotenv()
    from_email = os.getenv('EMAIL')
    password   = os.getenv('EMAIL_PASSWORD')

    html_content = read_file_content(html_file_path)
    if not html_content:
        return False
   
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Job Report (Dawrly Crew)'
    msg['From'] = from_email
    msg['To'] = to_email
   
    # Attach HTML content as email body
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)
    
    # Attach the HTML file
    with open(html_file_path, "rb") as file:
        attachment = MIMEApplication(file.read(), Name=os.path.basename(html_file_path))
    
    attachment['Content-Disposition'] = f'attachment; filename="{os.path.basename(html_file_path)}"'
    msg.attach(attachment)
   
    # Send via Gmail SMTP
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def read_file_content(file_path="./results/final_result.html"):
    # Read the HTML content from the file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
            return html_content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False