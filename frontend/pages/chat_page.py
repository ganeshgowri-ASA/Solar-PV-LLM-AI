"""
Chat Interface Page
Main conversational interface with RAG-powered responses and citations
"""
import sys
from pathlib import Path

# Add project root to Python path for Streamlit Cloud
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
from backend.api.mock_service import mock_api
from frontend.utils.ui_components import (
    show_loading,
    show_error,
    render_message,
    show_empty_state,
)


def render():
    """Render the chat interface page"""
    st.title("💬 AI Chat Assistant")
    st.markdown(
        "Ask questions about solar PV systems, IEC standards, testing procedures, and more. "
        "All responses are backed by authoritative sources and citations."
    )

    # Chat settings in expander
    with st.expander("⚙️ Chat Settings"):
        col1, col2, col3 = st.columns(3)

        with col1:
            include_sources = st.checkbox("Include Sources", value=True)

        with col2:
            model_selection = st.selectbox(
                "Model",
                ["GPT-4 Turbo", "GPT-4", "GPT-3.5 Turbo"],
                index=0,
            )

        with col3:
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
            )

    st.divider()

    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    if len(st.session_state.chat_history) == 0:
        show_empty_state(
            title="Start a Conversation",
            message="Ask any question about solar PV systems, standards, testing, or calculations.",
            icon="💬",
        )
    else:
        for idx, message in enumerate(st.session_state.chat_history):
            is_user = message["role"] == "user"
            render_message(message, is_user=is_user)

    # Chat input
    user_input = st.chat_input(
        "Ask about IEC standards, testing procedures, calculations, or any solar PV topic..."
    )

    if user_input:
        # Add user message to history
        user_message = {
            "role": "user",
            "content": user_input,
        }
        st.session_state.chat_history.append(user_message)

        # Display user message
        render_message(user_message, is_user=True)

        # Get AI response
        with st.chat_message("assistant", avatar="🤖"):
            with show_loading("Thinking..."):
                response = mock_api.chat_completion(
                    user_input, include_sources=include_sources
                )

            # Display response
            st.markdown(response["content"])

            # Display sources if available
            if response.get("sources"):
                with st.expander("📚 Sources & Citations", expanded=False):
                    for idx, source in enumerate(response["sources"], 1):
                        st.markdown(
                            f"""
                            <div class="citation">
                                <div class="citation-title">{idx}. {source['title']}</div>
                                <div class="citation-excerpt">{source['excerpt']}</div>
                                <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #888;">
                                    📄 Page {source['page']} | Section: {source['section']} |
                                    Relevance: {source['relevance_score']:.1%}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

        # Add assistant message to history
        assistant_message = {
            "role": "assistant",
            "content": response["content"],
            "sources": response.get("sources", []),
        }
        st.session_state.chat_history.append(assistant_message)

    # Sidebar with chat controls
    with st.sidebar:
        st.divider()
        st.markdown("### Chat Controls")

        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

        if st.button("💾 Export Chat", use_container_width=True):
            chat_export = "\n\n".join(
                [
                    f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                    for msg in st.session_state.chat_history
                ]
            )
            st.download_button(
                label="Download as Text",
                data=chat_export,
                file_name="chat_history.txt",
                mime="text/plain",
                use_container_width=True,
            )

        # Show chat statistics
        st.divider()
        st.markdown("### Chat Statistics")
        st.metric("Total Messages", len(st.session_state.chat_history))
        user_messages = sum(
            1 for msg in st.session_state.chat_history if msg["role"] == "user"
        )
        st.metric("Your Questions", user_messages)

    # Quick action buttons
    st.divider()
    st.markdown("### 💡 Suggested Questions")

    col1, col2 = st.columns(2)

    suggested_questions = [
        "What are the key tests in IEC 61215?",
        "How do I calculate solar panel efficiency?",
        "What are the safety requirements for PV modules?",
        "Explain thermal cycling test procedures",
        "How to size a solar PV system?",
        "What is the difference between IEC 61215 and IEC 61730?",
    ]

    for i, question in enumerate(suggested_questions):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.button(
                question,
                key=f"suggested_{i}",
                use_container_width=True,
                type="secondary",
            ):
                # Simulate clicking with the suggested question
                st.session_state.suggested_question = question
                st.rerun()

    # Handle suggested question click
    if hasattr(st.session_state, "suggested_question"):
        question = st.session_state.suggested_question
        delattr(st.session_state, "suggested_question")

        # Add to chat
        user_message = {"role": "user", "content": question}
        st.session_state.chat_history.append(user_message)

        # Get response
        response = mock_api.chat_completion(question, include_sources=include_sources)
        assistant_message = {
            "role": "assistant",
            "content": response["content"],
            "sources": response.get("sources", []),
        }
        st.session_state.chat_history.append(assistant_message)
        st.rerun()
