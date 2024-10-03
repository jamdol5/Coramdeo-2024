import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
import json

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] == st.secrets["credentials"]["username"]
            and st.session_state["password"] == st.secrets["credentials"]["password"]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct
        return True

# Fetch the data from Streamlit secrets
data = json.loads(st.secrets["accounting_data"]["data"])

# Initialize the DataManager with the fetched data
data_manager = DataManager(data)

def costs_page():
    st.title('지출 관리')

    costs = data_manager.get_costs()
    st.subheader("이벤트 관리")
    
    # Get all unique years and events
    years = sorted(costs.keys())
    all_events = set()
    for year_events in costs.values():
        all_events.update(year_events.keys())
    all_events = sorted(all_events)

    col1, col2 = st.columns(2)
    
    with col1:
        new_event = st.text_input("새로운 이벤트 이름")
        year = st.number_input("Year", min_value=2000, max_value=2100, step=1, value=2023)

        if st.button("이벤트 추가"):
            if new_event and new_event not in all_events:
                data_manager.add_event(new_event, year)
                st.success(f"이벤트 '{new_event}' 추가 성공!")
                st.rerun()
            else:
                st.error("이벤트 이름이 유효하지 않거나 이미 존재합니다.")
    
    with col2:    
        if years:
            selected_year = st.selectbox("이벤트 삭제할 연도 선택", years)
            events_in_year = list(costs.get(selected_year, {}).keys())

            if events_in_year:
                event_to_remove = st.selectbox("이벤트 삭제할 이벤트 선택", events_in_year)
                if st.button("이벤트 삭제"):
                    data_manager.remove_event(event_to_remove, selected_year)
                    st.success(f"이벤트 '{event_to_remove}' 삭제 성공!")
                    st.rerun()
            else:
                st.write("삭제할 이벤트가 없습니다.")
        else:
            st.write("이벤트가 없습니다.")

    # Add new cost
    st.subheader("새로운 지출 추가")

    if years:
        with st.form(key="add_cost_form"):
            selected_year = st.selectbox("연도 선택", years, key="cost_year_select")
            events_in_year = list(costs.get(selected_year, {}).keys())
            event = st.selectbox("이벤트 선택", events_in_year, key="cost_event_select")
            subcategory = st.selectbox("하위 카테고리 선택", data_manager.subcategories)

            date = st.date_input("날짜")
            description = st.text_input("설명")
            amount = st.number_input("금액", min_value=0.01, step=0.01)

            submit_button = st.form_submit_button(label="지출 추가")

        if submit_button:
            if event:
                new_cost = {
                    "date": date.isoformat(),
                    "description": description,
                    "amount": amount
                }
                data_manager.add_cost(event, subcategory, new_cost)
                st.success("지출 추가 성공!")
                st.rerun()
            else:
                st.error("이벤트를 선택하세요.")
    else:
        st.write("이벤트가 없습니다. 먼저 이벤트를 추가하세요.")
    
    # Display and manage existing costs
    st.subheader("기존 지출")
    for year, events in costs.items():
        st.write(f"### {year}년 지출")

        for event, subcategories in events.items():
            st.write(f"#### {event}")
            
            if isinstance(subcategories, dict):
                for subcategory, subcategory_costs in subcategories.items():
                    st.write(f"##### {subcategory}")
                    df_costs = pd.DataFrame(subcategory_costs)
                
                    if not df_costs.empty:
                        df_costs['date'] = pd.to_datetime(df_costs['date'])
                        df_costs = df_costs.sort_values('date', ascending=False)
                
                        for idx, row in df_costs.iterrows():
                            col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
                            col1.write(row['date'].strftime('%Y-%m-%d'))
                            col2.write(row['description'])
                            col3.write(f"${row['amount']:.2f}")
                            
                            year = row['date'].year

                            if col4.button("Delete", key=f"del_cost_{event}_{subcategory}_{year}_{idx}"):
                                data_manager.remove_cost(year, event, subcategory, idx)
                                st.success("지출 삭제 성공!")
                                st.rerun()
                    else:
                        st.write("이 카테고리에 대한 지출이 없습니다.")
            else:
                st.write("이 이벤트에 대한 지출 정보가 올바르지 않습니다.")

if __name__ == "__main__":
    costs_page()

