# REQUEST INSPECTOR v2.2
from collections import defaultdict
import threading
import time
import json
from playwright.sync_api import sync_playwright
import requests
from urllib.parse import urlparse

COLORS = {
    "GET": "\033[92m",
    "POST": "\033[94m",
    "PUT": "\033[93m",
    "DELETE": "\033[91m",
    "PATCH": "\033[96m",
    "OTHER": "\033[95m",
    "CYAN": "\033[96m",
    "GRAY": "\033[90m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m",
    "UNDERLINE": "\033[4m",
}


class Repeater:
    def __init__(self, captured_requests):
        self.requests = captured_requests
        self.session = requests.Session()

    def show_repeater_menu(self):
        while True:
            print(f"""
{COLORS['CYAN']}{COLORS['BOLD']}┌──[ {COLORS['YELLOW']}REPEATER MODE{COLORS['CYAN']} ]─────────────────────────────────────┐{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['CYAN']}❖{COLORS['RESET']} {COLORS['CYAN']}{COLORS['BOLD']}[1]{COLORS['RESET']} {COLORS['CYAN']}Select Request by ID{COLORS['RESET']}                                 {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['CYAN']}❖{COLORS['RESET']} {COLORS['CYAN']}{COLORS['BOLD']}[2]{COLORS['RESET']} {COLORS['CYAN']}View All Requests{COLORS['RESET']}                                    {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['RED']}✖{COLORS['RESET']} {COLORS['RED']}{COLORS['BOLD']}[3]{COLORS['RESET']} {COLORS['RED']}Exit Repeater{COLORS['RESET']}                                          {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}└────────────────────────────────────────────────────────────┘{COLORS['RESET']}
""")
            choice = input(f"{COLORS['CYAN']}└──> {COLORS['BOLD']}Your choice :{COLORS['RESET']} ").strip()

            if choice == "1":
                self.select_and_send_request()
            elif choice == "2":
                self.view_all_requests()
            elif choice == "3":
                print(f"\n{COLORS['CYAN']}►{COLORS['RESET']} {COLORS['DIM']}Exiting Repeater{COLORS['RESET']}")
                break
            else:
                print(f"\n{COLORS['RED']}✖{COLORS['RESET']} Invalid choice")
                time.sleep(1)

    def view_all_requests_with_selection(self):
        while True:
            print(f"\n{COLORS['CYAN']}{COLORS['BOLD']}{'=' * 70}{COLORS['RESET']}")
            print(f"{COLORS['CYAN']}{COLORS['BOLD']}  AVAILABLE REQUESTS{COLORS['RESET']}")
            print(f"{COLORS['CYAN']}{COLORS['BOLD']}{'=' * 70}{COLORS['RESET']}")

            for idx, req in enumerate(self.requests, 1):
                method = req['method']
                method_color = COLORS.get(method, COLORS['OTHER'])
                url_short = req['url'][:60] + '...' if len(req['url']) > 60 else req['url']
                print(
                    f"{COLORS['GRAY']}│{COLORS['RESET']} {COLORS['BOLD']}[{idx}]{COLORS['RESET']} {method_color}{method}{COLORS['RESET']} → {url_short}")

            print(f"{COLORS['GRAY']}│{COLORS['RESET']}")
            print(
                f"{COLORS['GRAY']}│{COLORS['RESET']} {COLORS['RED']}{COLORS['BOLD']}[0]{COLORS['RESET']} {COLORS['RED']}↩ Back to Repeater Menu{COLORS['RESET']}")
            print(f"{COLORS['CYAN']}{COLORS['BOLD']}{'=' * 70}{COLORS['RESET']}")

            choice = input(
                f"\n{COLORS['CYAN']}└──> {COLORS['BOLD']}Enter Request ID :{COLORS['RESET']} ").strip()

            if choice == "0":
                print(
                    f"\n{COLORS['CYAN']}►{COLORS['RESET']} {COLORS['DIM']}Returning to Repeater menu...{COLORS['RESET']}")
                time.sleep(0.5)
                return

            try:
                idx = int(choice) - 1
                if idx < 0 or idx >= len(self.requests):
                    print(f"\n{COLORS['RED']}✖{COLORS['RESET']} Invalid Request ID")
                    time.sleep(1)
                    continue

                original_req = self.requests[idx]
                self.modify_and_send(original_req, idx)

            except ValueError:
                print(f"\n{COLORS['RED']}✖{COLORS['RESET']} Invalid input. Please enter a number")
                time.sleep(1)

    def view_all_requests(self):
        print(f"\n{COLORS['CYAN']}{COLORS['BOLD']}{'=' * 70}{COLORS['RESET']}")
        print(f"{COLORS['CYAN']}{COLORS['BOLD']}  AVAILABLE REQUESTS{COLORS['RESET']}")
        print(f"{COLORS['CYAN']}{COLORS['BOLD']}{'=' * 70}{COLORS['RESET']}")

        for idx, req in enumerate(self.requests, 1):
            method = req['method']
            method_color = COLORS.get(method, COLORS['OTHER'])
            url_short = req['url'][:60] + '...' if len(req['url']) > 60 else req['url']
            print(
                f"{COLORS['GRAY']}│{COLORS['RESET']} {COLORS['BOLD']}[{idx}]{COLORS['RESET']} {method_color}{method}{COLORS['RESET']} → {url_short}")
        print()
        time.sleep(2)

    def select_and_send_request(self):
        req_id = input(f"\n{COLORS['CYAN']}└──> {COLORS['BOLD']}Enter Request ID :{COLORS['RESET']} ").strip()

        try:
            idx = int(req_id) - 1
            if idx < 0 or idx >= len(self.requests):
                print(f"\n{COLORS['RED']}✖{COLORS['RESET']} Invalid Request ID")
                time.sleep(1)
                return

            original_req = self.requests[idx]
            self.modify_and_send(original_req, idx)

        except ValueError:
            print(f"\n{COLORS['RED']}✖{COLORS['RESET']} Invalid input. Please enter a number")
            time.sleep(1)

    def modify_and_send(self, original_req, idx):
        print(
            f"\n{COLORS['CYAN']}{COLORS['BOLD']}╔═══════════════════════════════════════════════════════╗{COLORS['RESET']}")
        print(
            f"{COLORS['CYAN']}║{COLORS['RESET']}  {COLORS['BOLD']}ORIGINAL REQUEST #{idx + 1}{COLORS['RESET']}                              {COLORS['CYAN']}║{COLORS['RESET']}")
        print(f"{COLORS['CYAN']}╚═══════════════════════════════════════════════════════╝{COLORS['RESET']}")

        method_color = COLORS.get(original_req['method'], COLORS['OTHER'])
        print(f"\n{COLORS['BOLD']}Method:{COLORS['RESET']} {method_color}{original_req['method']}{COLORS['RESET']}")
        print(f"{COLORS['BOLD']}URL:{COLORS['RESET']} {original_req['url']}")
        print(f"\n{COLORS['BOLD']}Headers:{COLORS['RESET']}")
        for h, v in original_req['headers'].items():
            print(f"  {COLORS['DIM']}{h}:{COLORS['RESET']} {v}")

        if original_req.get('post_data'):
            print(f"\n{COLORS['BOLD']}Body:{COLORS['RESET']}")
            print(f"  {COLORS['YELLOW']}{original_req['post_data']}{COLORS['RESET']}")

        print(f"""
{COLORS['CYAN']}{COLORS['BOLD']}┌──[ {COLORS['YELLOW']}MODIFY REQUEST{COLORS['CYAN']} ]──────────────────────────────────┐{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['CYAN']}❖{COLORS['RESET']} {COLORS['CYAN']}{COLORS['BOLD']}[1]{COLORS['RESET']} {COLORS['CYAN']}Send Original Request{COLORS['RESET']}                            {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['CYAN']}❖{COLORS['RESET']} {COLORS['CYAN']}{COLORS['BOLD']}[2]{COLORS['RESET']} {COLORS['CYAN']}Modify URL{COLORS['RESET']}                                        {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['CYAN']}❖{COLORS['RESET']} {COLORS['CYAN']}{COLORS['BOLD']}[3]{COLORS['RESET']} {COLORS['CYAN']}Modify Method{COLORS['RESET']}                                     {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['CYAN']}❖{COLORS['RESET']} {COLORS['CYAN']}{COLORS['BOLD']}[4]{COLORS['RESET']} {COLORS['CYAN']}Modify Headers (Add/Edit/Remove){COLORS['RESET']}                {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['CYAN']}❖{COLORS['RESET']} {COLORS['CYAN']}{COLORS['BOLD']}[5]{COLORS['RESET']} {COLORS['CYAN']}Modify Body/Data{COLORS['RESET']}                                 {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['GREEN']}❖{COLORS['RESET']} {COLORS['GREEN']}{COLORS['BOLD']}[6]{COLORS['RESET']} {COLORS['GREEN']}Send Request{COLORS['RESET']}                                    {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['RED']}✖{COLORS['RESET']} {COLORS['RED']}{COLORS['BOLD']}[7]{COLORS['RESET']} {COLORS['RED']}Cancel{COLORS['RESET']}                                              {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}└────────────────────────────────────────────────────────────┘{COLORS['RESET']}
""")

        modified = original_req.copy()

        while True:
            choice = input(f"{COLORS['CYAN']}└──> {COLORS['BOLD']}Your choice :{COLORS['RESET']} ").strip()

            if choice == "1":
                self.send_request(original_req)
                break

            elif choice == "2":
                new_url = input(f"{COLORS['CYAN']}└──> {COLORS['BOLD']}New URL :{COLORS['RESET']} ").strip()
                if new_url:
                    modified['url'] = new_url
                    print(f"{COLORS['GREEN']}✓{COLORS['RESET']} URL updated")

            elif choice == "3":
                print(
                    f"\n{COLORS['DIM']}Available methods: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS{COLORS['RESET']}")
                new_method = input(
                    f"{COLORS['CYAN']}└──> {COLORS['BOLD']}New Method :{COLORS['RESET']} ").strip().upper()
                if new_method:
                    modified['method'] = new_method
                    print(f"{COLORS['GREEN']}✓{COLORS['RESET']} Method updated")

            elif choice == "4":
                self.modify_headers(modified)

            elif choice == "5":
                print(f"\n{COLORS['DIM']}Current body:{COLORS['RESET']}")
                print(f"{COLORS['YELLOW']}{modified.get('post_data', 'No body')}{COLORS['RESET']}")
                new_body = input(
                    f"\n{COLORS['CYAN']}└──> {COLORS['BOLD']}New Body (or empty to remove) :{COLORS['RESET']} ")
                if new_body.strip():
                    modified['post_data'] = new_body
                    print(f"{COLORS['GREEN']}✓{COLORS['RESET']} Body updated")
                else:
                    modified['post_data'] = None
                    print(f"{COLORS['GREEN']}✓{COLORS['RESET']} Body removed")

            elif choice == "6":
                self.send_request(modified)
                break

            elif choice == "7":
                print(f"\n{COLORS['CYAN']}►{COLORS['RESET']} {COLORS['DIM']}Operation cancelled{COLORS['RESET']}")
                time.sleep(1)
                break

            else:
                print(f"\n{COLORS['RED']}✖{COLORS['RESET']} Invalid choice")
                time.sleep(1)

    def modify_headers(self, modified):
        print(f"\n{COLORS['CYAN']}╔═══════════════════════════════════════════════════════╗{COLORS['RESET']}")
        print(
            f"{COLORS['CYAN']}║{COLORS['RESET']}  {COLORS['BOLD']}CURRENT HEADERS{COLORS['RESET']}                                   {COLORS['CYAN']}║{COLORS['RESET']}")
        print(f"{COLORS['CYAN']}╚═══════════════════════════════════════════════════════╝{COLORS['RESET']}")

        headers = modified.get('headers', {})
        for h, v in headers.items():
            print(f"  {COLORS['BOLD']}{h}:{COLORS['RESET']} {v}")

        print(f"""
{COLORS['CYAN']}╔═══════════════════════════════════════════════════════╗{COLORS['RESET']}
{COLORS['CYAN']}║{COLORS['RESET']}  {COLORS['CYAN']}{COLORS['BOLD']}[A]{COLORS['RESET']} Add Header  {COLORS['CYAN']}{COLORS['BOLD']}[E]{COLORS['RESET']} Edit Header  {COLORS['CYAN']}{COLORS['BOLD']}[R]{COLORS['RESET']} Remove Header {COLORS['CYAN']}║{COLORS['RESET']}
{COLORS['CYAN']}║{COLORS['RESET']}  {COLORS['GREEN']}{COLORS['BOLD']}[D]{COLORS['RESET']} Done                                    {COLORS['CYAN']}║{COLORS['RESET']}
{COLORS['CYAN']}╚═══════════════════════════════════════════════════════╝{COLORS['RESET']}
""")

        while True:
            header_choice = input(
                f"{COLORS['CYAN']}└──> {COLORS['BOLD']}Your choice :{COLORS['RESET']} ").strip().upper()

            if header_choice == "A":
                key = input(f"{COLORS['CYAN']}└──> {COLORS['BOLD']}Header Name :{COLORS['RESET']} ").strip()
                if key:
                    value = input(f"{COLORS['CYAN']}└──> {COLORS['BOLD']}Header Value :{COLORS['RESET']} ").strip()
                    if value:
                        modified['headers'][key] = value
                        print(f"{COLORS['GREEN']}✓{COLORS['RESET']} Header added")

            elif header_choice == "E":
                key = input(f"{COLORS['CYAN']}└──> {COLORS['BOLD']}Header Name to edit :{COLORS['RESET']} ").strip()
                if key in modified['headers']:
                    value = input(f"{COLORS['CYAN']}└──> {COLORS['BOLD']}New Value :{COLORS['RESET']} ").strip()
                    if value:
                        modified['headers'][key] = value
                        print(f"{COLORS['GREEN']}✓{COLORS['RESET']} Header updated")
                else:
                    print(f"{COLORS['RED']}✖{COLORS['RESET']} Header not found")

            elif header_choice == "R":
                key = input(f"{COLORS['CYAN']}└──> {COLORS['BOLD']}Header Name to remove :{COLORS['RESET']} ").strip()
                if key in modified['headers']:
                    del modified['headers'][key]
                    print(f"{COLORS['GREEN']}✓{COLORS['RESET']} Header removed")
                else:
                    print(f"{COLORS['RED']}✖{COLORS['RESET']} Header not found")

            elif header_choice == "D":
                break

            else:
                print(f"\n{COLORS['RED']}✖{COLORS['RESET']} Invalid choice")
                time.sleep(1)

    def send_request(self, req):
        print(
            f"\n{COLORS['CYAN']}{COLORS['BOLD']}╔═══════════════════════════════════════════════════════╗{COLORS['RESET']}")
        print(
            f"{COLORS['CYAN']}║{COLORS['RESET']}  {COLORS['BOLD']}SENDING REQUEST...{COLORS['RESET']}                               {COLORS['CYAN']}║{COLORS['RESET']}")
        print(f"{COLORS['CYAN']}╚═══════════════════════════════════════════════════════╝{COLORS['RESET']}")

        method = req['method']
        url = req['url']
        headers = req.get('headers', {})
        data = req.get('post_data')

        print(f"\n{COLORS['DIM']}→ {method} {url}{COLORS['RESET']}")

        try:
            clean_headers = {k: v for k, v in headers.items()
                             if k.lower() not in ['host', 'connection', 'content-length', 'content-encoding']}

            request_data = None
            if data:
                try:
                    request_data = json.loads(data)
                    response = self.session.request(method, url, headers=clean_headers, json=request_data, timeout=30)
                except:
                    if 'application/json' in headers.get('content-type', '').lower():
                        response = self.session.request(method, url, headers=clean_headers, data=data, timeout=30)
                    else:
                        response = self.session.request(method, url, headers=clean_headers, data=data, timeout=30)
            else:
                response = self.session.request(method, url, headers=clean_headers, timeout=30)

            self.display_response(response)

        except requests.exceptions.RequestException as e:
            print(f"\n{COLORS['RED']}✖{COLORS['RESET']} Error: {str(e)}")
            time.sleep(2)

        print(f"\n{COLORS['DIM']}↳ Returning to requests list...{COLORS['RESET']}")
        time.sleep(1.5)

    def display_response(self, response):
        print(
            f"\n{COLORS['GREEN']}{COLORS['BOLD']}╔═══════════════════════════════════════════════════════╗{COLORS['RESET']}")
        print(
            f"{COLORS['GREEN']}║{COLORS['RESET']}  {COLORS['BOLD']}RESPONSE{COLORS['RESET']}                                              {COLORS['GREEN']}║{COLORS['RESET']}")
        print(f"{COLORS['GREEN']}╚═══════════════════════════════════════════════════════╝{COLORS['RESET']}")

        status_color = COLORS['GREEN'] if 200 <= response.status_code < 300 else COLORS[
            'YELLOW'] if 300 <= response.status_code < 400 else COLORS['RED']
        print(
            f"\n{COLORS['BOLD']}Status:{COLORS['RESET']} {status_color}{response.status_code} {response.reason}{COLORS['RESET']}")
        print(f"{COLORS['BOLD']}Time:{COLORS['RESET']} {response.elapsed.total_seconds():.3f}s")

        print(f"\n{COLORS['BOLD']}Response Headers:{COLORS['RESET']}")
        for h, v in response.headers.items():
            print(f"  {COLORS['DIM']}{h}:{COLORS['RESET']} {v}")

        print(f"\n{COLORS['BOLD']}Response Body:{COLORS['RESET']}")
        try:
            content_type = response.headers.get('content-type', '').lower()

            if 'application/json' in content_type:
                body = response.json()
                print(f"  {COLORS['YELLOW']}{json.dumps(body, indent=2, ensure_ascii=False)}{COLORS['RESET']}")
            elif 'text' in content_type:
                body = response.text
                if len(body) > 2000:
                    body = body[:2000] + f"\n{COLORS['DIM']}... (truncated, {len(body)} total chars){COLORS['RESET']}"
                print(f"  {COLORS['YELLOW']}{body}{COLORS['RESET']}")
            else:
                print(f"  {COLORS['DIM']}[Binary or non-text content - Content-Type: {content_type}]{COLORS['RESET']}")
                print(f"  {COLORS['DIM']}Content length: {len(response.content)} bytes{COLORS['RESET']}")
        except:
            print(f"  {COLORS['YELLOW']}{response.text[:500]}{COLORS['RESET']}")


