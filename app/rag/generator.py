import json
import os
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

from app.rag.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


ABSTAIN_MESSAGE = (
    "I couldn't find sufficient evidence in the indexed documents "
    "to answer this question."
)


class LocalGenerator:
    def __init__(self, model_name: str = "gemini-3.1-flash-lite"):
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY was not found in the environment."
            )

        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)

    def build_prompt(
        self,
        question: str,
        context: str,
    ) -> str:
        user_prompt = USER_PROMPT_TEMPLATE.format(
            question=question,
            context=context,
        )

        return f"{SYSTEM_PROMPT}\n\n{user_prompt}"

    def _parse_response(self, text: str) -> dict:
        text = text.strip()

        # Remove markdown code fences if Gemini returns them.
        if text.startswith("```"):
            text = re.sub(
                r"^```(?:json)?\s*",
                "",
                text,
            )

            text = re.sub(
                r"\s*```$",
                "",
                text,
            )

        try:
            data = json.loads(text)

        except json.JSONDecodeError:
            return {
                "answerable": False,
                "answer": ABSTAIN_MESSAGE,
                "source_ids": [],
            }

        answerable = bool(
            data.get("answerable", False)
        )

        answer = str(
            data.get("answer", "")
        ).strip()

        source_ids = data.get(
            "source_ids",
            [],
        )

        if not isinstance(source_ids, list):
            source_ids = []

        cleaned_source_ids = []

        for source_id in source_ids:
            try:
                cleaned_source_ids.append(
                    int(source_id)
                )

            except (TypeError, ValueError):
                continue

        if not answerable or not answer:
            return {
                "answerable": False,
                "answer": ABSTAIN_MESSAGE,
                "source_ids": [],
            }

        return {
            "answerable": True,
            "answer": answer,
            "source_ids": cleaned_source_ids,
        }

    def generate_structured(
        self,
        question: str,
        context: str,
        max_output_tokens: int = 400,
    ) -> dict:

        prompt = self.build_prompt(
            question,
            context,
        )

        # Gemini can temporarily return 503 when the model
        # is experiencing high demand. Retry a few times
        # before allowing the error to propagate.
        max_attempts = 3

        for attempt in range(max_attempts):

            try:
                response = (
                    self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config={
                            "max_output_tokens": max_output_tokens,
                            "response_mime_type": "application/json",
                        },
                    )
                )

                if not response.text:
                    return {
                        "answerable": False,
                        "answer": ABSTAIN_MESSAGE,
                        "source_ids": [],
                    }

                return self._parse_response(
                    response.text
                )

            except errors.ServerError as exc:

                # Retry temporary Gemini server failures.
                if attempt < max_attempts - 1:

                    wait_seconds = 2 ** attempt

                    print(
                        f"Gemini server unavailable "
                        f"(attempt {attempt + 1}/{max_attempts}). "
                        f"Retrying in {wait_seconds}s..."
                    )

                    time.sleep(
                        wait_seconds
                    )

                else:
                    # All retries exhausted.
                    print(
                        "Gemini server remained unavailable "
                        "after all retry attempts."
                    )

                    raise exc

    def generate(
        self,
        question: str,
        context: str,
        max_new_tokens: int = 300,
    ) -> str:

        result = self.generate_structured(
            question=question,
            context=context,
            max_output_tokens=max_new_tokens,
        )

        return result["answer"]