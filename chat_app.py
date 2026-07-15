import streamlit as st
from dotenv import load_dotenv
from repo_rag.generator import chat

load_dotenv()

from repo_rag.retriever import HybridRetriever
from repo_rag.generator import ask

st.set_page_config(page_title="Ask My Repos", page_icon="🔍")
st.title("🔍 Ask My Repos")

@st.cache_resource
def load_retriever():
    return HybridRetriever()

retriever = load_retriever()

if "messages" not in st.session_state:
    st.session_state.messages = []

# render the conversation so far
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# handle a new question
if prompt := st.chat_input("Ask about your repos..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching your code..."):
            answer, chunks = ask(prompt, retriever)
        st.markdown(answer)
        with st.expander("Sources"):
            for c in chunks:
                m = c["meta"]
                st.write(f"`{m['repo']}/{m['file_path']}:{m['start_line']}-{m['end_line']}`")

    st.session_state.messages.append({"role": "assistant", "content": answer})


