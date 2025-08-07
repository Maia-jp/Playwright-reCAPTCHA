import pytest
from playwright.async_api import async_playwright

from playwright_recaptcha import (
    CapSolverError,
    RecaptchaNotFoundError,
    RecaptchaRateLimitError,
    RecaptchaSolveError,
    recaptchav2,
)


@pytest.mark.asyncio
@pytest.mark.xfail(raises=RecaptchaRateLimitError)
async def test_solver_with_normal_recaptcha() -> None:
    """Test the solver with a normal reCAPTCHA."""
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch()
        page = await browser.new_page()
        await page.goto("https://www.google.com/recaptcha/api2/demo")

        async with recaptchav2.AsyncSolver(page) as solver:
            await solver.solve_recaptcha(wait=True)


@pytest.mark.asyncio
@pytest.mark.xfail(raises=(RecaptchaNotFoundError, RecaptchaRateLimitError))
async def test_solver_with_hidden_recaptcha() -> None:
    """Test the solver with a hidden reCAPTCHA."""
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch()
        page = await browser.new_page()

        await page.goto("https://www.google.com/recaptcha/api2/demo?invisible=true")
        await page.get_by_role("button").click()

        async with recaptchav2.AsyncSolver(page) as solver:
            await solver.solve_recaptcha(wait=True)


@pytest.mark.asyncio
@pytest.mark.xfail(raises=RecaptchaRateLimitError)
async def test_solver_with_slow_browser() -> None:
    """Test the solver with a slow browser."""
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch(slow_mo=1000)
        page = await browser.new_page()
        await page.goto("https://www.google.com/recaptcha/api2/demo")

        async with recaptchav2.AsyncSolver(page) as solver:
            await solver.solve_recaptcha(wait=True)


@pytest.mark.asyncio
@pytest.mark.xfail(raises=CapSolverError)
async def test_solver_with_image_challenge() -> None:
    """Test the solver with an image challenge."""
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch()
        page = await browser.new_page()
        await page.goto("https://www.google.com/recaptcha/api2/demo")

        async with recaptchav2.AsyncSolver(page) as solver:
            await solver.solve_recaptcha(wait=True, image_challenge=True)


@pytest.mark.asyncio
async def test_recaptcha_not_found_error() -> None:
    """Test the solver with a page that does not have a reCAPTCHA."""
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch()
        page = await browser.new_page()
        await page.goto("https://www.google.com/")

        with pytest.raises(RecaptchaNotFoundError):
            async with recaptchav2.AsyncSolver(page) as solver:
                await solver.solve_recaptcha()


@pytest.mark.asyncio
async def test_google_cloud_credentials_required() -> None:
    """Test that Google Cloud credentials are required for audio transcription."""
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch()
        page = await browser.new_page()
        await page.goto("https://www.google.com/recaptcha/api2/demo")

        # Test without credentials should raise RecaptchaSolveError
        with pytest.raises(RecaptchaSolveError, match="Google Cloud credentials are required"):
            async with recaptchav2.AsyncSolver(
                page, google_cloud_credentials=None
            ) as solver:
                await solver.solve_recaptcha(wait=True)


@pytest.mark.asyncio
async def test_google_cloud_credentials_from_env() -> None:
    """Test that Google Cloud credentials can be loaded from environment variable."""
    import os
    
    # Save original value
    original_creds = os.environ.get("GOOGLE_CLOUD_CREDENTIALS")
    
    try:
        # Set environment variable
        os.environ["GOOGLE_CLOUD_CREDENTIALS"] = "test-credentials.json"
        
        async with async_playwright() as playwright:
            browser = await playwright.firefox.launch()
            page = await browser.new_page()
            
            # Should not raise an error during initialization
            solver = recaptchav2.AsyncSolver(page)
            assert solver._google_cloud_credentials == "test-credentials.json"
            solver.close()
    
    finally:
        # Restore original value
        if original_creds is None:
            os.environ.pop("GOOGLE_CLOUD_CREDENTIALS", None)
        else:
            os.environ["GOOGLE_CLOUD_CREDENTIALS"] = original_creds
