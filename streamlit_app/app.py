from pathlib import Path
import json

import requests
import streamlit as st

from components.sources import render_sources
from components.sidebar import render_sidebar


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000/query"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
HISTORY_FILE = DATA_DIR / "chat_history.json"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Telarc",
    page_icon="⌁",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 900px;
        padding-top: 45px;
        padding-bottom: 100px;
    }

    h1 {
        text-align: center !important;
        font-family: Arial, Helvetica, sans-serif !important;
        font-size: 52px !important;
        font-weight: 800 !important;
        letter-spacing: -3px !important;
        margin-bottom: 5px !important;
    }

    .telarc-subtitle {
        text-align: center;
        color: #777777;
        font-size: 15px;
        margin-bottom: 45px;
    }

    [data-testid="stChatMessage"] {
        padding-top: 12px;
        padding-bottom: 12px;
    }

    [data-testid="stChatMessage"]:has(
        [data-testid="chatAvatarIcon-user"]
    ) {
        background: transparent;
    }

    [data-testid="stChatInput"] {
        border-radius: 20px !important;
    }

    [data-testid="stChatInput"] textarea {
        background-color: #eeeeee !important;
        color: #111111 !important;
        caret-color: #111111 !important;
        border: 1px solid #cccccc !important;
        border-radius: 20px !important;
        font-size: 16px !important;
        padding: 15px 55px 15px 18px !important;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.12) !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #777777 !important;
        opacity: 1 !important;
    }

    [data-testid="stChatInput"] textarea:focus {
        border-color: #999999 !important;
        color: #111111 !important;
        background-color: #eeeeee !important;
        box-shadow: 0 5px 25px rgba(0, 0, 0, 0.16) !important;
    }

    [data-testid="stChatInput"] button {
        background-color: #111111 !important;
        color: #ffffff !important;
        border-radius: 50% !important;
    }

    [data-testid="stChatInput"] button:hover {
        background-color: #333333 !important;
        color: #ffffff !important;
    }

    [data-testid="stExpander"] {
        border-radius: 12px;
        border: 1px solid #dddddd;
    }

    @media (max-width: 700px) {

        h1 {
            font-size: 40px !important;
        }

        .block-container {
            padding-left: 18px;
            padding-right: 18px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CHAT HISTORY
# ============================================================

def load_chat_history() -> list[dict]:
    """
    Load persistent Telarc conversation history.
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not HISTORY_FILE.exists():
        return []

    try:

        with HISTORY_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return data

    except (
        OSError,
        json.JSONDecodeError,
    ):
        pass

    return []


def save_chat_history(messages: list[dict]) -> None:
    """
    Persist Telarc conversation history.
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = HISTORY_FILE.with_suffix(
        ".tmp"
    )

    with temporary_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            messages,
            file,
            ensure_ascii=False,
            indent=2,
        )

    temporary_file.replace(
        HISTORY_FILE
    )


# Load history only once per Streamlit session.

if "messages" not in st.session_state:

    st.session_state.messages = (
        load_chat_history()
    )


# ============================================================
# SIDEBAR
# ============================================================

render_sidebar()

with st.sidebar:

    st.divider()

    if st.button(
        "Clear conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        if HISTORY_FILE.exists():
            HISTORY_FILE.unlink()

        st.rerun()


# ============================================================
# HEADER
# ============================================================

st.title("⌁ TELARC")

st.markdown(
    '<div class="telarc-subtitle">'
    "Telecom Intelligence · Grounded in your documents"
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# DISPLAY EXISTING CONVERSATION
# ============================================================

for message in st.session_state.messages:

    role = message.get(
        "role",
        "assistant",
    )

    content = message.get(
        "content",
        "",
    )

    with st.chat_message(role):

        st.markdown(content)

        if role == "assistant":

            render_sources(
                message.get(
                    "citations",
                    [],
                )
            )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask Telarc anything about your telecom documents..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    question = question.strip()

    if not question:

        st.warning(
            "Please enter a question."
        )

        st.stop()

    # --------------------------------------------------------
    # Store user message
    # --------------------------------------------------------

    user_message = {
        "role": "user",
        "content": question,
    }

    st.session_state.messages.append(
        user_message
    )

    save_chat_history(
        st.session_state.messages
    )

    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)

    # --------------------------------------------------------
    # Call Telarc API
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching the telecom knowledge base..."
        ):

            try:

                response = requests.post(
                    API_URL,
                    json={
                        "question": question
                    },
                    timeout=120,
                )

                response.raise_for_status()

                result = response.json()

                answer = result.get(
                    "answer",
                    "I couldn't generate an answer.",
                )

                citations = result.get(
                    "citations",
                    [],
                )

                answerable = result.get(
                    "answerable",
                    False,
                )

                # ------------------------------------------------
                # Display answer
                # ------------------------------------------------

                st.markdown(answer)

                # ------------------------------------------------
                # Display sources
                # ------------------------------------------------

                render_sources(
                    citations
                )

                # ------------------------------------------------
                # Persist assistant response
                # ------------------------------------------------

                assistant_message = {
                    "role": "assistant",
                    "content": answer,
                    "answerable": answerable,
                    "citations": citations,
                }

                st.session_state.messages.append(
                    assistant_message
                )

                save_chat_history(
                    st.session_state.messages
                )

            except requests.exceptions.ConnectionError:

                st.error(
                    "I couldn't connect to the Telarc API. "
                    "Please make sure FastAPI is running "
                    "on port 8000."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out. "
                    "Please try again."
                )

            except requests.exceptions.RequestException as exc:

                st.error(
                    f"API request failed: {exc}"
                )