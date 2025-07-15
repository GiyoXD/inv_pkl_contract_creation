import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_js_eval import streamlit_js_eval

# --- PAGE CONFIGURATION & HEADER ---
# Set the title that will appear in the browser tab and the sidebar.
st.set_page_config(page_title="Pallet Calculator", layout="centered")

# --- CUSTOM CSS FOR STICKY HEADER ---
st.markdown("""
<style>
    /* This class makes the summary section float */
    .sticky-header {
        position: sticky;
        top: 3.5rem; /* Height of Streamlit's default header (56px) */
        background-color: #ffffff;
        border: 1px solid #e6e6e6; /* Replicates the border from st.container */
        border-radius: 0.5rem; /* Replicates the border-radius */
        z-index: 1000;
        padding: 1rem 1rem 0.5rem 1rem;
        margin-bottom: 1rem;
    }
    /* Custom metric card styling to replicate st.metric */
    .custom-metric {
        color: #31333F;
        padding: 0.5rem;
    }
    .custom-metric-label {
        font-size: 0.875rem;
        margin-bottom: 0.25rem;
    }
    .custom-metric-value {
        font-size: 1.5rem;
        font-weight: 600;
    }
    /* Custom status message styling */
    .status-message {
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 600;
    }
    .status-success { background-color: #d4edda; color: #155724; }
    .status-warning { background-color: #fff3cd; color: #856404; }
    .status-error   { background-color: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)


st.title("Pallet Weight Calculator")
st.markdown("Enter your pallet weights for real-time suggestions. The app will auto-update.")

# --- CONDITIONAL AUTO-REFRESH ---
# This is the core of the intelligent refresh logic.
active_element_tag = streamlit_js_eval(js_expressions='document.activeElement.tagName', key='get_active_element')

if active_element_tag != "INPUT":
    # When no input box is selected, refresh every second (1000 ms).
    st_autorefresh(interval=1000, limit=None, key="auto_refresh_calculator")
    st.caption("Status: Auto-refreshing...")
else:
    # When an input box is selected, show a message that refresh is paused.
    st.caption("Status: Paused while typing...")


# --- INITIALIZE SESSION STATE ---
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
current_list_size = len(st.session_state.pallet_weights)
if pallet_count != current_list_size:
    if pallet_count > current_list_size:
        st.session_state.pallet_weights.extend([None] * (pallet_count - current_list_size))
    else:
        st.session_state.pallet_weights = st.session_state.pallet_weights[:pallet_count]


# --- CALCULATIONS ---
weights = [w if w is not None else 0 for w in st.session_state.pallet_weights]
current_total_weight = sum(weights)
pallets_with_weight = sum(1 for w in st.session_state.pallet_weights if w is not None and w > 0)
remaining_weight = max_weight - current_total_weight
remaining_pallets = pallet_count - pallets_with_weight
suggested_weight = remaining_weight / remaining_pallets if remaining_pallets > 0 else 0.0
ideal_average = max_weight / pallet_count if pallet_count > 0 else 0.0

# --- BUILD HTML FOR STICKY SUMMARY ---
# Status Message Logic
if current_total_weight > max_weight:
    status_class = "status-error"
    status_text = f"🚨 DANGER: You are {current_total_weight - max_weight:,.0f} KG OVER the limit!"
elif current_total_weight > max_weight * 0.95:
    status_class = "status-warning"
    status_text = f"⚠️ WARNING: Approaching maximum weight limit."
else:
    status_class = "status-success"
    status_text = f"✅ LOOKING GOOD: You are within the weight limit."

# Construct the entire HTML block for the summary
summary_html = f"""
<div class="sticky-header">
    <h3 style="margin-bottom: 1rem;">Live Summary</h3>
    <div class="status-message {status_class}">
        {status_text}
    </div>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem;">
        <div class="custom-metric">
            <div class="custom-metric-label">Total Loaded (KG)</div>
            <div class="custom-metric-value">{current_total_weight:,.0f}</div>
        </div>
        <div class="custom-metric">
            <div class="custom-metric-label">Remaining (KG)</div>
            <div class="custom-metric-value">{remaining_weight:,.0f}</div>
        </div>
        <div class="custom-metric">
            <div class="custom-metric-label">Ideal Avg. (KG)</div>
            <div class="custom-metric-value">{ideal_average:,.0f}</div>
        </div>
        <div class="custom-metric">
            <div class="custom-metric-label">Suggested Next (KG)</div>
            <div class="custom-metric-value">{suggested_weight:,.0f}</div>
        </div>
    </div>
</div>
"""
st.markdown(summary_html, unsafe_allow_html=True)


# --- PALLET INPUTS ---
with st.container(border=True):
    st.subheader("Pallet Weights (KG)")
    
    cols = st.columns(3)
    for i in range(pallet_count):
        with cols[i % 3]:
            st.session_state.pallet_weights[i] = st.number_input(
                f"Pallet {i + 1}", 
                key=f"pallet_{i}", 
                min_value=0,
                value=st.session_state.pallet_weights[i],
                step=50,
                placeholder="Empty"
            )
    
    st.markdown("---")
    if st.button("Reset All Weights", use_container_width=True):
        st.session_state.pallet_weights = [None] * pallet_count
        st.rerun()
