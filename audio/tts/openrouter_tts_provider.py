import os
import httpx

from audio.tts.base_tts import BaseTTS
from audio.playback import play_mp3_async


OPENROUTER_TTS_URL = "https://openrouter.ai/api/v1/audio/speech"


class OpenRouterTTSProvider(BaseTTS):
    """OpenRouter TTS provider."""

    def __init__(self):
        self._api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self._model = os.getenv(
            "OPENROUTER_TTS_MODEL",
            "fish-audio/s2.1-pro-free",
        ).strip()
        self._voice = os.getenv("OPENROUTER_TTS_VOICE", "").strip()

    async def speak(self, text: str) -> None:
        if not text.strip():
            return

        if not self._api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set")

        payload = {
            "model": self._model,
            "input": text,
            "response_format": "mp3",
        }

        # Fish Audio does not require a preset voice ID.
        # Only send voice when one is explicitly configured.
        if self._voice:
            payload["voice"] = self._voice

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "X-OpenRouter-Title": "Clicky Windows",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                OPENROUTER_TTS_URL,
                headers=headers,
                json=payload,
            )

            if response.status_code >= 400:
                raise RuntimeError(
                    f"OpenRouter TTS error {response.status_code}: "
                    f"{response.text[:500]}"
                )

            audio_bytes = response.content

        await play_mp3_async(audio_bytes)