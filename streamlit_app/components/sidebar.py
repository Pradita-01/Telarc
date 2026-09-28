import streamlit as st


def render_sidebar():
    with st.sidebar:

        st.markdown(
            """
            <div style="
                font-size: 1.35rem;
                font-weight: 700;
                margin-bottom: 0.25rem;
            ">
                📡 Telarc
            </div>

            <div style="
                color: #888;
                font-size: 0.85rem;
                margin-bottom: 1.5rem;
            ">
                Telecom Knowledge Assistant
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        st.markdown("#### Knowledge Base")

        st.caption(
            "Telarc searches an indexed collection of "
            "telecom reports, financial statements, "
            "standards and technical documentation."
        )

        st.divider()

        st.markdown("#### Grounded answers")

        st.caption(
            "Answers are generated only when the retrieved "
            "documents provide sufficient evidence."
        )

        st.divider()

        st.caption("Telarc")