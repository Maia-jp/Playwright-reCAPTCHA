import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Generic, Iterable, Optional, TypeVar, Union

from playwright.async_api import APIResponse as AsyncAPIResponse
from playwright.async_api import Page as AsyncPage
from playwright.async_api import Response as AsyncResponse
from playwright.sync_api import APIResponse as SyncAPIResponse
from playwright.sync_api import Page as SyncPage
from playwright.sync_api import Response as SyncResponse

from .recaptcha_box import RecaptchaBox

PageT = TypeVar("PageT", AsyncPage, SyncPage)
APIResponse = Union[AsyncAPIResponse, SyncAPIResponse]
Response = Union[AsyncResponse, SyncResponse]


class BaseSolver(ABC, Generic[PageT]):
    """
    The base class for reCAPTCHA v2 solvers.

    Parameters
    ----------
    page : PageT
        The Playwright page to solve the reCAPTCHA on.
    attempts : int, optional
        The number of solve attempts, by default 5.
    capsolver_api_key : Optional[str], optional
        The CapSolver API key, by default None.
        If None, the `CAPSOLVER_API_KEY` environment variable will be used.
    google_cloud_credentials : Optional[str], optional
        Path to the Google Cloud credentials JSON file, by default None.
        If None, the `GOOGLE_CLOUD_CREDENTIALS` environment variable will be used.
        Required for audio challenge solving with Google Cloud Speech-to-Text API.
    force_google_cloud : bool, optional
        If True, forces the use of Google Cloud Speech-to-Text API and raises
        an error if credentials are not provided, by default False.
    """

    def __init__(
        self, 
        page: PageT, 
        *, 
        attempts: int = 5, 
        capsolver_api_key: Optional[str] = None,
        google_cloud_credentials: Optional[str] = None,
        force_google_cloud: bool = False
    ) -> None:
        self._page = page
        self._attempts = attempts
        self._capsolver_api_key = capsolver_api_key or os.getenv("CAPSOLVER_API_KEY")
        self._google_cloud_credentials = google_cloud_credentials or os.getenv("GOOGLE_CLOUD_CREDENTIALS")
        self._force_google_cloud = force_google_cloud
        
        # If force_google_cloud is True, ensure credentials are provided
        if self._force_google_cloud and not self._google_cloud_credentials:
            raise ValueError(
                "Google Cloud credentials are required when force_google_cloud=True. "
                "Provide google_cloud_credentials parameter or set GOOGLE_CLOUD_CREDENTIALS environment variable."
            )
        
        # Validate Google Cloud credentials if provided
        if self._google_cloud_credentials:
            self._validate_google_cloud_credentials()

        self._token: Optional[str] = None
        self._payload_response: Union[APIResponse, Response, None] = None
        self._page.on("response", self._response_callback)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(page={self._page!r}, "
            f"attempts={self._attempts!r}, "
            f"capsolver_api_key={self._capsolver_api_key!r}, "
            f"google_cloud_credentials={self._google_cloud_credentials!r}, "
            f"force_google_cloud={self._force_google_cloud!r})"
        )

    def close(self) -> None:
        """Remove the response listener."""
        try:
            self._page.remove_listener("response", self._response_callback)
        except KeyError:
            pass

    def _validate_google_cloud_credentials(self) -> None:
        """
        Validate the Google Cloud credentials file.
        
        Raises
        ------
        FileNotFoundError
            If the credentials file does not exist.
        ValueError
            If the credentials file is not valid JSON or missing required fields.
        """
        if not self._google_cloud_credentials:
            return

        credentials_path = Path(self._google_cloud_credentials)
        
        # Check if file exists
        if not credentials_path.exists():
            raise FileNotFoundError(
                f"Google Cloud credentials file not found: {self._google_cloud_credentials}"
            )
        
        # Check if file is readable and valid JSON
        try:
            with open(credentials_path, "r", encoding="utf-8") as f:
                credentials_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in Google Cloud credentials file: {self._google_cloud_credentials}. "
                f"Error: {e}"
            ) from e
        except (OSError, IOError) as e:
            raise ValueError(
                f"Cannot read Google Cloud credentials file: {self._google_cloud_credentials}. "
                f"Error: {e}"
            ) from e
        
        # Validate required fields for service account key
        required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
        missing_fields = [field for field in required_fields if field not in credentials_data]
        
        if missing_fields:
            raise ValueError(
                f"Google Cloud credentials file is missing required fields: {missing_fields}. "
                f"Ensure you are using a valid service account key file."
            )

    @staticmethod
    @abstractmethod
    def _get_task_object(recaptcha_box: RecaptchaBox) -> Optional[str]:
        """
        Get the ID of the object in the reCAPTCHA image challenge task.

        Parameters
        ----------
        recaptcha_box : RecaptchaBox
            The reCAPTCHA box.

        Returns
        -------
        Optional[str]
            The object ID. Returns None if the task object is not recognized.
        """

    @abstractmethod
    def _response_callback(self, response: Response) -> None:
        """
        The callback for intercepting payload and userverify responses.

        Parameters
        ----------
        response : Response
            The response.
        """

    @abstractmethod
    def _get_capsolver_response(
        self, recaptcha_box: RecaptchaBox, image_data: bytes
    ) -> Optional[Dict[str, Any]]:
        """
        Get the CapSolver JSON response for an image.

        Parameters
        ----------
        recaptcha_box : RecaptchaBox
            The reCAPTCHA box.
        image_data : bytes
            The image data.

        Returns
        -------
        Optional[Dict[str, Any]]
            The CapSolver JSON response.
            Returns None if the task object is not recognized.

        Raises
        ------
        CapSolverError
            If the CapSolver API returned an error.
        """

    @abstractmethod
    def _solve_tiles(self, recaptcha_box: RecaptchaBox, indexes: Iterable[int]) -> None:
        """
        Solve the tiles in the reCAPTCHA image challenge.

        Parameters
        ----------
        recaptcha_box : RecaptchaBox
            The reCAPTCHA box.
        indexes : Iterable[int]
            The indexes of the tiles that contain the task object.

        Raises
        ------
        CapSolverError
            If the CapSolver API returned an error.
        """

    @abstractmethod
    def _transcribe_audio(self, audio_url: str, *, language: str) -> Optional[str]:
        """
        Transcribe the reCAPTCHA audio challenge.

        Parameters
        ----------
        audio_url : str
            The reCAPTCHA audio URL.
        language : str
            The language of the audio.

        Returns
        -------
        Optional[str]
            The reCAPTCHA audio text.
            Returns None if the audio could not be converted.
        """

    @abstractmethod
    def _click_checkbox(self, recaptcha_box: RecaptchaBox) -> None:
        """
        Click the reCAPTCHA checkbox.

        Parameters
        ----------
        recaptcha_box : RecaptchaBox
            The reCAPTCHA box.

        Raises
        ------
        RecaptchaRateLimitError
            If the reCAPTCHA rate limit has been exceeded.
        """

    @abstractmethod
    def _get_audio_url(self, recaptcha_box: RecaptchaBox) -> str:
        """
        Get the reCAPTCHA audio URL.

        Parameters
        ----------
        recaptcha_box : RecaptchaBox
            The reCAPTCHA box.

        Returns
        -------
        str
            The reCAPTCHA audio URL.

        Raises
        ------
        RecaptchaRateLimitError
            If the reCAPTCHA rate limit has been exceeded.
        """

    @abstractmethod
    def _submit_audio_text(self, recaptcha_box: RecaptchaBox, text: str) -> None:
        """
        Submit the reCAPTCHA audio text.

        Parameters
        ----------
        recaptcha_box : RecaptchaBox
            The reCAPTCHA box.
        text : str
            The reCAPTCHA audio text.

        Raises
        ------
        RecaptchaRateLimitError
            If the reCAPTCHA rate limit has been exceeded.
        """

    @abstractmethod
    def _submit_tile_answers(self, recaptcha_box: RecaptchaBox) -> None:
        """
        Submit the reCAPTCHA image challenge tile answers.

        Parameters
        ----------
        recaptcha_box : RecaptchaBox
            The reCAPTCHA box.

        Raises
        ------
        RecaptchaRateLimitError
            If the reCAPTCHA rate limit has been exceeded.
        """

    @abstractmethod
    def _solve_image_challenge(self, recaptcha_box: RecaptchaBox) -> None:
        """
        Solve the reCAPTCHA image challenge.

        Parameters
        ----------
        recaptcha_box : RecaptchaBox
            The reCAPTCHA box.

        Raises
        ------
        CapSolverError
            If the CapSolver API returned an error.
        RecaptchaRateLimitError
            If the reCAPTCHA rate limit has been exceeded.
        """

    @abstractmethod
    def _solve_audio_challenge(self, recaptcha_box: RecaptchaBox) -> None:
        """
        Solve the reCAPTCHA audio challenge.

        Parameters
        ----------
        recaptcha_box : RecaptchaBox
            The reCAPTCHA box.

        Raises
        ------
        RecaptchaRateLimitError
            If the reCAPTCHA rate limit has been exceeded.
        """

    @abstractmethod
    def recaptcha_is_visible(self) -> bool:
        """
        Check if a reCAPTCHA challenge or unchecked reCAPTCHA box is visible.

        Returns
        -------
        bool
            Whether a reCAPTCHA challenge or unchecked reCAPTCHA box is visible.
        """

    @abstractmethod
    def solve_recaptcha(
        self,
        *,
        attempts: Optional[int] = None,
        wait: bool = False,
        wait_timeout: float = 30,
        image_challenge: bool = False,
    ) -> str:
        """
        Solve the reCAPTCHA and return the `g-recaptcha-response` token.

        Parameters
        ----------
        attempts : Optional[int], optional
            The number of solve attempts, by default 5.
        wait : bool, optional
            Whether to wait for the reCAPTCHA to appear, by default False.
        wait_timeout : float, optional
            The amount of time in seconds to wait for the reCAPTCHA to appear,
            by default 30. Only used if `wait` is True.
        image_challenge : bool, optional
            Whether to solve the image challenge, by default False.

        Returns
        -------
        str
            The `g-recaptcha-response` token.

        Raises
        ------
        CapSolverError
            If the CapSolver API returned an error.
        RecaptchaNotFoundError
            If the reCAPTCHA was not found.
        RecaptchaRateLimitError
            If the reCAPTCHA rate limit has been exceeded.
        RecaptchaSolveError
            If the reCAPTCHA could not be solved.
        """
