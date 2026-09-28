from app.rag.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


def test_system_prompt_requires_grounding():
    assert "ONLY from the evidence" in SYSTEM_PROMPT
    assert "Do NOT use your general knowledge" in SYSTEM_PROMPT
    assert "answerable" in SYSTEM_PROMPT
    assert "source_ids" in SYSTEM_PROMPT

def test_system_prompt_requires_json():
    assert "valid JSON" in SYSTEM_PROMPT
    assert '"answerable": true' in SYSTEM_PROMPT
    assert '"answerable": false' in SYSTEM_PROMPT


def test_user_prompt_requires_question_and_evidence():
    prompt = USER_PROMPT_TEMPLATE.format(
        question="What is 5G?",
        context="5G is a mobile network technology.",
    )

    assert "What is 5G?" in prompt
    assert "5G is a mobile network technology." in prompt


def test_user_prompt_requires_insufficient_evidence_response():
    prompt = USER_PROMPT_TEMPLATE.format(
        question="What is Airtel's satellite revenue?",
        context="Airtel expanded its 5G network.",
    )

    assert "answerable=false" in prompt
    assert "insufficient" in prompt.lower()


def test_generator_builds_prompt():
    from app.rag.generator import LocalGenerator

    generator = LocalGenerator.__new__(LocalGenerator)

    prompt = generator.build_prompt(
        question="What is 5G?",
        context="5G is a mobile network technology.",
    )

    assert "What is 5G?" in prompt
    assert "5G is a mobile network technology." in prompt


def test_generator_parses_answerable_response():
    from app.rag.generator import LocalGenerator

    generator = LocalGenerator.__new__(LocalGenerator)

    response = generator._parse_response(
        """
        {
            "answerable": true,
            "answer": "5G is a mobile network technology.",
            "source_ids": [1]
        }
        """
    )

    assert response["answerable"] is True
    assert response["answer"] == "5G is a mobile network technology."
    assert response["source_ids"] == [1]


def test_generator_parses_abstention_response():
    from app.rag.generator import LocalGenerator

    generator = LocalGenerator.__new__(LocalGenerator)

    response = generator._parse_response(
        """
        {
            "answerable": false,
            "answer": "I couldn't find sufficient evidence in the indexed documents to answer this question.",
            "source_ids": []
        }
        """
    )

    assert response["answerable"] is False
    assert response["source_ids"] == []
    assert "couldn't find sufficient evidence" in response["answer"]


def test_generator_rejects_invalid_json():
    from app.rag.generator import LocalGenerator

    generator = LocalGenerator.__new__(LocalGenerator)

    response = generator._parse_response(
        "This is not valid JSON."
    )

    assert response["answerable"] is False
    assert response["source_ids"] == []


def test_generator_returns_structured_answer():
    from app.rag.generator import LocalGenerator

    class FakeResponse:
        text = """
        {
            "answerable": true,
            "answer": "5G is a mobile network technology.",
            "source_ids": [1]
        }
        """

    class FakeModels:
        def generate_content(
            self,
            model,
            contents,
            config,
        ):
            assert model == "gemini-3.1-flash-lite"
            assert "What is 5G?" in contents
            assert "5G is a mobile network technology." in contents
            assert config["max_output_tokens"] == 400
            assert config["response_mime_type"] == "application/json"

            return FakeResponse()

    class FakeClient:
        models = FakeModels()

    generator = LocalGenerator.__new__(LocalGenerator)
    generator.client = FakeClient()
    generator.model_name = "gemini-3.1-flash-lite"

    result = generator.generate_structured(
        question="What is 5G?",
        context="5G is a mobile network technology.",
    )

    assert result["answerable"] is True
    assert result["answer"] == "5G is a mobile network technology."
    assert result["source_ids"] == [1]