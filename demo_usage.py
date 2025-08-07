#!/usr/bin/env python3
"""
Demo script showing all the new Google Cloud reCAPTCHA solving features.
"""

import logging
from playwright.sync_api import sync_playwright
from playwright_recaptcha import recaptchav2

# Setup logging to see debug information
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def demo_basic_usage():
    """Demo basic usage without credentials (uses free API)."""
    print("🔷 DEMO 1: Basic usage (free API fallback)")
    
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=True)
        page = browser.new_page()
        
        # Basic solver - will use free Google API if no credentials
        solver = recaptchav2.SyncSolver(page, debug=True)
        print("✅ Solver initialized - will fall back to free API")
        solver.close()
        browser.close()

def demo_forced_google_cloud():
    """Demo forced Google Cloud usage (requires credentials)."""
    print("\n🔷 DEMO 2: Forced Google Cloud (requires credentials)")
    
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=True)
        page = browser.new_page()
        
        try:
            # This will fail because no credentials provided but Google Cloud is forced
            solver = recaptchav2.SyncSolver(
                page, 
                force_google_cloud=True,
                debug=True
            )
        except ValueError as e:
            print(f"✅ Correctly failed: {e}")
        
        browser.close()

def demo_with_credentials():
    """Demo with credentials file (production-ready)."""
    print("\n🔷 DEMO 3: With credentials file (production-ready)")
    
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=True)
        page = browser.new_page()
        
        try:
            # This would work with real credentials
            solver = recaptchav2.SyncSolver(
                page,
                google_cloud_credentials="/path/to/your/credentials.json",
                force_google_cloud=True,
                debug=True
            )
            print("✅ Would work with real credentials file")
        except FileNotFoundError:
            print("✅ Correctly validates credentials file exists")
        
        browser.close()

def demo_async_usage():
    """Demo async version."""
    print("\n🔷 DEMO 4: Async version")
    
    import asyncio
    from playwright.async_api import async_playwright
    
    async def async_demo():
        async with async_playwright() as playwright:
            browser = await playwright.firefox.launch(headless=True)
            page = await browser.new_page()
            
            # Async solver with debug
            solver = recaptchav2.AsyncSolver(page, debug=True)
            print("✅ Async solver initialized")
            solver.close()
            await browser.close()
    
    asyncio.run(async_demo())

def show_usage_examples():
    """Show code examples."""
    print("\n📚 USAGE EXAMPLES:")
    print("=" * 60)
    
    print("""
# 1. Basic usage (fallback to free API)
solver = recaptchav2.SyncSolver(page, debug=True)
token = solver.solve_recaptcha(wait=True)

# 2. Force Google Cloud (requires credentials)  
solver = recaptchav2.SyncSolver(
    page,
    google_cloud_credentials="path/to/credentials.json",
    force_google_cloud=True,
    debug=True
)
token = solver.solve_recaptcha(wait=True)
# Output: ✅ CAPTCHA solved with your own Google Cloud API keys

# 3. Environment variable
export GOOGLE_CLOUD_CREDENTIALS="path/to/credentials.json"
solver = recaptchav2.SyncSolver(page, force_google_cloud=True)

# 4. Async version
async with recaptchav2.AsyncSolver(
    page, 
    google_cloud_credentials="credentials.json",
    force_google_cloud=True
) as solver:
    token = await solver.solve_recaptcha(wait=True)
""")

def main():
    print("🚀 Playwright-reCAPTCHA Google Cloud Integration Demo")
    print("=" * 60)
    
    demo_basic_usage()
    demo_forced_google_cloud() 
    demo_with_credentials()
    demo_async_usage()
    show_usage_examples()
    
    print("\n🎉 Demo Complete!")
    print("\n📝 Key Features:")
    print("✅ Rock-solid Google Cloud Speech-to-Text API integration")
    print("✅ Automatic fallback to free API when credentials not provided")
    print("✅ Force Google Cloud option with error handling")
    print("✅ Comprehensive debug logging")
    print("✅ Environment variable support")
    print("✅ Both sync and async support")
    print("✅ Production-ready error handling")
    print("✅ Clear success/failure messages")

if __name__ == "__main__":
    main()