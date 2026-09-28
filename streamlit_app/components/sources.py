import streamlit as st


def render_sources(citations: list[dict]):
    if not citations:
        return

    st.markdown("### Sources")

    for citation in citations:
        with st.expander(
            f"Source {citation['source_id']} — "
            f"{citation['document']} — Page {citation['page']}"
        ):
            st.write(f"**Document:** {citation['document']}")
            st.write(f"**Page:** {citation['page']}")
            st.write(f"**Chunk ID:** `{citation['chunk_id']}`")
            st.write(f"**Retrieval score:** {citation['score']:.4f}")