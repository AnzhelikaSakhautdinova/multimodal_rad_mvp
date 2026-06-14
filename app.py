import streamlit as st
from src.search import search

st.title("Video RAG")

query = st.text_input("Search scene")

if query:
    results = search(query)

    for result in results:
        st.image(result["frame_path"], width=500)

        st.write(
            f"Timestamp: {result['timestamp']}"
        )

        st.write(
            f"Score: {result['score']:.3f}"
        )

        st.write(
            result["description"]
        )

        st.divider()