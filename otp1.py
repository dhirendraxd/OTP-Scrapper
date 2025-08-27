import imaplib
import email
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)

try:
    from webdriver_manager.chrome import ChromeDriverManager

    USE_WEBDRIVER_MANAGER = True
except ImportError:
    USE_WEBDRIVER_MANAGER = False

# Email Configuration - UPDATE THESE WITH YOUR ACTUAL CREDENTIALS
EMAIL_USER = "vibeckh.babu@gmail.com"  # Your actual Gmail
EMAIL_PASS = "mael yhsy jugh gtxa"     # Your App Password
IMAP_SERVER = "imap.gmail.com"

# Timing Configuration
EMAIL_CHECK_INTERVAL = 3  # seconds between email checks
MAX_WAIT_TIME = 120  # max seconds to wait for OTP email


class SmartOTPAutomator:
    def __init__(self):
        self.driver = None
        self.mail = None
        self.EMAIL_USER = EMAIL_USER
        self.EMAIL_PASS = EMAIL_PASS

    def connect_to_existing_browser(self):
        """Connect to an existing Chrome browser with remote debugging"""
        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

            if USE_WEBDRIVER_MANAGER:
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=chrome_options,
                )
            else:
                self.driver = webdriver.Chrome(options=chrome_options)

            print("✓ Connected to existing browser")
            return True
        except WebDriverException as e:
            print("✗ Could not connect to existing browser.")
            print(
                "💡 To use existing browser, start Chrome with: chrome --remote-debugging-port=9222"
            )
            print("💡 Or we can open a new browser window instead.")
            return False

    def setup_new_browser(self):
        """Create new browser instance with anti-detection settings"""
        try:
            chrome_options = Options()

            # Essential stability options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-gpu-sandbox")
            chrome_options.add_argument("--disable-software-rasterizer")
            
            # Anti-Cloudflare detection measures
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            
            # Fix GPU/WebGL errors while maintaining compatibility
            chrome_options.add_argument("--use-gl=swiftshader")
            chrome_options.add_argument("--enable-unsafe-swiftshader")
            chrome_options.add_argument("--disable-vulkan")
            
            # User agent and window size to appear more human
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Experimental options for better stealth
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Disable automation indicators
            prefs = {
                "profile.default_content_setting_values": {"notifications": 2},
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)

            print("🚀 Starting stealth browser to bypass Cloudflare...")

            if USE_WEBDRIVER_MANAGER:
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=chrome_options,
                )
            else:
                self.driver = webdriver.Chrome(options=chrome_options)

            # Execute stealth scripts to hide automation
            stealth_scripts = [
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
                "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})",
                "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})",
                "Object.defineProperty(screen, 'colorDepth', {get: () => 24})",
                "Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8})",
                "window.chrome = { runtime: {} };",
                "Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})})"
            ]
            
            for script in stealth_scripts:
                try:
                    self.driver.execute_script(script)
                except:
                    pass
                    
            print("✓ Browser ready with anti-detection!")
            return True
        except Exception as e:
            print(f"✗ Failed to setup browser: {e}")
            return False

    def handle_cloudflare(self):
        """Handle Cloudflare protection page"""
        try:
            # Wait a bit for the page to load
            time.sleep(3)
            
            # Check if we're on a Cloudflare page
            if "cloudflare" in self.driver.page_source.lower() or "checking your browser" in self.driver.page_source.lower():
                print("🛡️ Cloudflare detected! Waiting for automatic bypass...")
                
                # Wait for Cloudflare to finish checking (usually 5-10 seconds)
                max_wait = 30
                start_time = time.time()
                
                while (time.time() - start_time) < max_wait:
                    time.sleep(2)
                    
                    # Check if we've been redirected past Cloudflare
                    if "cloudflare" not in self.driver.page_source.lower() and "checking your browser" not in self.driver.page_source.lower():
                        print("✓ Cloudflare bypass successful!")
                        return True
                        
                    # Look for and click the "I'm human" checkbox if present
                    try:
                        # Common Cloudflare checkbox selectors
                        checkbox_selectors = [
                            "input[type='checkbox']",
                            ".cf-turnstile",
                            "#cf-turnstile",
                            ".challenge-form input",
                            "iframe[src*='cloudflare']"
                        ]
                        
                        for selector in checkbox_selectors:
                            try:
                                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if element.is_displayed():
                                    print("🤖 Attempting to interact with Cloudflare challenge...")
                                    self.driver.execute_script("arguments[0].click();", element)
                                    time.sleep(2)
                                    break
                            except:
                                continue
                                
                    except:
                        pass
                        
                    print("⏳ Still waiting for Cloudflare...")
                
                print("⚠️ Cloudflare taking longer than expected...")
                return False
            
            return True
            
        except Exception as e:
            print(f"✗ Error handling Cloudflare: {e}")
            return True  # Continue anyway

    def connect_to_email(self):
        """Connect to email server"""
        try:
            self.mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            self.mail.login(self.EMAIL_USER, self.EMAIL_PASS)
            self.mail.select("inbox")
            print("✓ Connected to email")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to email: {e}")
            return False

    def find_otp_elements(self):
        """Intelligently find OTP-related elements on the page"""
        print("🔍 Scanning page for OTP elements...")

        # Common patterns for Send OTP buttons
        send_button_selectors = [
            # By text content
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send')]",
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'otp')]",
            "//input[@type='submit'][contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send')]",
            "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send')]",
            # By common IDs/classes
            "//*[contains(@id, 'send')]",
            "//*[contains(@class, 'send')]",
            "//*[contains(@id, 'otp')]",
            "//*[contains(@class, 'otp')]",
        ]

        # Common patterns for OTP input fields
        otp_input_selectors = [
            "//input[@type='text'][contains(@placeholder, 'OTP')]",
            "//input[@type='text'][contains(@placeholder, 'code')]",
            "//input[@type='number'][contains(@placeholder, 'OTP')]",
            "//input[contains(@id, 'otp')]",
            "//input[contains(@class, 'otp')]",
            "//input[contains(@name, 'otp')]",
            "//input[contains(@name, 'code')]",
            "//input[@maxlength='6']",
            "//input[@maxlength='4']",
        ]

        # Common patterns for Verify buttons
        verify_button_selectors = [
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'verify')]",
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]",
            "//input[@type='submit'][contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'verify')]",
            "//*[contains(@id, 'verify')]",
            "//*[contains(@class, 'verify')]",
            "//*[contains(@id, 'submit')]",
            "//*[contains(@class, 'submit')]",
        ]

        found_elements = {}

        # Find Send OTP button
        for selector in send_button_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    found_elements["send_button"] = element
                    print(f"✓ Found Send button: {selector}")
                    break
            except NoSuchElementException:
                continue

        # Find OTP input field
        for selector in otp_input_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    found_elements["otp_input"] = element
                    print(f"✓ Found OTP input: {selector}")
                    break
            except NoSuchElementException:
                continue

        # Find Verify button
        for selector in verify_button_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    found_elements["verify_button"] = element
                    print(f"✓ Found Verify button: {selector}")
                    break
            except NoSuchElementException:
                continue

        return found_elements

    def get_latest_otp(self, sender_filter=None):
        """Extract OTP from the most recent unread email"""
        try:
            search_criteria = "UNSEEN"
            if sender_filter:
                search_criteria = f'(UNSEEN FROM "{sender_filter}")'

            result, data = self.mail.search(None, search_criteria)
            mail_ids = data[0].split()

            if not mail_ids:
                return None

            latest_email_id = mail_ids[-1]
            result, msg_data = self.mail.fetch(latest_email_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode("utf-8", errors="ignore")
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="ignore")

            # Look for OTP patterns
            otp_patterns = [
                r"\b\d{6}\b",  # 6-digit OTP
                r"\b\d{4}\b",  # 4-digit OTP
                r"\b\d{5}\b",  # 5-digit OTP
                r"\b\d{8}\b",  # 8-digit OTP
            ]

            for pattern in otp_patterns:
                otp_match = re.search(pattern, body)
                if otp_match:
                    otp = otp_match.group(0)
                    print(f"✓ Found OTP: {otp}")
                    return otp

            return None

        except Exception as e:
            print(f"✗ Error reading email: {e}")
            return None

    def run_automation(self, sender_filter=None, url_to_navigate=None):
        """Main automation flow"""
        print("🚀 Starting Smart OTP Automation...")

        # Automatically open new browser
        print("📱 Opening new browser automatically...")
        if not self.setup_new_browser():
            return False

        # Navigate to URL if provided
        if url_to_navigate:
            print(f"🌐 Navigating to: {url_to_navigate}")
            self.driver.get(url_to_navigate)
            
            # Handle Cloudflare if present
            if not self.handle_cloudflare():
                print("⚠️ Cloudflare protection may still be active. You might need to complete it manually.")
                input("Press Enter after completing Cloudflare challenge...")

        # Connect to email
        if not self.connect_to_email():
            return False

        try:
            print(f"📄 Current page: {self.driver.current_url}")

            # Find elements on the page
            elements = self.find_otp_elements()

            if not elements:
                print("❌ No OTP elements found on this page!")
                print("💡 Make sure you're on the right page with OTP functionality")
                return False

            # Click Send OTP if button found
            if "send_button" in elements:
                print("📧 Clicking 'Send OTP' button...")
                elements["send_button"].click()
                time.sleep(2)  # Wait for any UI updates
            else:
                print("⚠️ No Send OTP button found. Assuming OTP was already sent.")

            # Wait for OTP input to be available
            if "otp_input" not in elements:
                print("🔄 Waiting for OTP input field to appear...")
                time.sleep(3)
                elements = self.find_otp_elements()

            if "otp_input" not in elements:
                print("❌ No OTP input field found!")
                return False

            # Wait for OTP email
            print(f"⏳ Waiting for OTP email (max {MAX_WAIT_TIME}s)...")
            otp = None
            start_time = time.time()

            while otp is None and (time.time() - start_time) < MAX_WAIT_TIME:
                time.sleep(EMAIL_CHECK_INTERVAL)
                otp = self.get_latest_otp(sender_filter)

                if otp is None:
                    print("⏳ Still waiting for OTP...")

            if otp is None:
                print("✗ No OTP received within timeout period")
                return False

            # Enter OTP
            print(f"✍️ Entering OTP: {otp}")
            otp_input = elements["otp_input"]
            otp_input.clear()
            otp_input.send_keys(otp)

            # Click verify button if available
            if "verify_button" in elements:
                print("✅ Clicking verify button...")
                time.sleep(1)  # Small delay for visual feedback
                elements["verify_button"].click()
                print("🎉 OTP submitted successfully!")
            else:
                print("⚠️ No verify button found. OTP entered, please verify manually.")

            return True

        except Exception as e:
            print(f"✗ Automation failed: {e}")
            return False
        finally:
            # Ask before cleanup
            choice = input("\n🔧 Keep browser open? (y/n): ").lower().strip()
            if choice != "y":
                self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
            except:
                pass

        if self.driver:
            try:
                self.driver.quit()
            except:
                pass


def main():
    print("Smart OTP Automation Tool - Korean Embassy Nepal")
    print("=" * 50)
    
    # Automatically open new browser - no user choice needed
    print("📱 Automatically opening new browser...")
    
    # Use pre-configured email credentials (no manual input needed)
    print(f"📧 Using email: {EMAIL_USER}")
    print("🔑 Using saved App Password")
    
    # Pre-configured URL for Korean Embassy Nepal
    url = "https://koreanembassynepal.org/login"
    print(f"🌐 Target URL: {url}")
    
    # Optional: Ask for sender filter only if needed
    sender_filter = None  # Set to None for automatic detection, or specify like "noreply@koreanembassynepal.org"

    # Create automator with pre-configured email settings
    automator = SmartOTPAutomator()
    automator.EMAIL_USER = EMAIL_USER
    automator.EMAIL_PASS = EMAIL_PASS

    success = automator.run_automation(sender_filter, url)

    if success:
        print("✅ Automation completed!")
    else:
        print("❌ Automation failed. Check the logs above.")


if __name__ == "__main__":
    main()

    #  bypassing cloudflare  captcha
    automator.bypass_cloudflare_captcha() 
    