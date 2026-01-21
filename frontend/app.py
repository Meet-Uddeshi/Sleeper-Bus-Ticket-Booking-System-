import sys
import os

# --- Path Setup ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

import streamlit as st
import requests
import datetime
import pandas as pd
from common.config import settings
from common.logger import logger

# --- Configuration ---
BOOKING_API_URL = settings.BOOKING_API_URL
PREDICTION_API_URL = settings.PREDICTION_API_URL

st.set_page_config(page_title="Sleeper Bus Booking", layout="wide")

# --- Session State ---
if 'selected_seats' not in st.session_state:
    st.session_state.selected_seats = set()
if 'selected_seat_details' not in st.session_state:
    st.session_state.selected_seat_details = []

# --- API Helper Functions ---
def get_stations():
    try:
        return requests.get(f"{BOOKING_API_URL}/stations").json()
    except:
        return []

def get_meals():
    try:
        return requests.get(f"{BOOKING_API_URL}/meals").json()
    except:
        return []

def get_available_seats(from_id, to_id, date_str):
    try:
        params = {"from_station": from_id, "to_station": to_id, "travel_date": date_str}
        res = requests.get(f"{BOOKING_API_URL}/seats", params=params)
        return res.json() if res.status_code == 200 else []
    except:
        return []

def create_booking(payload):
    try:
        return requests.post(f"{BOOKING_API_URL}/book", json=payload)
    except Exception as e:
        return None

def get_my_bookings():
    try:
        res = requests.get(f"{BOOKING_API_URL}/bookings")
        return res.json() if res.status_code == 200 else []
    except:
        return []

# --- ADDED: Prediction Helper Function ---
def get_prediction(date_obj, start_order, end_order):
    try:
        payload = {
            "travel_date": date_obj.isoformat(),
            "start_station_order": start_order,
            "end_station_order": end_order
        }
        # Note: Prediction service runs on port 8001
        response = requests.post(f"{PREDICTION_API_URL}/predict", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"confirmation_probability": 0, "demand_level": "Unknown"}
    except Exception as e:
        return {"confirmation_probability": 0, "demand_level": f"Error"}

def toggle_seat(seat_id, seat_number, deck_type, max_seats):
    """
    Handles seat selection with a limit based on passenger count.
    """
    current_count = len(st.session_state.selected_seats)
    
    # Logic: Unselect if already selected
    if seat_id in st.session_state.selected_seats:
        st.session_state.selected_seats.remove(seat_id)
        st.session_state.selected_seat_details = [
            s for s in st.session_state.selected_seat_details if s['id'] != seat_id
        ]
    
    # Logic: Select (Only if limit not reached)
    else:
        if current_count >= max_seats:
            st.toast(f"⚠️ You can only select {max_seats} seats.", icon="🛑")
        else:
            st.session_state.selected_seats.add(seat_id)
            st.session_state.selected_seat_details.append({
                "id": seat_id,
                "number": seat_number,
                "deck": deck_type
            })

# --- Sidebar ---
st.sidebar.title("🚌 Sleeper Bus")
page = st.sidebar.radio("Menu", ["Search & Book", "My Bookings"])

