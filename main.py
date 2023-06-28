import os
from datetime import datetime

import pandas as pd
import streamlit as st

from common import DayOfWeek
from scheduler import create_schedule, update_schedule


def on_load_google_sheets():
    url = st.session_state.google_sheets_url
    csv_url = url.replace("/edit#gid=", "/export?format=csv&gid=")
    habits_df = pd.read_csv(csv_url)
    st.session_state.habits_df = habits_df


def on_generate_schedule():
    st.session_state.todo_list = create_schedule(
        st.session_state.habits_df, DayOfWeek[st.session_state.day_of_week.upper()]
    )


def on_update_schedule():
    question = st.session_state.schedule_question
    st.session_state.todo_list = update_schedule(st.session_state.todo_list, question)


st.set_page_config(
    page_title="Mastery List GPT",
    page_icon="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/2611.png",
)


st.markdown(
    "<h1 style='text-align: center'>Mastery List GPT</h1>",
    unsafe_allow_html=True,
)

if not "api_key" in st.session_state:
    st.session_state.api_key = ""
    st.session_state.google_sheets_url = ""
    st.session_state.habits_df = None
    st.session_state.todo_list = []


os.environ["OPENAI_API_KEY"] = st.session_state.api_key


with st.sidebar:
    st.text_input(
        "OpenAI API Key",
        type="password",
        key="api_key",
        placeholder="sk-...4242",
        help="Get your API key: https://platform.openai.com/account/api-keys",
    )
    st.text_input(
        "Google Sheets URL",
        key="google_sheets_url",
        placeholder="https://docs.google.com/spreadsheets/d/xxxxxxx/edit#gid=0",
        on_change=on_load_google_sheets,
        help="Example Sheet: https://docs.google.com/spreadsheets/d/1RpM7U9FNEFzXzY6S0qtb9Upla0QYSWZRCY1jpCO8PfI/edit?usp=sharing",
    )

    if st.session_state.habits_df is not None:
        st.dataframe(st.session_state.habits_df)
    if st.session_state.habits_df is not None and st.session_state.api_key != "":
        st.selectbox(
            "Day of the week for your schedule",
            [e.value for e in DayOfWeek],
            index=datetime.now().weekday(),
            key="day_of_week",
            on_change=on_generate_schedule,
        )

        st.button("Generate Schedule", on_click=on_generate_schedule, type="primary")


if st.session_state.todo_list:
    st.subheader(f"{st.session_state.day_of_week} Schedule")

    for i, todo in enumerate(st.session_state.todo_list):
        st.checkbox(str(todo), key=f"todo_{i}")

    st.chat_input(
        "Change your Schedule",
        key="schedule_question",
        on_submit=on_update_schedule,
    )
else:
    st.info("Your schedule is empty. Generate a schedule to get started.")