def print_banner():
    banner = f"""
{COLORS['CYAN']}{COLORS['BOLD']}
    ██╗ ███╗   ██╗ ███████╗ ██████╗  ███████╗  ██████╗ ████████╗  ██████╗  ██████╗ 
    ██║ ████╗  ██║ ██╔════╝ ██╔══██╗ ██╔════╝ ██╔════╝ ╚══██╔══╝ ██╔═══██╗ ██╔══██╗
    ██║ ██╔██╗ ██║ ███████╗ ██████╔╝ █████╗   ██║         ██║    ██║   ██║ ██████╔╝
    ██║ ██║╚██╗██║ ╚════██║ ██╔═══╝  ██╔══╝   ██║         ██║    ██║   ██║ ██╔══██╗
    ██║ ██║ ╚████║ ███████║ ██║      ███████╗ ╚██████╗    ██║    ╚██████╔╝ ██║  ██║
    ╚═╝ ╚═╝  ╚═══╝ ╚══════╝ ╚═╝      ╚══════╝  ╚═════╝    ╚═╝     ╚═════╝  ╚═╝  ╚═╝
                                      {COLORS['YELLOW']}[ v2.2 ]{COLORS['CYAN']}
╚═════════════════════════════════════════════════════════════════════════════════════╝{COLORS['RESET']}
"""
    print(banner)


