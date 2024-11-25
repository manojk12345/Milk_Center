import streamlit as st
from db_function import user, farmer, milk_collection, payments
import time
import pandas as pd
import sqlite3
from datetime import datetime


def insert_new_farmer(farmer_name, contact_info):
    conn = sqlite3.connect('milk_collection_data.db')
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO FARMER (farmerName, contactInfo) VALUES (?, ?)", (farmer_name, contact_info))
        conn.commit()
        return "success"
    except:
        return "failure"
    finally:
        conn.close()
        
def insert_new_user(user_name, password):
    conn = sqlite3.connect('milk_collection_data.db')
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO USER (userName, password) VALUES (?, ?)", (user_name, password))
        conn.commit()
        return "success"
    except:
        return "failure"
    finally:
        conn.close()

def insert_milk_data(farmer_name, quantity, reading, price_per_liter, total_amount):
    conn = sqlite3.connect('milk_collection_data.db')
    cur = conn.cursor()
    
    try:
        recorded_by = st.session_state['username']  
        current_time = datetime.now().strftime('%H:%M:%S')

        cur.execute('''
            INSERT INTO MILKCOLLECTION (recordedBy, farmerName, quantity, reading, pricePerLiter, totalAmount, date, time) 
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_DATE,?)
        ''', (recorded_by, farmer_name, quantity, reading, price_per_liter, total_amount,current_time))

        cur.execute('''
            SELECT due FROM PAYMENTS 
            WHERE farmerName = ?
        ''', (farmer_name,))
        result = cur.fetchone()

        if result:
            current_due = result[0]
            new_due = current_due + total_amount  
            
            cur.execute('''
                UPDATE PAYMENTS 
                SET due = ? 
                WHERE farmerName = ?
            ''', (new_due, farmer_name))
        else:
            
            total_balance = total_amount
            settled = 0  
            due = total_balance
            cur.execute('''
                INSERT INTO PAYMENTS (farmerName, totalBalance, setteled, due) 
                VALUES (?, ?, ?, ?)
            ''', (farmer_name, total_balance, settled, due))

        conn.commit()
        conn.close()
        return "success"
    except Exception as e:
        conn.close()
        print(f"Insert error: {str(e)}")  
        return f"failure: {str(e)}"
    
def fetch_monthly_report(year, month, farmer_name):
    conn = sqlite3.connect('milk_collection_data.db')
    query = f'''
        SELECT  f.farmerName, m.date,m.time, m.reading as fatrate, m.quantity, m.totalAmount
        FROM MILKCOLLECTION m
        JOIN FARMER f ON m.farmerName = f.farmerName
        WHERE strftime('%Y', m.date) = ? AND strftime('%m', m.date) = ? AND f.farmerName = ?
        ORDER BY m.totalAmount DESC
    '''
    df = pd.read_sql_query(query, conn, params=(year, month, farmer_name))
    conn.close()
    return df   

