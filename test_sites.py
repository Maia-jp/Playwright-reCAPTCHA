#!/usr/bin/env python3
"""
Test reCAPTCHA solver on various test sites.
"""

import logging
from playwright.sync_api import sync_playwright
from playwright_recaptcha import recaptchav2

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_google_demo():
    """Test on official Google reCAPTCHA demo."""
    print("🎯 Testing: Google Official Demo")
    print("URL: https://www.google.com/recaptcha/api2/demo")
    print("-" * 60)
    
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        
        try:
            page.goto("https://www.google.com/recaptcha/api2/demo", timeout=30000)
            page.wait_for_load_state("networkidle")
            
            with recaptchav2.SyncSolver(page, force_google_cloud=True, debug=True) as solver:
                token = solver.solve_recaptcha(wait=True, attempts=3)
                print(f"✅ SUCCESS! Token: {token[:50]}...")
                return True
                
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
        finally:
            page.wait_for_timeout(3000)
            browser.close()

def test_recaptcha_demo_io():
    """Test on recaptcha-demo.io - a dedicated test site."""
    print("\n🎯 Testing: reCAPTCHA Demo Site")
    print("URL: https://recaptcha-demo.io/")
    print("-" * 60)
    
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        
        try:
            page.goto("https://recaptcha-demo.io/", timeout=30000)
            page.wait_for_load_state("networkidle")
            
            with recaptchav2.SyncSolver(page, force_google_cloud=True, debug=True) as solver:
                token = solver.solve_recaptcha(wait=True, attempts=3)
                print(f"✅ SUCCESS! Token: {token[:50]}...")
                return True
                
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
        finally:
            page.wait_for_timeout(3000)
            browser.close()

def test_2captcha_demo():
    """Test on 2captcha demo site."""
    print("\n🎯 Testing: 2captcha Demo")
    print("URL: https://2captcha.com/demo/recaptcha-v2")
    print("-" * 60)
    
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        
        try:
            page.goto("https://2captcha.com/demo/recaptcha-v2", timeout=30000)
            page.wait_for_load_state("networkidle")
            
            with recaptchav2.SyncSolver(page, force_google_cloud=True, debug=True) as solver:
                token = solver.solve_recaptcha(wait=True, attempts=3)
                print(f"✅ SUCCESS! Token: {token[:50]}...")
                return True
                
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
        finally:
            page.wait_for_timeout(3000)
            browser.close()