def print_main_menu():
    menu = f"""
{COLORS['CYAN']}{COLORS['BOLD']}┌──[ {COLORS['YELLOW']}SELECT MODE{COLORS['CYAN']} ]──────────────────────────────────────┐{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['CYAN']}❖{COLORS['RESET']} {COLORS['CYAN']}{COLORS['BOLD']}[1]{COLORS['RESET']} {COLORS['CYAN']}View All Requests{COLORS['RESET']}                                    {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['CYAN']}❖{COLORS['RESET']} {COLORS['CYAN']}{COLORS['BOLD']}[2]{COLORS['RESET']} {COLORS['CYAN']}View GET Requests{COLORS['RESET']}                                    {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['CYAN']}❖{COLORS['RESET']} {COLORS['CYAN']}{COLORS['BOLD']}[3]{COLORS['RESET']} {COLORS['CYAN']}View POST Requests{COLORS['RESET']}                                   {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['CYAN']}❖{COLORS['RESET']} {COLORS['CYAN']}{COLORS['BOLD']}[4]{COLORS['RESET']} {COLORS['CYAN']}View Other Methods (PUT, DELETE, etc.){COLORS['RESET']}               {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['GREEN']}❖{COLORS['RESET']} {COLORS['GREEN']}{COLORS['BOLD']}[5]{COLORS['RESET']} {COLORS['GREEN']}Open Repeater{COLORS['RESET']}                                    {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['RED']}✖{COLORS['RESET']} {COLORS['RED']}{COLORS['BOLD']}[6]{COLORS['RESET']} {COLORS['RED']}Exit Tool{COLORS['RESET']}                                            {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}└────────────────────────────────────────────────────────────┘{COLORS['RESET']}
"""
    print(menu)


