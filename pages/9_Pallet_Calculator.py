import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_js_eval import streamlit_js_eval

# --- PAGE CONFIGURATION & HEADER ---
# Set the title that will appear in the browser tab and the sidebar.
st.set_page_config(page_title="Pallet Calculator", layout="centered")

st.title("Pallet Weight Calculator")
st.markdown("Enter your pallet weights for real-time suggestions. The app will auto-update.")

# --- CONDITIONAL AUTO-REFRESH ---
# This is the core of the intelligent refresh logic.
# 1. We ask the browser what element is currently active (in focus).
# 2. If it's NOT an "INPUT" element, we enable the auto-refresh.
# 3. If it IS an "INPUT" element (meaning you're typing), we disable auto-refresh.
active_element_tag = streamlit_js_eval(js_expressions='document.activeElement.tagName', key='get_active_element')

if active_element_tag != "INPUT":
    # When no input box is selected, refresh every second (1000 ms).
    st_autorefresh(interval=1000, limit=None, key="auto_refresh_calculator")
    st.caption("Status: Auto-refreshing...")
else:
    # When an input box is selected, show a message that refresh is paused.
    st.caption("Status: Paused while typing...")


# --- INITIALIZE SESSION STATE ---
# Session state is used to store the weights of the pallets so they persist
# across reruns when the user interacts with the app.
# We use None to represent an empty input field.
if 'pallet_weights' not in st.session_state:
    st.session_state.pallet_weights = [None] * 12 # Default to 12 pallets

# --- SETTINGS ---
with st.container(border=True):
    st.subheader("Configuration")
    col1, col2 = st.columns(2)

    with col1:
        max_weight = st.number_input(
            "Max Gross Weight (KG)", 
            min_value=0, 
            value=25000, 
            step=1000,
            help="Set the maximum allowable gross weight for the entire shipment."
        )

    with col2:
        pallet_count = st.number_input(
            "Total Number of Pallets", 
            min_value=1, 
            value=12, 
            step=1,
            help="Set the total number of pallets in the shipment."
        )

# --- SYNC PALLET COUNT WITH SESSION STATE ---
# Adjust the list of weights in session_state if the user changes the pallet count.
current_list_size = len(st.session_state.pallet_weights)
if pallet_count != current_list_size:
    # If the user increases the count, add empty (None) slots to the end.
    if pallet_count > current_list_size:
        st.session_state.pallet_weights.extend([None] * (pallet_count - current_list_size))
    # If the user decreases the count, truncate the list.
    else:
        st.session_state.pallet_weights = st.session_state.pallet_weights[:pallet_count]


# --- CALCULATIONS ---
# These calculations are performed on every rerun of the script.
# Replace None with 0 for calculation purposes, but keep None in the state for the UI.
weights = [w if w is not None else 0 for w in st.session_state.pallet_weights]
current_total_weight = sum(weights)
pallets_with_weight = sum(1 for w in st.session_state.pallet_weights if w is not None and w > 0)

remaining_weight = max_weight - current_total_weight
remaining_pallets = pallet_count - pallets_with_weight

# Calculate the suggested weight for the next unloaded pallet.
if remaining_pallets > 0:
    suggested_weight = remaining_weight / remaining_pallets
else:
    suggested_weight = 0.0

# Calculate the ideal average weight across all pallets from the start.
if pallet_count > 0:
    ideal_average = max_weight / pallet_count
else:
    ideal_average = 0.0

# --- LIVE SUMMARY DISPLAY ---
with st.container(border=True):
    st.subheader("Live Summary")

    # Status Message
    if current_total_weight > max_weight:
        st.error(f"🚨 DANGER: You are {current_total_weight - max_weight:,.0f} KG OVER the limit!")
    elif current_total_weight > max_weight * 0.95:
        st.warning(f"⚠️ WARNING: Approaching maximum weight limit.")
    else:
        st.success(f"✅ LOOKING GOOD: You are within the weight limit.")

    # Metric Cards using standard st.metric
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Loaded (KG)", f"{current_total_weight:,.0f}")
    col2.metric("Remaining (KG)", f"{remaining_weight:,.0f}")
    col3.metric("Ideal Avg. (KG)", f"{ideal_average:,.0f}")
    col4.metric("Suggested Next (KG)", f"{suggested_weight:,.0f}")


# --- PALLET INPUTS ---
with st.container(border=True):
    st.subheader("Pallet Weights (KG)")
    
    # Create columns for a cleaner layout on wider screens
    cols = st.columns(3)
    for i in range(pallet_count):
        # Distribute pallet inputs across the columns
        with cols[i % 3]:
            # The key is crucial for Streamlit to identify each widget uniquely.
            # The value is read from and written to our session_state list.
            st.session_state.pallet_weights[i] = st.number_input(
                f"Pallet {i + 1}", 
                key=f"pallet_{i}", 
                min_value=0,
                value=st.session_state.pallet_weights[i], # This can be None, which makes the input empty
                step=50,
                placeholder="Empty" # Show a placeholder for empty inputs
            )
    
    st.markdown("---")
    # Reset Button
    if st.button("Reset All Weights", use_container_width=True):
        # To reset, we re-initialize the list in session_state with Nones.
        st.session_state.pallet_weights = [None] * pallet_count
        st.rerun()
