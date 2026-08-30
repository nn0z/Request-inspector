# Request Inspector

**Request Inspector** is an advanced web traffic security tool built with Python and Playwright, designed to inspect outgoing and incoming HTTP/HTTPS requests, analyze endpoint behavior, and assist in vulnerability assessment and bug bounty hunting.

---

## 🚀 Key Features

- **Automated Target Crawling:** Launches a headless browser to navigate websites and map out hidden endpoints and assets automatically.
- **Interactive Element Simulation:** Automatically fills input forms, simulates user clicks, and triggers background actions to uncover obscured requests.
- **Traffic Categorization:** Captures and sorts live traffic by HTTP methods (`GET`, `POST`, `PUT`, `DELETE`, etc.) to streamline analysis.
- **Headers & Payload Inspection:** Analyzes full request headers, examines incoming and outgoing body data, and tracks custom payloads sent during form submissions and user interactions.
- **Built-in Repeater:** Select any captured request, modify its method, URL, headers, or body, and resend it to the server to test for vulnerabilities.
- **Response Viewer:** Displays detailed server responses including status codes, response headers, and formatted body content (JSON/HTML).
- **Color-Coded Output:** Easy-to-read terminal output with color coding for different HTTP methods and response statuses.

---

## 🛠️ Requirements & Installation

Make sure you have Python 3 installed along with the required Playwright dependency:

```
pip install playwright
playwright install
```

---

## Disclaimer
Request Inspector is developed for authorized penetration testing, security auditing, and bug bounty hunting only.
The authors assume no liability and are not responsible for any misuse or damage caused by this program.
Always ensure you have explicit written permission from the target system owner before scanning.
