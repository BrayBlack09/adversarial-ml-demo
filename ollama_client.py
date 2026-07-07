"""Thin wrapper around the local Ollama HTTP API.

We talk to the model Ollama is already serving on localhost:11434. Keeping this
in one place means the rest of the code never has to know about HTTP details.
"""

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"


def chat(system_prompt: str, user_content: str, temperature: float = 0.0,
         model: str = MODEL) -> str:
    """Send one system+user turn to the model and return its reply text.

    temperature=0.0 makes the model as deterministic as it can be, so that when
    we re-run the same payload we get (nearly) the same answer. That matters for
    a measurement study: we want the attack success rate to reflect the payload,
    not random sampling noise.

    `model` is overridable so the judge can (optionally) run on a different model
    than the one under attack.
    """
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "stream": False,
            "options": {"temperature": temperature},
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]
