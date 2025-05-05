from pathlib import Path

import streamlit as st
from streamlit import session_state as state
from rdagent.log.ui import conf

# 设置主日志路径
if "log_folder" not in state:
    state.log_folder = Path("./log")
if "log_folders" not in state:
    state.log_folders = UI_SETTING.default_log_folders

summary_page = st.page("ds_summary.py", title="Summary", icon="📊")
trace_page = st.page("ds_trace.py", title="Trace", icon="📈")
st.set_page_config(layout="wide", page_title="RD-Agent", page_icon="🎓", initial_sidebar_state="expanded")
st.navigation([summary_page, trace_page]).run()

# UI - Sidebar
with st.sidebar:
    st.subheader("Pages", divider="rainbow")
    st.page_link(summary_page, icon="📊")
    st.page_link(trace_page, icon="📈")

    st.subheader("Settings", divider="rainbow")
    with st.form("log_folder_form", border=False):
        log_folder_str = st.text_area(
            "**Log Folders**(split by ';')", placeholder=state.log_folder, value=";".join(state.log_folders)
        )
        if st.form_submit_button("Confirm", type='primary'):
            state.log_folders = [folder.strip() for folder in log_folder_str.split(";") if folder.strip()]
            st.rerun()