def fetch_due_amount(farmer_name):
    conn = sqlite3.connect('milk_collection_data.db')
    cur = conn.cursor()
    cur.execute("SELECT due FROM PAYMENTS WHERE farmerName = ?", (farmer_name,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else None

def settle_payment(farmer_name, pay_amount):
    conn = sqlite3.connect('milk_collection_data.db')
    cur = conn.cursor()
    
    cur.execute("SELECT due, setteled FROM PAYMENTS WHERE farmerName = ?", (farmer_name,))
    result = cur.fetchone()
    
    if result:
        due, setteled = result
        new_due = max(0, due - pay_amount)  
        new_setteled = setteled + pay_amount
        
        cur.execute("UPDATE PAYMENTS SET due = ?, setteled = ? WHERE farmerName = ?", (new_due, new_setteled, farmer_name))
        conn.commit()
        conn.close()
        return "success", new_due
    else:
        conn.close()
        return "failure", None

def home_page():
    # st.title("Milk Collection Center")
    st.markdown("<h1 style='text-align: center;'>Milk Collection Center</h1>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: right;'><b>Logged in as :</b> {st.session_state['username']}</div>", unsafe_allow_html=True)

    slide = st.radio(
        " ", 
        ["Register Farmer", "Farmers List", "Milk Collection", 
            "Milk Collection Data", "Monthly Reports", 
            "Settle Payments", "Logout"], 
        key='slide',horizontal=True
    )
    
    if slide == "Register Farmer":
        with st.form(key='farmer-registration-form',clear_on_submit=True):
            st.write("#### Farmer Registration Form")
            farmer_name = st.text_input("Farmer Name")
            contact_info = st.text_input("Contact Info")
                
            if st.form_submit_button("Submit"):
                conn = sqlite3.connect('milk_collection_data.db')
                cur = conn.cursor()
                cur.execute("SELECT * FROM FARMER WHERE farmerName = ?", (farmer_name,))
                existing_user = cur.fetchone()
                conn.close()
                    
                if existing_user:
                    st.error(f"Farmer with name {farmer_name} already exists. Please use different name.")
                else:
                    status = insert_new_farmer(farmer_name, contact_info)
                    if status == 'success':
                        st.success("Farmer registered successfully!")
                        time.sleep(1)
                        st.rerun() 
                    else:
                        st.error("Failed to register farmer. Please try again.")
    
    elif slide == "Farmers List":
        st.write("#### Farmers List")
        conn = sqlite3.connect('milk_collection_data.db')
        df = pd.read_sql_query("SELECT * FROM FARMER", conn)
        conn.close()
        st.dataframe(df,use_container_width=True, hide_index =True)

    elif slide == "Milk Collection":
        with st.form(key='milk-collection-form',clear_on_submit=True):
            st.write("#### Enter Milk Collection Data")
            conn = sqlite3.connect('milk_collection_data.db')
            cur = conn.cursor()
            
            data = cur.execute(''' SELECT distinct farmerName FROM FARMER ''').fetchall()

            conn.close()
            farmer_name = st.selectbox("Select Farmer Name", [str(i[0]) for i in data])
            quantity = st.number_input("Milk Quantity (in liters)", step=0.1)
            reading = st.number_input("Fat Reading", step=0.1)
            price_per_liter = st.number_input("Price per Liter", step=0.1)
            
            
            if st.form_submit_button("Submit"):
                conn = sqlite3.connect('milk_collection_data.db')
                cur = conn.cursor()
                
                cur.execute('''
                    SELECT * FROM FARMER 
                    WHERE farmerName = ?
                ''', (farmer_name,))
                
                existing_farmer = cur.fetchone()
                
                if not existing_farmer:
                    st.error("Farmer does not exist. Please register the farmer first.")
                    conn.close()
            
                else:
                    current_time = datetime.now()
                    current_date = current_time.date()
                    current_hour = current_time.hour
                    
                    if current_hour < 12:
                        delivery_type = 'morning'
                        time_condition = "CAST(strftime('%H', time) AS INTEGER) < 12"
                    else:
                        delivery_type = 'evening'
                        time_condition = "CAST(strftime('%H', time) AS INTEGER) >= 12"
                        
                    cur.execute(f'''
                        SELECT * FROM MILKCOLLECTION 
                        WHERE farmerName = ? 
                        AND date = ? 
                        AND {time_condition}
                    ''', (farmer_name, current_date))

                    existing_entry = cur.fetchone()

                    if existing_entry:
                        conn.close()
                        st.error(f"You have already delivered milk in the {delivery_type}.")
                    else:
                        total_amount = round(quantity * reading * (price_per_liter / 10), 2)

                        status = insert_milk_data(farmer_name, quantity, reading, price_per_liter, total_amount)
                        if status == 'success':
                            st.success(f"Milk collection data added successfully for the {delivery_type}!")
                            time.sleep(2)
                            st.rerun() 
                        else:
                            st.error(f"Record already exists for {delivery_type}")
                            
    elif slide == "Milk Collection Data":
        st.write("#### Milk collection Data")
        
        conn = sqlite3.connect('milk_collection_data.db')
        df = pd.read_sql_query("SELECT * FROM MILKCOLLECTION", conn)
        df = df.sort_values(by='date', ascending=False)
        conn.close()
        
        st.dataframe(df,use_container_width=True, hide_index =True)
    
    elif slide == "Monthly Reports":
        st.write("#### Monthly Report")
        
        conn = sqlite3.connect('milk_collection_data.db')
        cur = conn.cursor()
        data = cur.execute("SELECT distinct farmerName FROM FARMER").fetchall()
        conn.close()
        
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        year_options = [str(y) for y in range(2020, current_year + 1)]
        month_options = [str(m).zfill(2) for m in range(1, 13)]
        
        year = st.selectbox("Select Year", year_options, index=year_options.index(str(current_year)))
        month = st.selectbox("Select Month", month_options, index=month_options.index(str(current_month).zfill(2)))
        farmer_name = st.selectbox("Select Farmer Name", [str(i[0]) for i in data])

        df = fetch_monthly_report(year, month, farmer_name)

        if df.empty:
            st.write(f"No data found for {year}-{month}. Farmer ID: {farmer_name}")
        else:                
            st.dataframe(df,use_container_width=True, hide_index =True)
            st.write(f"Total : {round(df['totalAmount'].sum(),2)}")
    
    elif slide == "Settle Payments":
        st.write("#### Settle Payments")

        conn = sqlite3.connect('milk_collection_data.db')
        cur = conn.cursor()
        data = cur.execute("SELECT distinct farmerName FROM FARMER").fetchall()
        conn.close()
        
        farmer_name = st.selectbox("Select Farmer Name", [str(i[0]) for i in data])
        pay_amount = st.number_input("Enter Payment Amount:", step=0.01, min_value=0.01)

        if farmer_name:
            due_amount = fetch_due_amount(farmer_name)
            if due_amount is not None:
                st.write(f"Current Due Amount: ₹{round(due_amount,2)}")
            else:
                st.warning("No due amount found for the given Farmer")

        if st.button("Settle Payment"):
            if farmer_name and pay_amount > 0:
                status, new_due = settle_payment(farmer_name, pay_amount)
                if status == "success":
                    st.success(f"Payment settled! New due amount: ₹{new_due}")
                    time.sleep(1)
                    st.rerun()  
                else:
                    st.error("Failed to settle payment. Please try again.")
            else:
                st.warning("Please enter a valid Farmer ID and Payment Amount.")
                
        conn = sqlite3.connect('milk_collection_data.db')
        df = pd.read_sql_query("SELECT farmerName,totalBalance,setteled,due FROM PAYMENTS", conn)
        st.dataframe(df,use_container_width=True, hide_index =True)
    
    elif slide == "Logout":
        st.session_state.clear()
        st.write("Logged out successfully.")
        st.session_state.logged_in = False
        st.rerun()
        

def main():
    user()
    farmer()
    milk_collection()
    payments()
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if st.session_state.logged_in:
        home_page()
    else:
        col1, col2 = st.columns([1, 0.1])  
        with col1:
            page = st.radio("  ", ["Login", "Registration"], key='page', horizontal=True)

        if page == 'Login':
            with st.form(key='login-form',clear_on_submit=True):
                user_name = st.text_input('User Name')
                password = st.text_input('Password', type='password')
                
                if st.form_submit_button("Login"):
                    conn = sqlite3.connect('milk_collection_data.db')
                    cur = conn.cursor()
                    data = cur.execute("SELECT * FROM USER WHERE userName = ? AND password = ?", (user_name, password)).fetchone()
                    conn.close()
                    
                    if data:
                        st.session_state.logged_in = True
                        st.session_state['username'] = user_name
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Incorrect username or password.")
        
        elif page == 'Registration':
            with st.form(key='registration-form',clear_on_submit=True):
                user_name = st.text_input('User Name')
                password = st.text_input('Password', type='password')
                
                if st.form_submit_button("Register"):
                    conn = sqlite3.connect('milk_collection_data.db')
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM USER WHERE userName = ?", (user_name,))
                    existing_user = cur.fetchone()
                    conn.close()
                    
                    if existing_user:
                        st.error("Username already exists. Please choose a different username.")
                    else:
                        status = insert_new_user(user_name, password)
                        if status == 'success':
                            st.success("Registered successfully!")
                            st.stop()
                        else:
                            st.error("Failed to register. Please try again.")
                

# Run the app
if __name__ == '__main__':
    main()
    
    
    
    









