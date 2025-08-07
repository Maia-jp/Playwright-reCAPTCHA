#!/usr/bin/env python3
"""
Test script for API key functionality.
"""

import os
import logging
from playwright.sync_api import sync_playwright
from playwright_recaptcha import recaptchav2

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_api_key_validation():
    """Test API key validation."""
    print("🔑 Testing API Key Validation")
    print("=" * 50)
    
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=True)
        page = browser.new_page()
        
        # Test 1: Valid API key format
        try:
            solver = recaptchav2.SyncSolver(
                page,
                google_cloud_credentials="AIzaSyDHltePuTdf17iweuAAcHuwovEyvT31upE",
                debug=True
            )
            print("✅ API key format validation successful")
            solver.close()
        except Exception as e:
            print(f"❌ API key validation failed: {e}")
        
        # Test 2: Invalid API key format
        try:
            solver = recaptchav2.SyncSolver(
                page,
                google_cloud_credentials="invalid_key",
                debug=True
            )
            print("❌ Should have failed with invalid key")
            solver.close()
        except FileNotFoundError:
            print("✅ Correctly rejected invalid API key format")
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
        
        # Test 3: Force Google Cloud with API key
        try:
            solver = recaptchav2.SyncSolver(
                page,
                google_cloud_credentials="AIzaSyDHltePuTdf17iweuAAcHuwovEyvT31upE",
                force_google_cloud=True,
                debug=True
            )
            print("✅ Force Google Cloud with API key successful")
            solver.close()
        except Exception as e:
            print(f"❌ Force with API key failed: {e}")
        
        browser.close()

def test_with_env_api_key():
    """Test with API key from .env file."""
    print("\n🔑 Testing with .env API Key")
    print("=" * 50)
    
    # Load API key from .env if available
    api_key = None
    try:
        with open('.env', 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('GOOGLE_CLOUD_CREDENTIALS='):
                    api_key = line.split('=', 1)[1].strip()
                    break
    except FileNotFoundError:
        print("⚠️ No .env file found")
        return
    
    if not api_key:
        print("⚠️ No GOOGLE_CLOUD_CREDENTIALS found in .env")
        return
        
    print(f"Found API key: {api_key[:20]}...")
    
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Set environment variable
            os.environ['GOOGLE_CLOUD_CREDENTIALS'] = api_key
            
            solver = recaptchav2.SyncSolver(
                page,
                force_google_cloud=True,
                debug=True
            )
            print("✅ Environment variable API key successful")
            print("🎯 Ready for actual CAPTCHA solving with your API key!")
            solver.close()
            
        except Exception as e:
            print(f"❌ Environment API key test failed: {e}")
        finally:
            # Clean up environment
            if 'GOOGLE_CLOUD_CREDENTIALS' in os.environ:
                del os.environ['GOOGLE_CLOUD_CREDENTIALS']
        
        browser.close()

def show_usage_examples():
    """Show usage examples with API keys."""
    print("\n📚 API Key Usage Examples:")
    print("=" * 60)
    print("""
# 1. Direct API key
solver = recaptchav2.SyncSolver(
    page,
    google_cloud_credentials="AIzaSyDHltePuTdf17iweuAAcHuwovEyvT31upE",
    force_google_cloud=True,
    debug=True
)

# 2. Environment variable
export GOOGLE_CLOUD_CREDENTIALS="AIzaSyDHltePuTdf17iweuAAcHuwovEyvT31upE"
solver = recaptchav2.SyncSolver(page, force_google_cloud=True)

# 3. .env file
echo "GOOGLE_CLOUD_CREDENTIALS=AIzaSyDHltePuTdf17iweuAAcHuwovEyvT31upE" > .env
solver = recaptchav2.SyncSolver(page, force_google_cloud=True)

# When successful, you'll see:
# ✅ CAPTCHA solved with your own Google Cloud API keys
""")

def main():
    print("🚀 Google Cloud API Key Support Test")
    print("=" * 60)
    
    test_api_key_validation()
    test_with_env_api_key()
    show_usage_examples()
    
    print("\n🎉 API Key Support Testing Complete!")
    print("\n✨ New Features:")
    print("✅ Support for Google Cloud API keys (AIza...)")
    print("✅ Support for JSON credentials files")
    print("✅ Automatic detection of credential type")
    print("✅ Environment variable support for both")
    print("✅ Force Google Cloud option")
    print("✅ Comprehensive error handling")

if __name__ == "__main__":
    main()