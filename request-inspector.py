# REQUEST INSPECTOR v2.0
from collections import defaultdict
import threading
import time
from playwright.sync_api import sync_playwright

COLORS = {
    "GET": "\033[92m",
    "POST": "\033[94m",
    "PUT": "\033[93m",
    "DELETE": "\033[91m",
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

def print_banner():
    banner = f"""
{COLORS['CYAN']}{COLORS['BOLD']}
    ██╗ ███╗   ██╗ ███████╗ ██████╗  ███████╗  ██████╗ ████████╗  ██████╗  ██████╗ 
    ██║ ████╗  ██║ ██╔════╝ ██╔══██╗ ██╔════╝ ██╔════╝ ╚══██╔══╝ ██╔═══██╗ ██╔══██╗
    ██║ ██╔██╗ ██║ ███████╗ ██████╔╝ █████╗   ██║         ██║    ██║   ██║ ██████╔╝
    ██║ ██║╚██╗██║ ╚════██║ ██╔═══╝  ██╔══╝   ██║         ██║    ██║   ██║ ██╔══██╗
    ██║ ██║ ╚████║ ███████║ ██║      ███████╗ ╚██████╗    ██║    ╚██████╔╝ ██║  ██║
    ╚═╝ ╚═╝  ╚═══╝ ╚══════╝ ╚═╝      ╚══════╝  ╚═════╝    ╚═╝     ╚═════╝  ╚═╝  ╚═╝
                                      {COLORS['YELLOW']}[ v2.0 ]{COLORS['CYAN']}
╚═════════════════════════════════════════════════════════════════════════════════════╝{COLORS['RESET']}
"""
    print(banner)

def print_menu():
    menu = f"""
{COLORS['CYAN']}{COLORS['BOLD']}┌──[ {COLORS['YELLOW']}SELECT VIEW MODE{COLORS['CYAN']} ]──────────────────────────────────────┐{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['CYAN']}❖{COLORS['RESET']} {COLORS['CYAN']}{COLORS['BOLD']}[1]{COLORS['RESET']} {COLORS['CYAN']}View GET Requests{COLORS['RESET']}                                    {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['CYAN']}❖{COLORS['RESET']} {COLORS['CYAN']}{COLORS['BOLD']}[2]{COLORS['RESET']} {COLORS['CYAN']}View POST Requests{COLORS['RESET']}                                   {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['CYAN']}❖{COLORS['RESET']} {COLORS['CYAN']}{COLORS['BOLD']}[3]{COLORS['RESET']} {COLORS['CYAN']}View Other Methods (PUT, DELETE, etc.){COLORS['RESET']}               {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['CYAN']}❖{COLORS['RESET']} {COLORS['CYAN']}{COLORS['BOLD']}[4]{COLORS['RESET']} {COLORS['CYAN']}View ALL Requests{COLORS['RESET']}                                    {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}│{COLORS['RESET']} {COLORS['RED']}✖{COLORS['RESET']} {COLORS['RED']}{COLORS['BOLD']}[5]{COLORS['RESET']} {COLORS['RED']}Exit Tool{COLORS['RESET']}                                            {COLORS['CYAN']}│{COLORS['RESET']}
{COLORS['CYAN']}└────────────────────────────────────────────────────────────┘{COLORS['RESET']}
"""
    print(menu)


def inspect_page_requests(target_url):
    captured_requests = []
    method_counts = defaultdict(int)
    counts_lock = threading.Lock()

    with sync_playwright() as p:
        print(
            f"{COLORS['CYAN']}►{COLORS['RESET']} {COLORS['DIM']}Initializing headless browser engine...{COLORS['RESET']}"
        )
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
                counter_parts.append(
                    f"{m_color}{COLORS['BOLD']}{m}:{c}{COLORS['RESET']}"
                )

            counter_str = " | ".join(counter_parts)
            print(
                f"\r{COLORS['GRAY']}↳{COLORS['RESET']} {COLORS['DIM']}[Request FOUND]{COLORS['RESET']} {counter_str}",
                end="",
                flush=True,
            )

        page.on("request", log_request)

        print(
            f"{COLORS['CYAN']}►{COLORS['RESET']} {COLORS['DIM']}Navigating to target:{COLORS['RESET']} {COLORS['YELLOW']}{target_url}{COLORS['RESET']}"
        )
        try:
            page.goto(target_url, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass

        print(
            f"\n{COLORS['CYAN']}►{COLORS['RESET']} {COLORS['DIM']}Simulating user interactions (Inputs & Buttons){COLORS['RESET']}"
        )

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

    print(
        f"\n\n{COLORS['GREEN']}╔══════════════════════════════════════════════════════════════╗{COLORS['RESET']}"
    )
    print(
        f"{COLORS['GREEN']}║{COLORS['RESET']} {COLORS['GREEN']}✓{COLORS['RESET']} Scan Completed Successfully! Total"
        f" Requests: {COLORS['YELLOW']}{len(captured_requests)}{COLORS['RESET']:<12} {COLORS['GREEN']}   ║{COLORS['RESET']}"
    )
    print(
        f"{COLORS['GREEN']}╚══════════════════════════════════════════════════════════════╝{COLORS['RESET']}"
    )

    while True:
        print_menu()
        choice = input(
            f"\n{COLORS['CYAN']}└──> {COLORS['BOLD']}Enter your choice :{COLORS['RESET']} "
        ).strip()

        if choice == "1":
            target_methods = {"GET"}
        elif choice == "2":
            target_methods = {"POST"}
        elif choice == "3":
            target_methods = set(method_counts.keys()) - {"GET", "POST"}
        elif choice == "4":
            target_methods = set(method_counts.keys())
        elif choice == "5":
            print(
                f"\n{COLORS['CYAN']}►{COLORS['RESET']} {COLORS['DIM']}Exiting tool. Have a great hunts!{COLORS['RESET']}")
            break
        else:
            print(
                f"\n{COLORS['RED']}✖{COLORS['RESET']} {COLORS['RED']}Invalid choice. Please select between 1 and 5.{COLORS['RESET']}"
            )
            time.sleep(1)
            continue

        filtered = [
            req for req in captured_requests if req["method"] in target_methods
        ]

        if not filtered:
            print(
                f"\n{COLORS['YELLOW']}⚠{COLORS['RESET']} {COLORS['DIM']}No requests found matching this filter.{COLORS['RESET']}"
            )
            time.sleep(1)
            continue

        print(
            f"\n{COLORS['CYAN']}╔══════════════════════════════════════════════════════════════╗{COLORS['RESET']}"
        )
        print(
            f"{COLORS['CYAN']}║{COLORS['RESET']} {COLORS['BOLD']}Displaying {COLORS['YELLOW']}{len(filtered)}{COLORS['RESET']}{COLORS['BOLD']} Requests{COLORS['RESET']}                              {COLORS['CYAN']}║{COLORS['RESET']}"
        )
        print(
            f"{COLORS['CYAN']}╚══════════════════════════════════════════════════════════════╝{COLORS['RESET']}"
        )

        for idx, req in enumerate(filtered, 1):
            m_color = COLORS.get(req["method"], COLORS["OTHER"])
            print(
                f"\n{COLORS['GRAY']}┌─ {COLORS['BOLD']}#{idx}{COLORS['RESET']} {m_color}{COLORS['BOLD']}[{req['method']}]{COLORS['RESET']} {COLORS['DIM']}→{COLORS['RESET']} {req['url']}"
            )
            print(
                f"{COLORS['GRAY']}│{COLORS['RESET']}"
            )
            print(f"{COLORS['GRAY']}│{COLORS['RESET']} {COLORS['BOLD']}Headers:{COLORS['RESET']}")
            for h, v in req["headers"].items():
                print(
                    f"{COLORS['GRAY']}│{COLORS['RESET']}   {COLORS['GRAY']}•{COLORS['RESET']} {COLORS['DIM']}{h}:{COLORS['RESET']} {v}")

            if req["post_data"]:
                print(f"{COLORS['GRAY']}│{COLORS['RESET']}")
                print(f"{COLORS['GRAY']}│{COLORS['RESET']} {COLORS['BOLD']}Body / Payload:{COLORS['RESET']}")
                print(f"{COLORS['GRAY']}│{COLORS['RESET']}   {COLORS['YELLOW']}{req['post_data']}{COLORS['RESET']}")
            print(
                f"{COLORS['GRAY']}└──────────────────────────────────────────────────────────{COLORS['RESET']}"
            )

        time.sleep(1.5)

if __name__ == "__main__":
    print_banner()
    url = input(
        f"{COLORS['CYAN']}└──> {COLORS['BOLD']}Enter target URL :{COLORS['RESET']} "
    ).strip()
    if not url.startswith("http"):
        url = "https://" + url
    inspect_page_requests(url)