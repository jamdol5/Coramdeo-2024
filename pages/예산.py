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

def revenue_page():
    st.title("예산 관리")
    
    revenues = data_manager.get_revenues()
    
    # Add new revenue
    st.subheader("새로운 예산 추가")
    with st.form("예산 추가"):
        date = st.date_input("날짜")
        description = st.text_input("설명")
        amount = st.number_input("금액", min_value=0.01, step=0.01)
        submitted = st.form_submit_button("예산 추가")
        
        if submitted:
            new_revenue = {
                "date": date.isoformat(),
                "description": description,
                "amount": amount
            }
            data_manager.add_revenue(new_revenue)
            st.success("예산 추가 성공!")
            st.rerun()
    
    # Display and manage existing revenues
    st.subheader("기존 예산")
    df_revenue = pd.DataFrame(revenues)
    
    if not df_revenue.empty and 'date' in df_revenue.columns:
        df_revenue['date'] = pd.to_datetime(df_revenue['date'],errors='coerce')
        df_revenue = df_revenue.sort_values('date', ascending=False)
        
        for idx, row in df_revenue.iterrows():
            year = row['date'].year

            col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
            col1.write(row['date'].strftime('%Y-%m-%d') if pd.notnull(row['date']) else 'No Date')
            col2.write(row['description'])
            col3.write(f"${row['amount']:.2f}")
            if col4.button("삭제", key=f"del_rev_{idx}"):
                data_manager.remove_revenue(year,idx)
                st.success("예산 삭제 성공!")
                st.rerun()
    else:
        st.write("아직 예산이 없습니다.")

if __name__ == "__main__":
    revenue_page()
