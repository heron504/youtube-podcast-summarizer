"""
Email sender for PDF reports
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

class EmailSender:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_report(self, to_email, pdf_path, subject=None):
        """Send PDF report via email"""
        if not subject:
            subject = f"AI科技播客每日摘要 - {datetime.now().strftime('%Y年%m月%d日')}"

        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to_email
        msg['Subject'] = subject

        # Email body
        body = f"""
        您好！

        这是您订阅的AI科技播客每日摘要报告。

        报告包含了今日最新的YouTube订阅频道视频内容摘要，
        通过Gemini AI智能分析生成，帮助您快速了解技术动态。

        请查看附件中的PDF报告。

        报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        祝您学习愉快！
        """

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # Attach PDF if it exists
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(pdf_path)}'
            )
            msg.attach(part)

        try:
            # Connect to server and send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable security
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.username, to_email, text)
            server.quit()

            print(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    @staticmethod
    def get_gmail_config():
        """Get Gmail SMTP configuration"""
        return {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587
        }

    @staticmethod
    def get_outlook_config():
        """Get Outlook SMTP configuration"""
        return {
            'smtp_server': 'smtp-mail.outlook.com',
            'smtp_port': 587
        }

    @staticmethod
    def get_qq_config():
        """Get QQ Mail SMTP configuration"""
        return {
            'smtp_server': 'smtp.qq.com',
            'smtp_port': 587
        }