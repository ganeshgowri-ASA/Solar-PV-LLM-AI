"""
Chat Assistant Page - Standalone Streamlit page
For use with Streamlit's multi-page app feature.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import get_client, ExpertiseLevel

st.set_page_config(page_title="Chat Assistant - Solar PV AI", page_icon="", layout="wide")

st.title("Chat with Solar PV AI")
st.markdown("Ask any question about solar PV systems, installation, standards, or calculations.")

# Initialize
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

client = get_client()

# Settings
with st.sidebar:
    expertise = st.selectbox(
        "Expertise Level",
        options=[e.value for e in ExpertiseLevel],
        index=1
    )
    stream_enabled = st.checkbox("Enable Streaming", value=False)

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.conversation_id = None
        st.rerun()

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if query := st.chat_input("Ask about solar PV systems..."):
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.write(query)

    # Get response
    with st.chat_message("assistant"):
        if stream_enabled:
            response_placeholder = st.empty()
            full_response = ""
            for token in client.chat_stream(query, ExpertiseLevel(expertise), st.session_state.conversation_id):
                full_response += token
                response_placeholder.markdown(full_response + "")
            response_placeholder.markdown(full_response)
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})
        else:
            with st.spinner("Thinking..."):
                response = client.chat_query(query, ExpertiseLevel(expertise), st.session_state.conversation_id)

            if response.success:
                data = response.data
                st.session_state.conversation_id = data.get("conversation_id")
                answer = data.get("response", "Sorry, I couldn't generate a response.")
                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})

                # Citations
                if data.get("citations"):
                    with st.expander("View Citations"):
                        for cite in data["citations"]:
                            st.markdown(f"**{cite.get('source')}** - {cite.get('text', '')}")
            else:
                st.error(response.error)
                st.session_state.chat_history.append({"role": "assistant", "content": f"Error: {response.error}"})

    st.rerun()