# --- PAGE 1: SEARCH & BOOK ---
if page == "Search & Book":
    st.title("Plan Your Journey")
    
    # 1. Input Section
    c1, c2, c3, c4 = st.columns(4)
    stations = get_stations()
    station_map = {s['name']: s for s in stations}
    
    if not stations:
        st.error("Backend offline. Cannot fetch stations.")
        st.stop()
        
    with c1:
        from_st = st.selectbox("From", list(station_map.keys()), index=0)
    with c2:
        to_st = st.selectbox("To", list(station_map.keys()), index=len(stations)-1)
    with c3:
        t_date = st.date_input("Date", datetime.date.today())
    with c4:
        # ASK USER FOR PASSENGER COUNT FIRST
        num_passengers = st.number_input("Passengers", min_value=1, max_value=6, value=1)

    # Route Validation
    start_node = station_map[from_st]
    end_node = station_map[to_st]
    
    if start_node['sequence_order'] >= end_node['sequence_order']:
        st.error("❌ Invalid Route.")
    else:
        # 2. Availability Check
        if st.button("Check Availability"):
            # Fetch real data
            seats = get_available_seats(start_node['id'], end_node['id'], t_date.isoformat())
            st.session_state.cached_available_seats = seats # Cache for UI stability
            st.session_state.search_performed = True
            
            # Reset selection on new search
            st.session_state.selected_seats = set()
            st.session_state.selected_seat_details = []

        # Logic: Only show grid if search was performed
        if st.session_state.get('search_performed'):
            
            # --- ADDED: PREDICTION DISPLAY ---
            st.divider()
            st.subheader("📊 Demand Forecast")
            
            # Call Prediction API
            pred = get_prediction(t_date, start_node['sequence_order'], end_node['sequence_order'])
            
            p1, p2 = st.columns(2)
            p1.metric("Booking Probability", f"{pred['confirmation_probability']}%")
            p2.metric("Demand Level", pred['demand_level'])
            
            if pred['demand_level'] == "High":
                st.warning("🔥 High Demand! Book fast.")
            elif pred['demand_level'] == "Medium":
                st.info("⚠️ Moderate demand.")
            else:
                st.success("✅ Good availability.")
            # ---------------------------------

            available_seats = st.session_state.cached_available_seats
            available_count = len(available_seats)
            
            st.divider()
            
            # --- CRITICAL CHECK: Do we have enough seats? ---
            if available_count < num_passengers:
                st.error(f"❌ Not enough seats! You requested {num_passengers}, but only {available_count} are available.")
            else:
                st.markdown(f"### 💺 Select Seats ({len(st.session_state.selected_seats)}/{num_passengers})")
                
                # --- 3. Seat Grid ---
                # Map available seats for lookup
                avail_map = {s['seat_number']: s['id'] for s in available_seats}
                
                col_lower, col_upper = st.columns(2)
                
                # Lower Deck Render
                with col_lower:
                    st.markdown("#### Lower Deck")
                    cols = st.columns(5)
                    for i in range(1, 11):
                        seat_num = f"L{i}"
                        s_id = avail_map.get(seat_num)
                        
                        with cols[(i-1)%5]:
                            if s_id:
                                is_sel = s_id in st.session_state.selected_seats
                                label = "✅" if is_sel else "🟩"
                                type_ = "primary" if is_sel else "secondary"
                                if st.button(f"{label} {seat_num}", key=seat_num, type=type_):
                                    toggle_seat(s_id, seat_num, "Lower", num_passengers)
                                    st.rerun()
                            else:
                                st.button(f"🟥 {seat_num}", disabled=True, key=seat_num)

                # Upper Deck Render
                with col_upper:
                    st.markdown("#### Upper Deck")
                    cols = st.columns(5)
                    for i in range(1, 11):
                        seat_num = f"U{i}"
                        s_id = avail_map.get(seat_num)
                        
                        with cols[(i-1)%5]:
                            if s_id:
                                is_sel = s_id in st.session_state.selected_seats
                                label = "✅" if is_sel else "🟩"
                                type_ = "primary" if is_sel else "secondary"
                                if st.button(f"{label} {seat_num}", key=seat_num, type=type_):
                                    toggle_seat(s_id, seat_num, "Upper", num_passengers)
                                    st.rerun()
                            else:
                                st.button(f"🟥 {seat_num}", disabled=True, key=seat_num)

                # --- 4. Checkout Section ---
                selected_count = len(st.session_state.selected_seats)
                
                if selected_count > 0:
                    st.divider()
                    st.subheader("📝 Passenger Details")
                    
                    if selected_count != num_passengers:
                        st.warning(f"⚠️ You requested {num_passengers} passengers but selected {selected_count} seats. Please select {num_passengers - selected_count} more.")
                    else:
                        # Fetch Meals Once
                        meals_list = get_meals()
                        meal_opts = {f"{m['name']} (${m['price']})": m['id'] for m in meals_list}
                        
                        with st.form("checkout"):
                            passengers = []
                            for idx, seat in enumerate(st.session_state.selected_seat_details):
                                st.markdown(f"**Passenger {idx+1} - Seat {seat['number']}**")
                                c1, c2, c3 = st.columns([2,1,2])
                                name = c1.text_input(f"Name", key=f"n{seat['id']}")
                                age = c2.number_input(f"Age", min_value=5, max_value=100, key=f"a{seat['id']}")
                                # Optional Meals
                                meals = c3.multiselect(f"Meals (Optional)", options=list(meal_opts.keys()), key=f"m{seat['id']}")
                                
                                passengers.append({
                                    "seat_id": seat['id'],
                                    "name": name,
                                    "meal_ids": [meal_opts[m] for m in meals]
                                })
                                st.divider()
                            
                            if st.form_submit_button("Confirm Booking"):
                                success = 0
                                bar = st.progress(0)
                                for i, p in enumerate(passengers):
                                    if not p['name']:
                                        st.error(f"Name required for Passenger {i+1}")
                                        continue
                                        
                                    payload = {
                                        "seat_id": p['seat_id'],
                                        "start_station_id": start_node['id'],
                                        "end_station_id": end_node['id'],
                                        "travel_date": t_date.isoformat(),
                                        "passenger_name": p['name'],
                                        "meal_ids": p['meal_ids']
                                    }
                                    res = create_booking(payload)
                                    if res and res.status_code == 200:
                                        success += 1
                                    bar.progress((i+1)/len(passengers))
                                
                                if success == len(passengers):
                                    st.balloons()
                                    st.success("🎉 Booking Successful!")
                                    st.session_state.selected_seats = set()
                                    st.session_state.search_performed = False
                                    st.rerun()

# --- PAGE 2: MY BOOKINGS ---
elif page == "My Bookings":
    st.title("My Bookings")
    data = get_my_bookings()
    
    if not data:
        st.info("No bookings found.")
    else:
        # Create a nice dataframe
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)