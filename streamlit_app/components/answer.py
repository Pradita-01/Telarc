import streamlit as st


def render_answer(result: dict):
    if result["answerable"]:
        st.markdown("### Answer")
        st.markdown(result["answer"])
    else:
        st.markdown("### Answer")
        st.markdown(
            f"""
            <div style="
                color: #555;
                background: #eeeeee;
                border-radius: 14px;
                padding: 14px 18px;
                line-height: 1.6;
            ">
                {result["answer"]}
            </div>
            """,
            unsafe_allow_html=True,
        )