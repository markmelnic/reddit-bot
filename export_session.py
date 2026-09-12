"""Helper script to log into Reddit manually on a local machine, solve captcha, and save session cookies."""

import json
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def main():
    username = input("Enter your Reddit username (e.g. AppropriateChance699): ").strip()
    if not username:
        print("Username is required.")
        return

    session_dir = Path("sessions")
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / f"{username}.cookies"

    print(f"\n[INFO] Launching non-headless Chrome browser...")
    print(f"[INFO] Please log into Reddit manually and solve any captchas if prompted.")
    print(f"[INFO] You have 90 seconds before cookies are automatically saved.\n")

    options = webdriver.ChromeOptions()
    options.add_argument("--lang=en")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.reddit.com/login/")
        
        # Wait for user to login manually
        print(f"Waiting 90 seconds for manual login...")
        for i in range(90, 0, -1):
            print(f"Time remaining: {i}s...", end="\r")
            time.sleep(1)
        print("\nSaving cookies...")

        cookies = driver.get_cookies()
        with open(session_file, "w") as f:
            json.dump(cookies, f, indent=2)

        print(f"\n[SUCCESS] Saved {len(cookies)} cookies to {session_file}")
        print(f"[INFO] You can now commit this file or upload it to Render so the bot uses it automatically!")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
