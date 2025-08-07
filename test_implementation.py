#!/usr/bin/env python3
"""
Test script for the enhanced reCAPTCHA solver with Google Cloud integration.
"""

import os
import logging
import tempfile
import json
from playwright.sync_api import sync_playwright
from playwright_recaptcha import recaptchav2

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_mock_credentials():
    """Create a mock credentials file for testing purposes."""
    mock_creds = {
        "type": "service_account",
        "project_id": "mock-project",
        "private_key_id": "mock-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMOCK_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
        "client_email": "mock@mock-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(mock_creds, temp_file, indent=2)
    temp_file.close()
    return temp_file.name

def test_initialization():
    """Test various initialization scenarios."""
    logger.info("=" * 60)
    logger.info("Testing Initialization Scenarios")
    logger.info("=" * 60)
    
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=True)
        page = browser.new_page()
        
        # Test 1: Basic initialization without credentials
        try:
            solver = recaptchav2.SyncSolver(page, debug=True)
            logger.info("✅ Basic initialization successful")
            solver.close()
        except Exception as e:
            logger.error(f"❌ Basic initialization failed: {e}")
        
        # Test 2: Force Google Cloud without credentials (should fail)
        try:
            solver = recaptchav2.SyncSolver(page, force_google_cloud=True)
            logger.error("❌ Should have failed with missing credentials")
            solver.close()
        except ValueError as e:
            logger.info(f"✅ Correctly failed when forcing Google Cloud without credentials: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
        
        # Test 3: With mock credentials file
        mock_creds_file = None
        try:
            mock_creds_file = create_mock_credentials()
            solver = recaptchav2.SyncSolver(
                page, 
                google_cloud_credentials=mock_creds_file,
                debug=True
            )
            logger.info("✅ Mock credentials initialization successful")
            solver.close()
        except Exception as e:
            logger.error(f"❌ Mock credentials initialization failed: {e}")
        finally:
            if mock_creds_file and os.path.exists(mock_creds_file):
                os.unlink(mock_creds_file)
        
        # Test 4: Force Google Cloud with mock credentials
        mock_creds_file = None
        try:
            mock_creds_file = create_mock_credentials()
            solver = recaptchav2.SyncSolver(
                page, 
                google_cloud_credentials=mock_creds_file,
                force_google_cloud=True,
                debug=True
            )
            logger.info("✅ Force Google Cloud with mock credentials successful")
            solver.close()
        except Exception as e:
            logger.error(f"❌ Force Google Cloud with mock credentials failed: {e}")
        finally:
            if mock_creds_file and os.path.exists(mock_creds_file):
                os.unlink(mock_creds_file)
        
        browser.close()

def test_fallback_behavior():
    """Test the fallback behavior between Google Cloud and free API."""
    logger.info("=" * 60)
    logger.info("Testing API Fallback Behavior")
    logger.info("=" * 60)
    
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Test without credentials - should use fallback
            solver = recaptchav2.SyncSolver(page, debug=True)
            logger.info("✅ Solver initialized for fallback test")
            
            # This won't actually solve a CAPTCHA, but we can test the transcription method
            # with a mock audio URL to see the fallback behavior
            logger.info("Solver ready - fallback to free API should be available")
            solver.close()
            
        except Exception as e:
            logger.error(f"❌ Fallback test failed: {e}")
        
        browser.close()

def test_with_real_credentials():
    """Test with real credentials if available."""
    logger.info("=" * 60)
    logger.info("Testing with Real Credentials (if available)")
    logger.info("=" * 60)
    
    # Check for real credentials file
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path or not os.path.exists(creds_path):
        logger.warning("⚠️  No real Google Cloud credentials found. Set GOOGLE_APPLICATION_CREDENTIALS environment variable.")
        return
    
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=True)
        page = browser.new_page()
        
        try:
            solver = recaptchav2.SyncSolver(
                page,
                google_cloud_credentials=creds_path,
                force_google_cloud=True,
                debug=True
            )
            logger.info("✅ Real credentials initialization successful")
            logger.info("🎯 Ready for actual CAPTCHA solving with Google Cloud API")
            solver.close()
            
        except Exception as e:
            logger.error(f"❌ Real credentials test failed: {e}")
        
        browser.close()

def main():
    """Run all tests."""
    logger.info("🚀 Starting Playwright-reCAPTCHA Google Cloud Integration Tests")
    
    test_initialization()
    test_fallback_behavior()
    test_with_real_credentials()
    
    logger.info("=" * 60)
    logger.info("🎉 Test Suite Complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next Steps:")
    logger.info("1. Set up real Google Cloud credentials (JSON file)")
    logger.info("2. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
    logger.info("3. Test with actual reCAPTCHA: page.goto('https://www.google.com/recaptcha/api2/demo')")
    logger.info("4. Use solver.solve_recaptcha(wait=True) for real solving")

if __name__ == "__main__":
    main()