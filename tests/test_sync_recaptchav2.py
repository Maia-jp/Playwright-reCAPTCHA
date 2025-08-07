import pytest
from playwright.sync_api import sync_playwright

from playwright_recaptcha import (
    CapSolverError,
    RecaptchaNotFoundError,
    RecaptchaRateLimitError,
    RecaptchaSolveError,
    recaptchav2,
)


@pytest.mark.xfail(raises=RecaptchaRateLimitError)
def test_solver_with_normal_recaptcha() -> None:
    """Test the solver with a normal reCAPTCHA."""
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch()
        page = browser.new_page()
        page.goto("https://www.google.com/recaptcha/api2/demo")

        with recaptchav2.SyncSolver(page) as solver:
            solver.solve_recaptcha(wait=True)


@pytest.mark.xfail(raises=(RecaptchaNotFoundError, RecaptchaRateLimitError))
def test_solver_with_hidden_recaptcha() -> None:
    """Test the solver with a hidden reCAPTCHA."""
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch()
        page = browser.new_page()

        page.goto("https://www.google.com/recaptcha/api2/demo?invisible=true")
        page.get_by_role("button").click()

        with recaptchav2.SyncSolver(page) as solver:
            solver.solve_recaptcha(wait=True)


@pytest.mark.xfail(raises=RecaptchaRateLimitError)
def test_solver_with_slow_browser() -> None:
    """Test the solver with a slow browser."""
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(slow_mo=1000)
        page = browser.new_page()
        page.goto("https://www.google.com/recaptcha/api2/demo")

        with recaptchav2.SyncSolver(page) as solver:
            solver.solve_recaptcha(wait=True)


@pytest.mark.xfail(raises=CapSolverError)
def test_solver_with_image_challenge() -> None:
    """Test the solver with an image challenge."""
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch()
        page = browser.new_page()
        page.goto("https://www.google.com/recaptcha/api2/demo")

        with recaptchav2.SyncSolver(page) as solver:
            solver.solve_recaptcha(wait=True, image_challenge=True)


def test_recaptcha_not_found_error() -> None:
    """Test the solver with a page that does not have a reCAPTCHA."""
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch()
        page = browser.new_page()
        page.goto("https://www.google.com/")

        with pytest.raises(RecaptchaNotFoundError), recaptchav2.SyncSolver(
            page
        ) as solver:
            solver.solve_recaptcha()


def test_google_cloud_credentials_required() -> None:
    """Test that Google Cloud credentials are required for audio transcription."""
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch()
        page = browser.new_page()
        page.goto("https://www.google.com/recaptcha/api2/demo")

        # Test without credentials should raise ValueError when forced
        with pytest.raises(ValueError, match="Google Cloud credentials are required when force_google_cloud=True"):
            recaptchav2.SyncSolver(page, google_cloud_credentials=None, force_google_cloud=True)


def test_google_cloud_credentials_from_env() -> None:
    """Test that Google Cloud credentials can be loaded from environment variable."""
    import os
    
    # Save original value
    original_creds = os.environ.get("GOOGLE_CLOUD_CREDENTIALS")
    
    try:
        # Set environment variable
        os.environ["GOOGLE_CLOUD_CREDENTIALS"] = "test-credentials.json"
        
        with sync_playwright() as playwright:
            browser = playwright.firefox.launch()
            page = browser.new_page()
            
            # Should not raise an error during initialization
            solver = recaptchav2.SyncSolver(page)
            assert solver._google_cloud_credentials == "test-credentials.json"
            solver.close()
    
    finally:
        # Restore original value
        if original_creds is None:
            os.environ.pop("GOOGLE_CLOUD_CREDENTIALS", None)
        else:
            os.environ["GOOGLE_CLOUD_CREDENTIALS"] = original_creds


def test_force_google_cloud_without_credentials() -> None:
    """Test that force_google_cloud=True raises error without credentials."""
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch()
        page = browser.new_page()
        
        # Should raise ValueError during initialization
        with pytest.raises(ValueError, match="Google Cloud credentials are required when force_google_cloud=True"):
            recaptchav2.SyncSolver(page, force_google_cloud=True)


def test_force_google_cloud_with_credentials() -> None:
    """Test that force_google_cloud=True works with credentials provided."""
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch()
        page = browser.new_page()
        
        # Should not raise error during initialization when credentials are provided
        # (Even though the file doesn't exist, this tests the parameter logic)
        try:
            solver = recaptchav2.SyncSolver(
                page, 
                google_cloud_credentials="dummy-path.json",
                force_google_cloud=True
            )
            # This will fail on file validation, which is expected
        except (FileNotFoundError, ValueError) as e:
            # Expected - file doesn't exist or is invalid
            assert "not found" in str(e) or "Cannot read" in str(e)
        else:
            solver.close()
