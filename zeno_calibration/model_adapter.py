import requests
import uuid
import time

class ModelAdapter:
    """
    Minimal model adapter for Zeno Calibration.
    Works with any OpenAI-style chat completion endpoint.

    Expected config:
    {
        "type": "openai_chat",
        "endpoint": "http://localhost:1234/v1/chat/completions",
        "model_name": "my-model",
        "api_key_env": ""   # optional
    }
    """

    def __init__(self, config: dict):
        self.config = config
        self.endpoint = config.get("endpoint")
        self.model_name = config.get("model_name", "")
        self.api_key = config.get("api_key_env", "")

    def send(self, messages, temperature=0.2):
        """
        messages = [
          {"role": "user", "content": "..."}
        ]
        Returns: model text output as string.
        """

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature
        }

        headers = {
            "Content-Type": "application/json"
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            r = requests.post(self.endpoint, json=payload, headers=headers, timeout=60)
            r.raise_for_status()

            data = r.json()
            return data["choices"][0]["message"]["content"].strip()

        except Exception as e:
            return f"[ZENO_MODEL_ERROR] {str(e)}"


def make_adapter(config: dict):
    """
    Factory for creating a ModelAdapter.
    Future versions may add other adapter types.
    """
    adapter_type = config.get("type", "")

    if adapter_type == "openai_chat":
        return ModelAdapter(config)

    raise ValueError(f"Unsupported adapter type: {adapter_type}")