def test_custom_site():
    """Create a custom test page."""
    print("\n🎯 Testing: Custom Test Page")
    print("Creating custom reCAPTCHA page...")
    print("-" * 60)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>reCAPTCHA Test</title>
        <script src="https://www.google.com/recaptcha/api.js" async defer></script>
        <style>
            body { font-family: Arial, sans-serif; padding: 50px; }
            .container { max-width: 500px; margin: 0 auto; text-align: center; }
            .g-recaptcha { display: inline-block; margin: 20px 0; }
            button { padding: 10px 20px; font-size: 16px; }
            .result { margin-top: 20px; padding: 10px; background: #f0f0f0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>reCAPTCHA Test Page</h1>
            <p>This is a test page for reCAPTCHA solving.</p>
            
            <form id="demo-form">
                <div class="g-recaptcha" data-sitekey="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"></div>
                <br>
                <button type="submit">Submit</button>
            </form>
            
            <div id="result" class="result" style="display:none;">
                <h3>Success!</h3>
                <p>reCAPTCHA was solved successfully.</p>
            </div>
        </div>
        
        <script>
            document.getElementById('demo-form').addEventListener('submit', function(e) {
                e.preventDefault();
                var response = grecaptcha.getResponse();
                if (response.length > 0) {
                    document.getElementById('result').style.display = 'block';
                    console.log('reCAPTCHA token:', response);
                } else {
                    alert('Please complete the reCAPTCHA');
                }
            });
        </script>
    </body>
    </html>
    """
    
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        
        try:
            # Load Google first to avoid domain issues
            page.goto("https://www.google.com/", wait_until="commit")
            page.set_content(html_content)
            page.wait_for_timeout(3000)  # Wait for reCAPTCHA to load
            
            with recaptchav2.SyncSolver(page, force_google_cloud=True, debug=True) as solver:
                token = solver.solve_recaptcha(wait=True, attempts=3)
                print(f"✅ SUCCESS! Token: {token[:50]}...")
                
                # Click submit button to see result
                page.click("button[type='submit']")
                page.wait_for_timeout(2000)
                
                return True
                
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
        finally:
            page.wait_for_timeout(5000)  # Keep open longer to see result
            browser.close()

def test_interactive_mode():
    """Interactive testing mode - choose which site to test."""
    print("\n🎮 Interactive Testing Mode")
    print("=" * 60)
    
    sites = [
        ("Google Official Demo", "https://www.google.com/recaptcha/api2/demo"),
        ("reCAPTCHA Demo IO", "https://recaptcha-demo.io/"),
        ("2captcha Demo", "https://2captcha.com/demo/recaptcha-v2"),
        ("Custom Test Page", "custom")
    ]
    
    print("Available test sites:")
    for i, (name, url) in enumerate(sites, 1):
        print(f"{i}. {name}")
        if url != "custom":
            print(f"   URL: {url}")
        print()
    
    try:
        choice = int(input("Choose a site to test (1-4): "))
        if choice < 1 or choice > 4:
            print("Invalid choice")
            return
    except ValueError:
        print("Invalid input")
        return
    
    name, url = sites[choice - 1]
    print(f"\n🚀 Testing {name}...")
    
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        
        try:
            if url == "custom":
                # Custom page logic
                page.goto("https://www.google.com/", wait_until="commit")
                html_content = """<!DOCTYPE html><html><head><title>Test</title><script src="https://www.google.com/recaptcha/api.js" async defer></script></head><body><h1>Test reCAPTCHA</h1><div class="g-recaptcha" data-sitekey="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"></div></body></html>"""
                page.set_content(html_content)
                page.wait_for_timeout(3000)
            else:
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle")
            
            print("🔧 Initializing solver...")
            with recaptchav2.SyncSolver(page, force_google_cloud=True, debug=True) as solver:
                print("🤖 Starting reCAPTCHA solving...")
                token = solver.solve_recaptcha(wait=True, attempts=5)
                print(f"🎉 SUCCESS! Token: {token[:50]}...")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        finally:
            input("\nPress Enter to close browser...")
            browser.close()

def main():
    print("🧪 reCAPTCHA Solver Test Sites")
    print("=" * 60)
    print("These sites are perfect for testing reCAPTCHA solvers:")
    print()
    
    print("RECOMMENDED TEST SITES:")
    print("1. https://www.google.com/recaptcha/api2/demo")
    print("   - Official Google demo")
    print("   - Most reliable for testing")
    print()
    print("2. https://recaptcha-demo.io/")
    print("   - Dedicated reCAPTCHA testing site")
    print("   - Clean, simple interface")
    print()
    print("3. https://2captcha.com/demo/recaptcha-v2") 
    print("   - Popular captcha service demo")
    print("   - Good for testing different scenarios")
    print()
    
    choice = input("Choose test mode:\n1. Run all tests automatically\n2. Interactive mode (choose site)\n3. Quick Google demo test\nChoice (1-3): ")
    
    if choice == "1":
        print("\n🚀 Running all tests...")
        results = []
        results.append(("Google Demo", test_google_demo()))
        results.append(("reCAPTCHA Demo IO", test_recaptcha_demo_io()))
        results.append(("Custom Page", test_custom_site()))
        
        print("\n" + "="*60)
        print("FINAL RESULTS")
        print("="*60)
        for name, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{name}: {status}")
            
    elif choice == "2":
        test_interactive_mode()
        
    elif choice == "3":
        test_google_demo()
        
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()