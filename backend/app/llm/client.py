"""
Rawbank Sentient Fraud Intelligence Platform
Phase 6 Sentient Fraud Investigation Copilot - Groq API Client
-----------------------------------------------------------------------------
Server-side client for Groq LLM API communication.
Zero secrets in source code. Configurable via environment variables.
Provides robust timeout, rate limit, and error handling without exposing secrets.
"""

import json
import logging
import httpx
from typing import Dict, Any, Optional
from backend.app.config import settings

logger = logging.getLogger("rawbank_backend.llm")


class GroqConfigurationError(Exception):
    """Raised when Groq API is misconfigured or missing credentials."""
    pass


class GroqAPIError(Exception):
    """Raised when Groq API returns an HTTP error or malformed payload."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class GroqTimeoutError(Exception):
    """Raised when Groq API request times out."""
    pass


class GroqClient:
    """
    Communicates securely with Groq Cloud via OpenAI-compatible chat completions API.
    All calls are strictly server-side.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        api_url: Optional[str] = None,
        timeout_seconds: Optional[float] = None
    ):
        self.api_key = api_key or settings.groq_api_key
        self.model = model or settings.groq_model
        self.api_url = api_url or settings.groq_api_url
        self.timeout_seconds = timeout_seconds or settings.groq_timeout_seconds

    def is_configured(self) -> bool:
        """Checks if Groq API key is present."""
        return bool(self.api_key and self.api_key.strip())

    def generate_investigation(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """
        Sends synchronous request to Groq chat completions endpoint.
        Returns parsed JSON object response.
        """
        if not self.is_configured():
            raise GroqConfigurationError(
                "GROQ_API_KEY environment variable is not configured. "
                "Please configure GROQ_API_KEY in .env or run tests using mock adapter."
            )

        if not self.model or not self.model.strip():
            raise GroqConfigurationError(
                "GROQ_MODEL is not configured. Please specify a valid model such as 'llama-3.3-70b-versatile'."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }

        logger.info(f"Dispatching investigation prompt to Groq (model={self.model})")

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(self.api_url, headers=headers, json=payload)

            if response.status_code == 401:
                logger.error("Groq authentication failed (401 Unauthorized)")
                raise GroqAPIError("Invalid or unauthorized Groq API key.", status_code=401)
            elif response.status_code == 429:
                logger.warning("Groq rate limit exceeded (429 Too Many Requests)")
                raise GroqAPIError("Groq API rate limit exceeded. Please retry after a brief delay.", status_code=429)
            elif response.status_code >= 400:
                logger.error(f"Groq API returned HTTP {response.status_code}: {response.text}")
                raise GroqAPIError(
                    f"Groq API returned HTTP {response.status_code}",
                    status_code=response.status_code
                )

            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                raise GroqAPIError("Empty response received from Groq LLM (no choices returned).")

            message_content = choices[0].get("message", {}).get("content", "")
            if not message_content or not message_content.strip():
                raise GroqAPIError("Empty content string returned from Groq LLM.")

            try:
                parsed_json = json.loads(message_content)
                return parsed_json
            except json.JSONDecodeError as jde:
                logger.error(f"Failed to parse LLM JSON output: {jde}. Raw content: {message_content[:200]}")
                raise GroqAPIError(f"Malformed JSON returned by LLM: {str(jde)}")

        except httpx.TimeoutException as te:
            logger.error(f"Groq API request timed out after {self.timeout_seconds}s: {te}")
            raise GroqTimeoutError(f"Groq LLM request timed out after {self.timeout_seconds} seconds.")
        except httpx.RequestError as re:
            logger.error(f"Network error communicating with Groq API: {re}")
            raise GroqAPIError(f"Network error connecting to Groq API: {re.__class__.__name__}")
