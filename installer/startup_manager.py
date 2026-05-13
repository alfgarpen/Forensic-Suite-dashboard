import webbrowser
import time
import requests
import sys

def open_browser(url, timeout=30):
    print(f"[*] Waiting for dashboard to be ready at {url}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("[*] Dashboard is ready! Opening browser...")
                webbrowser.open(url)
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    
    print("[!] Timeout waiting for dashboard. Please open it manually.")
    return False

if __name__ == "__main__":
    target_url = "http://localhost:5001"
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    open_browser(target_url)
