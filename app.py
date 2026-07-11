import streamlit as st
from cloner import clone_repo, cleanup_repo
from parser import parse_repo
from embedder import index_chunks
from main_test import search
from llm import ask_llm

st.set_page_config(page_title="Chat with your codebase", layout="wide")

st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background: linear-gradient(180deg, #0e1117 0%, #131722 100%);
    }
    h1 {
        background: linear-gradient(90deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    .stButton button {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
    }
    .stChatMessage {
        background-color: #1c2128;
        border-radius: 12px;
        border: 1px solid #30363d;
        padding: 8px;
    }
    .stTextInput input, .stChatInput textarea {
        background-color: #1c2128;
        border: 1px solid #30363d;
        border-radius: 8px;
        color: white;
    }
    div[data-testid="stExpander"] {
        background-color: #1c2128;
        border-radius: 8px;
        border: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

if "repo_loaded" not in st.session_state:
    st.session_state.repo_loaded = False
if "messages" not in st.session_state:
    st.session_state.messages = []

st.sidebar.markdown("### 📂 Load a repository")
github_url = st.sidebar.text_input("GitHub URL")

if st.sidebar.button("Load Repo"):
    with st.spinner("Cloning and indexing... this may take a minute"):
        path = clone_repo(github_url)
        chunks = parse_repo(path)
        count = index_chunks(chunks)
        cleanup_repo(path)
        st.session_state.repo_loaded = True
        st.session_state.chunk_count = count
    st.sidebar.success("✅ Indexed successfully")
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Chunks", count)
    col2.metric("Model", "BAAI")

if st.session_state.repo_loaded:
    st.sidebar.info(f"{st.session_state.chunk_count} chunks ready to search")

st.markdown("# 🤖 Chat with your codebase")
st.caption("Ask questions about any GitHub repository in plain English")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_question = st.chat_input("Ask something about the code")

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.write(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Searching and thinking..."):
            chunks = search(user_question, top_k=3)
            answer = ask_llm(user_question, chunks)
            st.write(answer)

            with st.expander("View source code used"):
                for c in chunks:
                    label = f"{c['class']}.{c['function']}" if c['class'] else c['function']
                    st.markdown(f"**{label}** — `{c['file']}` — similarity: `{c['score']:.2f}`")
                    st.code(c['code'], language="python")

    st.session_state.messages.append({"role": "assistant", "content": answer})