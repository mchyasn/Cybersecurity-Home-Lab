import http.server
import socketserver
import urllib.parse
import smtplib
from email.message import EmailMessage

# Configuration
PORT = 8000
EMAIL_ADDRESS = "redacted"  # Your Gmail address
EMAIL_PASSWORD = "gylf uqju ibcx ulco"  # Your Gmail app password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


class CanaryTokenHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/canary":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Nothing to see here!")

            # Extract information about the requester
            ip = self.client_address[0]
            user_agent = self.headers.get('User-Agent')

            # Send alert email
            self.send_alert_email(ip, user_agent)
        else:
            super().do_GET()

    def send_alert_email(self, ip, user_agent):
        msg = EmailMessage()
        msg.set_content(f"Canary token triggered!\nIP: {ip}\nUser-Agent: {user_agent}")
        msg['Subject'] = "Canary Token Alert"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), CanaryTokenHandler) as httpd:
        print(f"Serving canary token at http://localhost:{PORT}/canary")
        httpd.serve_forever()