def inspect_page_requests(target_url):
    captured_requests = []
    method_counts = defaultdict(int)
    counts_lock = threading.Lock()

    with sync_playwright() as p:
        print(
            f"{COLORS['CYAN']}►{COLORS['RESET']} {COLORS['DIM']}Initializing headless browser engine...{COLORS['RESET']}")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        def log_request(request):
            method = request.method.upper()
            with counts_lock:
                method_counts[method] += 1

            captured_requests.append({
                "method": method,
                "url": request.url,
                "headers": dict(request.headers),
                "post_data": request.post_data,
            })

            counter_parts = []
            for m, c in sorted(method_counts.items()):
                m_color = COLORS.get(m, COLORS["OTHER"])
                counter_parts.append(f"{m_color}{COLORS['BOLD']}{m}:{c}{COLORS['RESET']}")

            counter_str = " | ".join(counter_parts)
            print(f"\r{COLORS['GRAY']}↳{COLORS['RESET']} {COLORS['DIM']}[Request FOUND]{COLORS['RESET']} {counter_str}",
                  end="", flush=True)

        page.on("request", log_request)

        print(
            f"{COLORS['CYAN']}►{COLORS['RESET']} {COLORS['DIM']}Navigating to target:{COLORS['RESET']} {COLORS['YELLOW']}{target_url}{COLORS['RESET']}")
        try:
            page.goto(target_url, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass

        print(
            f"\n{COLORS['CYAN']}►{COLORS['RESET']} {COLORS['DIM']}Simulating user interactions (Inputs & Buttons){COLORS['RESET']}")

        try:
            forms = page.locator("form")
            for f in range(forms.count()):
                try:
                    form = forms.nth(f)
                    if not form.is_visible():
                        continue

                    inputs = form.locator(
                        "input:not([type='hidden']):not([type='submit']):not([type='button']):not([type='reset'])")
                    for i in range(inputs.count()):
                        try:
                            inp = inputs.nth(i)
                            if inp.is_visible():
                                inp_type = inp.get_attribute("type") or "text"
                                if inp_type == "email":
                                    inp.fill("test@example.com", timeout=200)
                                elif inp_type == "password":
                                    inp.fill("testpass123", timeout=200)
                                else:
                                    inp.fill("test_payload", timeout=200)
                        except:
                            pass

                    submit_btn = form.locator("button[type='submit'], input[type='submit'], button:not([type])")
                    if submit_btn.count() > 0 and submit_btn.first.is_visible():
                        print(f"{COLORS['GRAY']}   ↳ Submitting form {f + 1}...{COLORS['RESET']}")
                        with page.expect_navigation(timeout=5000):
                            submit_btn.first.click()
                        time.sleep(0.5)
                except:
                    pass
        except:
            pass

        try:
            buttons = page.locator("button, input[type='submit'], a.btn")
            for i in range(min(buttons.count(), 20)):
                try:
                    btn = buttons.nth(i)
                    if btn.is_visible():
                        with page.expect_navigation(timeout=3000, wait_until="networkidle"):
                            btn.click()
                        time.sleep(0.3)
                except:
                    pass
        except:
            pass

        time.sleep(1.5)
        browser.close()

    print(f"\n\n{COLORS['GREEN']}╔══════════════════════════════════════════════════════════════╗{COLORS['RESET']}")
    print(
        f"{COLORS['GREEN']}║{COLORS['RESET']} {COLORS['GREEN']}✓{COLORS['RESET']} Scan Completed Successfully! Total Requests: {COLORS['YELLOW']}{len(captured_requests)}{COLORS['RESET']:<10} {COLORS['GREEN']}║{COLORS['RESET']}")
    print(f"{COLORS['GREEN']}╚══════════════════════════════════════════════════════════════╝{COLORS['RESET']}")

    while True:
        print_main_menu()
        choice = input(f"\n{COLORS['CYAN']}└──> {COLORS['BOLD']}Enter your choice :{COLORS['RESET']} ").strip()

        if choice == "1":
            target_methods = set(method_counts.keys())
            display_filtered(captured_requests, target_methods, "ALL")

        elif choice == "2":
            target_methods = {"GET"}
            display_filtered(captured_requests, target_methods, "GET")

        elif choice == "3":
            target_methods = {"POST"}
            display_filtered(captured_requests, target_methods, "POST")

        elif choice == "4":
            target_methods = set(method_counts.keys()) - {"GET", "POST"}
            display_filtered(captured_requests, target_methods, "OTHER")

        elif choice == "5":
            if not captured_requests:
                print(f"\n{COLORS['YELLOW']}⚠{COLORS['RESET']} No requests captured yet. Please scan a URL first.")
                time.sleep(1)
                continue

            repeater = Repeater(captured_requests)
            repeater.view_all_requests_with_selection()

        elif choice == "6":
            print(
                f"\n{COLORS['CYAN']}►{COLORS['RESET']} {COLORS['DIM']}Exiting tool. Have a great hunts!{COLORS['RESET']}")
            break

        else:
            print(f"\n{COLORS['RED']}✖{COLORS['RESET']} Invalid choice. Please select between 1 and 6.")
            time.sleep(1)
            continue


def display_filtered(captured_requests, target_methods, filter_name):
    filtered = [req for req in captured_requests if req["method"] in target_methods]

    if not filtered:
        print(
            f"\n{COLORS['YELLOW']}⚠{COLORS['RESET']} {COLORS['DIM']}No requests found matching this filter.{COLORS['RESET']}")
        time.sleep(1)
        return

    print(f"\n{COLORS['CYAN']}╔══════════════════════════════════════════════════════════════╗{COLORS['RESET']}")
    print(
        f"{COLORS['CYAN']}║{COLORS['RESET']} {COLORS['BOLD']}Displaying {COLORS['YELLOW']}{len(filtered)}{COLORS['RESET']}{COLORS['BOLD']} {filter_name} Requests{COLORS['RESET']}                          {COLORS['CYAN']}║{COLORS['RESET']}")
    print(f"{COLORS['CYAN']}╚══════════════════════════════════════════════════════════════╝{COLORS['RESET']}")

    for idx, req in enumerate(filtered, 1):
        m_color = COLORS.get(req["method"], COLORS["OTHER"])
        print(
            f"\n{COLORS['GRAY']}┌─ {COLORS['BOLD']}#{idx}{COLORS['RESET']} {m_color}{COLORS['BOLD']}[{req['method']}]{COLORS['RESET']} {COLORS['DIM']}→{COLORS['RESET']} {req['url']}")
        print(f"{COLORS['GRAY']}│{COLORS['RESET']}")
        print(f"{COLORS['GRAY']}│{COLORS['RESET']} {COLORS['BOLD']}Headers:{COLORS['RESET']}")
        for h, v in req["headers"].items():
            print(
                f"{COLORS['GRAY']}│{COLORS['RESET']}   {COLORS['GRAY']}•{COLORS['RESET']} {COLORS['DIM']}{h}:{COLORS['RESET']} {v}")

        if req["post_data"]:
            print(f"{COLORS['GRAY']}│{COLORS['RESET']}")
            print(f"{COLORS['GRAY']}│{COLORS['RESET']} {COLORS['BOLD']}Body / Payload:{COLORS['RESET']}")
            print(f"{COLORS['GRAY']}│{COLORS['RESET']}   {COLORS['YELLOW']}{req['post_data']}{COLORS['RESET']}")
        print(f"{COLORS['GRAY']}└──────────────────────────────────────────────────────────{COLORS['RESET']}")

    time.sleep(2)


if __name__ == "__main__":
    print_banner()
    url = input(f"{COLORS['CYAN']}└──> {COLORS['BOLD']}Enter target URL :{COLORS['RESET']} ").strip()
    if not url.startswith("http"):
        url = "https://" + url
    inspect_page_requests(url)
