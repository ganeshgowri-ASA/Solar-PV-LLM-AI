"""
Chat Page - Standalone Streamlit page
AI Chat Assistant for Solar PV questions with RAG-powered responses.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import get_client, ExpertiseLevel

st.set_page_config(page_title="Chat - Solar PV AI", page_icon="💬", layout="wide")

st.title("💬 Solar PV Chat Assistant")
st.markdown("Ask questions about solar PV systems, IEC standards, testing procedures, and more.")

client = get_client()

# Initialize chat history
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Chat settings
with st.expander("⚙️ Chat Settings"):
    col1, col2 = st.columns(2)

    with col1:
        expertise = st.selectbox(
            "Expertise Level",
            options=["Beginner", "Intermediate", "Expert"],
            index=1,
            help="Adjusts response complexity"
        )
        expertise_map = {
            "Beginner": ExpertiseLevel.BEGINNER,
            "Intermediate": ExpertiseLevel.INTERMEDIATE,
            "Expert": ExpertiseLevel.EXPERT
        }

    with col2:
        include_sources = st.checkbox("Include Sources", value=True)

st.markdown("---")

# Display chat history
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.markdown(f"- **{source.get('source', 'Source')}**: {source.get('text', '')}")

# Empty state
if len(st.session_state.chat_messages) == 0:
    st.info("👋 Start a conversation by asking about solar PV systems, standards, calculations, or any related topic.")

# Chat input
user_input = st.chat_input("Ask about solar PV systems, IEC standards, testing procedures...")

if user_input:
    # Add user message
    st.session_state.chat_messages.append({"role": "user", "content": user_input})

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat_query(
                    query=user_input,
                    expertise_level=expertise_map.get(expertise, ExpertiseLevel.INTERMEDIATE)
                )

                if response.success:
                    answer = response.data.get("response", "I apologize, but I couldn't generate a response.")
                    sources = response.data.get("citations", [])

                    st.markdown(answer)

                    if sources and include_sources:
                        with st.expander("📚 Sources"):
                            for source in sources:
                                st.markdown(f"- **{source.get('source', 'Source')}**: {source.get('text', '')}")

                    # Add to history
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources if include_sources else []
                    })
                else:
                    error_msg = f"Error: {response.error}"
                    st.error(error_msg)
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Sidebar controls
with st.sidebar:
    st.markdown("### Chat Controls")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_messages = []
        st.rerun()

    if st.session_state.chat_messages:
        chat_export = "\n\n".join([
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in st.session_state.chat_messages
        ])
        st.download_button(
            "💾 Export Chat",
            chat_export,
            "chat_history.txt",
            "text/plain",
            use_container_width=True
        )

    st.markdown("---")
    st.markdown("### Chat Stats")
    total = len(st.session_state.chat_messages)
    user_msgs = sum(1 for m in st.session_state.chat_messages if m["role"] == "user")
    st.metric("Total Messages", total)
    st.metric("Your Questions", user_msgs)

# Suggested questions
st.markdown("---")
st.markdown("### 💡 Suggested Questions")

suggested = [
    "What are the key tests in IEC 61215?",
    "How do I calculate solar panel efficiency?",
    "What safety requirements apply to PV modules?",
    "Explain thermal cycling test procedures",
    "How do I size a solar PV system?",
    "What is the difference between IEC 61215 and IEC 61730?"
]

cols = st.columns(2)
for i, question in enumerate(suggested):
    with cols[i % 2]:
        if st.button(question, key=f"suggested_{i}", use_container_width=True):
            # Add question to chat
            st.session_state.chat_messages.append({"role": "user", "content": question})

            # Get response
            try:
                response = client.chat_query(
                    query=question,
                    expertise_level=expertise_map.get(expertise, ExpertiseLevel.INTERMEDIATE)
                )

                if response.success:
                    answer = response.data.get("response", "I couldn't generate a response.")
                    sources = response.data.get("citations", [])
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources if include_sources else []
                    })
                else:
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": f"Error: {response.error}"
                    })
            except Exception as e:
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": f"Error: {str(e)}"
                })

            st.rerun()
