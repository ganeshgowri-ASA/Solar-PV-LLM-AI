"""
Reusable UI components for the Solar PV LLM AI System
"""
import streamlit as st
import time
from typing import Optional, Callable, Any


def show_loading(message: str = "Processing..."):
    """Display a loading spinner with a message"""
    return st.spinner(message)


def show_success(message: str, icon: str = "✅"):
    """Display a success message"""
    st.success(f"{icon} {message}")


def show_error(message: str, icon: str = "❌"):
    """Display an error message"""
    st.error(f"{icon} {message}")


def show_warning(message: str, icon: str = "⚠️"):
    """Display a warning message"""
    st.warning(f"{icon} {message}")


def show_info(message: str, icon: str = "ℹ️"):
    """Display an info message"""
    st.info(f"{icon} {message}")


def create_card(title: str, content: str, icon: Optional[str] = None):
    """Create a styled card component"""
    card_html = f"""
    <div style="
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    ">
        <h3 style="margin: 0 0 0.5rem 0; color: #333;">
            {icon + ' ' if icon else ''}{title}
        </h3>
        <p style="margin: 0; color: #666;">{content}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def create_metric_card(label: str, value: str, delta: Optional[str] = None,
                       delta_color: str = "normal"):
    """Create a metric card with optional delta"""
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def create_expandable_section(title: str, content: Any, expanded: bool = False):
    """Create an expandable section"""
    with st.expander(title, expanded=expanded):
        if callable(content):
            content()
        else:
            st.write(content)


def create_tabs(tab_names: list):
    """Create tabs and return tab objects"""
    return st.tabs(tab_names)


def render_message(message: dict, is_user: bool = False):
    """Render a chat message with proper styling"""
    avatar = "👤" if is_user else "🤖"
    role = "user" if is_user else "assistant"

    with st.chat_message(role, avatar=avatar):
        st.markdown(message.get("content", ""))

        # Show sources if available
        if not is_user and message.get("sources"):
            with st.expander("📚 Sources & Citations"):
                for idx, source in enumerate(message["sources"], 1):
                    st.markdown(f"**{idx}. {source.get('title', 'Untitled')}**")
                    st.caption(source.get('excerpt', ''))
                    if source.get('page'):
                        st.caption(f"Page: {source['page']}")
                    st.divider()


def create_file_uploader(
    label: str,
    accepted_types: list,
    max_size_mb: int = 10,
    help_text: Optional[str] = None,
    key: Optional[str] = None
):
    """Create a file uploader with validation"""
    uploaded_file = st.file_uploader(
        label,
        type=accepted_types,
        help=help_text or f"Max size: {max_size_mb}MB. Accepted: {', '.join(accepted_types)}",
        key=key
    )

    if uploaded_file:
        # Check file size
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            show_error(f"File too large ({file_size_mb:.2f}MB). Maximum size: {max_size_mb}MB")
            return None

    return uploaded_file


def create_search_bar(placeholder: str = "Search...", key: Optional[str] = None):
    """Create a styled search bar"""
    return st.text_input(
        "Search",
        placeholder=placeholder,
        label_visibility="collapsed",
        key=key
    )


def create_filter_sidebar(filters: dict):
    """Create a sidebar with filters"""
    selected_filters = {}

    with st.sidebar:
        st.header("🔍 Filters")

        for filter_name, filter_config in filters.items():
            if filter_config["type"] == "multiselect":
                selected_filters[filter_name] = st.multiselect(
                    filter_config["label"],
                    filter_config["options"],
                    default=filter_config.get("default", [])
                )
            elif filter_config["type"] == "select":
                selected_filters[filter_name] = st.selectbox(
                    filter_config["label"],
                    filter_config["options"],
                    index=filter_config.get("default", 0)
                )
            elif filter_config["type"] == "slider":
                selected_filters[filter_name] = st.slider(
                    filter_config["label"],
                    min_value=filter_config["min"],
                    max_value=filter_config["max"],
                    value=filter_config.get("default", filter_config["min"])
                )
            elif filter_config["type"] == "date":
                selected_filters[filter_name] = st.date_input(
                    filter_config["label"]
                )

    return selected_filters


def show_progress_bar(progress: float, text: str = ""):
    """Show a progress bar"""
    return st.progress(progress, text=text)


def create_button_group(buttons: list, key_prefix: str = "btn"):
    """Create a group of buttons in columns"""
    cols = st.columns(len(buttons))
    results = {}

    for idx, (col, button) in enumerate(zip(cols, buttons)):
        with col:
            results[button["name"]] = st.button(
                button["label"],
                key=f"{key_prefix}_{idx}",
                type=button.get("type", "secondary"),
                use_container_width=True
            )

    return results


def render_table(data, columns: Optional[list] = None):
    """Render a styled dataframe table"""
    if columns:
        data = data[columns]

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True
    )


def create_download_button(
    data: Any,
    filename: str,
    label: str = "Download",
    mime: str = "text/csv",
    key: Optional[str] = None
):
    """Create a download button"""
    return st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime,
        key=key
    )


def show_empty_state(
    title: str,
    message: str,
    icon: str = "📭",
    action_label: Optional[str] = None,
    action_callback: Optional[Callable] = None
):
    """Show an empty state with optional action"""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 3rem 1rem; color: #666;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
            <h3 style="color: #333; margin-bottom: 0.5rem;">{title}</h3>
            <p>{message}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(action_label, use_container_width=True):
                action_callback()


class LoadingState:
    """Context manager for loading states"""

    def __init__(self, message: str = "Processing..."):
        self.message = message
        self.spinner = None

    def __enter__(self):
        self.spinner = st.spinner(self.message)
        self.spinner.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.spinner:
            self.spinner.__exit__(exc_type, exc_val, exc_tb)


def simulate_streaming_response(text: str, delay: float = 0.03):
    """Simulate streaming response for better UX"""
    placeholder = st.empty()
    displayed_text = ""

    for char in text:
        displayed_text += char
        placeholder.markdown(displayed_text)
        time.sleep(delay)

    return displayed_text
