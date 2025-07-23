import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from pathlib import Path
import math # Import the math library for ceiling function

# --- Page Configuration ---
st.set_page_config(page_title="Invoice Explorer", layout="wide")
st.title("Invoice Data Explorer & Editor 🧭")
st.info("Use the tabs to view summaries, see details, or edit an existing invoice.")

# --- Shared Configuration ---
DATA_ROOT = "data"
DATA_DIRECTORY = os.path.join(DATA_ROOT, 'Invoice Record')
DATABASE_FILE = os.path.join(DATA_DIRECTORY, 'master_invoice_data.db')
TABLE_NAME = 'invoices'
CONTAINER_TABLE_NAME = 'invoice_containers'

# --- Check for Database ---
if not os.path.exists(DATABASE_FILE):
    st.error(f"Database file not found at '{DATABASE_FILE}'. Please add an invoice first.")
    st.stop()

# --- HELPER FUNCTIONS (No changes here) ---

def find_active_invoices(search_mode, search_term):
    with sqlite3.connect(DATABASE_FILE) as conn:
        query = f"SELECT DISTINCT inv_no, inv_ref FROM {TABLE_NAME} WHERE LOWER({search_mode}) LIKE LOWER(?) AND status = 'active' ORDER BY inv_no"
        return [{'inv_no': row[0], 'inv_ref': row[1]} for row in conn.cursor().execute(query, (f'%{search_term}%',)).fetchall()]

def get_invoice_line_items(inv_ref):
    with sqlite3.connect(DATABASE_FILE) as conn:
        return pd.read_sql_query(f"SELECT id, inv_no, inv_date, inv_ref, po, item, description, pcs, sqft, pallet_count, unit, amount, net, gross, cbm, production_order_no, creating_date FROM {TABLE_NAME} WHERE inv_ref = ?", conn, params=(inv_ref,))

def get_invoice_containers(inv_ref):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor(); cursor.execute(f"SELECT container_description FROM {CONTAINER_TABLE_NAME} WHERE inv_ref = ?", (inv_ref,)); return [row[0] for row in cursor.fetchall()]

def update_invoice_data(inv_ref, edited_df, container_list):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor(); cursor.execute("BEGIN TRANSACTION;")
        try:
            cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE inv_ref = ?", (inv_ref,)); cursor.execute(f"DELETE FROM {CONTAINER_TABLE_NAME} WHERE inv_ref = ?", (inv_ref,))
            df_to_save = edited_df.copy(); df_to_save['status'] = 'active'; df_to_save.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
            if container_list:
                container_data = [(inv_ref, desc) for desc in container_list]
                cursor.executemany(f"INSERT INTO {CONTAINER_TABLE_NAME} (inv_ref, container_description) VALUES (?, ?)", container_data)
            cursor.execute("COMMIT;")
        except Exception as e:
            cursor.execute("ROLLBACK;"); raise e

def undo(history_index_key):
    if st.session_state.get(history_index_key, 0) > 0: st.session_state[history_index_key] -= 1

def redo(history_key, history_index_key):
    if st.session_state.get(history_index_key, 0) < len(st.session_state.get(history_key, [])) - 1: st.session_state[history_index_key] += 1

# --- Create Tabs ---
tab1, tab2, tab3 = st.tabs(["Invoice Summary", "Detailed View", "✏️ Edit Invoice"])

# ==============================================================================
# --- TAB 1: Invoice Summary (with Pagination) ---
# ==============================================================================
with tab1:
    st.header("Summarized Invoice View")
    
    # --- State and Reset for Summary Filters ---
    summary_filter_keys = ['summary_ref_filter', 'summary_no_filter', 'summary_container_filter', 'summary_date_range']
    if 'summary_current_page' not in st.session_state:
        st.session_state.summary_current_page = 1
    
    def reset_summary_filters_and_page():
        for key in summary_filter_keys:
            st.session_state[key] = None if key == 'summary_date_range' else ""
        st.session_state.summary_current_page = 1

    with st.expander("🔍 Filters for Summary View", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        f_col1.text_input("Filter by Invoice Ref:", key='summary_ref_filter')
        f_col2.text_input("Filter by Invoice No:", key='summary_no_filter')
        f_col3.text_input("Filter by Container:", key='summary_container_filter')
        today_date_summary = datetime.now().date()
        st.date_input("Filter by Creation Date Range:", value=st.session_state.get('summary_date_range') or (today_date_summary, today_date_summary), key='summary_date_range')
        st.button("Reset Summary Filters", on_click=reset_summary_filters_and_page, use_container_width=True, key="reset_summary")
    
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            query = f"""
                SELECT i.inv_no, i.inv_ref, i.inv_date, MAX(i.status) as status, SUM(CAST(i.sqft AS REAL)) as total_sqft, SUM(CAST(i.amount AS REAL)) as total_amount, SUM(CAST(i.pcs AS INTEGER)) as total_pcs, SUM(CAST(i.net AS REAL)) as total_net, SUM(CAST(i.gross AS REAL)) as total_gross, SUM(CAST(i.cbm AS REAL)) as total_cbm, i.creating_date, (SELECT GROUP_CONCAT(c.container_description, ', ') FROM {CONTAINER_TABLE_NAME} c WHERE c.inv_ref = i.inv_ref) AS containers
                FROM {TABLE_NAME} i
            """; conditions, params = [], []
            if st.session_state.get('summary_ref_filter'): conditions.append("i.inv_ref LIKE ?"); params.append(f"%{st.session_state.summary_ref_filter}%")
            if st.session_state.get('summary_no_filter'): conditions.append("i.inv_no LIKE ?"); params.append(f"%{st.session_state.summary_no_filter}%")
            if st.session_state.get('summary_container_filter'): conditions.append(f"i.inv_ref IN (SELECT c.inv_ref FROM {CONTAINER_TABLE_NAME} c WHERE c.container_description LIKE ?)"); params.append(f"%{st.session_state.summary_container_filter}%")
            if st.session_state.get('summary_date_range') and len(st.session_state.summary_date_range) == 2: start_date, end_date = st.session_state.summary_date_range; start_dt = datetime.combine(start_date, datetime.min.time()).strftime('%Y-%m-%d %H:%M:%S'); end_dt = datetime.combine(end_date, datetime.max.time()).strftime('%Y-%m-%d %H:%M:%S'); conditions.append("i.creating_date BETWEEN ? AND ?"); params.extend([start_dt, end_dt])
            if conditions: query += " WHERE " + " AND ".join(conditions)
            query += " GROUP BY i.inv_no, i.inv_ref, i.inv_date, i.creating_date ORDER BY i.creating_date DESC"
            df_summary = pd.read_sql_query(query, conn, params=params)
    except Exception as e: st.error(f"An error occurred while querying the summary data: {e}"); st.stop()
    
    if df_summary.empty:
        st.warning("No invoices match your current filter criteria.")
    else:
        ITEMS_PER_PAGE = 15
        total_items = len(df_summary)
        total_pages = math.ceil(total_items / ITEMS_PER_PAGE)

        if st.session_state.summary_current_page > total_pages:
            st.session_state.summary_current_page = total_pages if total_pages > 0 else 1

        start_idx = (st.session_state.summary_current_page - 1) * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        paginated_df = df_summary.iloc[start_idx:end_idx]
        
        st.success(f"Found {total_items} matching invoices. Showing page {st.session_state.summary_current_page} of {total_pages}.")
        st.markdown("---")

        for row in paginated_df.itertuples():
            expander_title = f"**Inv No:** {row.inv_no} | **Ref:** {row.inv_ref} | **Date:** {row.inv_date}"
            with st.expander(expander_title):
                st.markdown("##### Invoice Totals")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Amount", f"${row.total_amount:,.2f}"); col2.metric("Total Pcs", f"{row.total_pcs:,.0f}"); col3.metric("Total Sqft", f"{row.total_sqft:,.2f}")
                col4, col5, col6 = st.columns(3)
                col4.metric("Net Weight (KG)", f"{row.total_net:,.2f}"); col5.metric("Gross Weight (KG)", f"{row.total_gross:,.2f}"); col6.metric("Total CBM", f"{row.total_cbm:,.3f}")
                st.markdown("**Containers / Trucks:**"); st.info(row.containers if row.containers else "N/A")
                st.markdown("---")
                if st.button("✏️ Edit This Invoice", key=f"edit_btn_{row.inv_ref}", use_container_width=True):
                    st.session_state.edit_search_term = row.inv_ref
                    st.session_state.edit_search_mode = "Invoice Reference"
                    st.session_state.just_switched_to_edit = True
                    st.rerun()

        st.markdown("---")
        p_col1, p_col2, p_col3 = st.columns([1.5, 1, 1.5])
        if p_col1.button("⬅️ Previous Summary Page", use_container_width=True, disabled=(st.session_state.summary_current_page <= 1)):
            st.session_state.summary_current_page -= 1; st.rerun()
        p_col2.markdown(f"<div style='text-align: center; font-weight: bold;'>Page {st.session_state.summary_current_page} of {total_pages}</div>", unsafe_allow_html=True)
        if p_col3.button("Next Summary Page ➡️", use_container_width=True, disabled=(st.session_state.summary_current_page >= total_pages)):
            st.session_state.summary_current_page += 1; st.rerun()

        if st.session_state.get("just_switched_to_edit"):
            st.toast(f"Loading '{st.session_state.edit_search_term}' in the 'Edit Invoice' tab...")
            del st.session_state.just_switched_to_edit
        
        st.markdown("---")
        st.subheader("Grand Totals for All Filtered Invoices")
        total_sqft_sum = pd.to_numeric(df_summary['total_sqft'], errors='coerce').sum(); total_amount_sum = pd.to_numeric(df_summary['total_amount'], errors='coerce').sum(); total_pcs_sum = pd.to_numeric(df_summary['total_pcs'], errors='coerce').sum(); total_net_sum = pd.to_numeric(df_summary['total_net'], errors='coerce').sum(); total_gross_sum = pd.to_numeric(df_summary['total_gross'], errors='coerce').sum(); total_cbm_sum = pd.to_numeric(df_summary['total_cbm'], errors='coerce').sum()
        gt_col1, gt_col2, gt_col3 = st.columns(3); gt_col1.metric("Total Sqft", f"{total_sqft_sum:,.2f}"); gt_col2.metric("Total Amount", f"$ {total_amount_sum:,.2f}"); gt_col3.metric("Total Pcs", f"{total_pcs_sum:,.0f}")
        gt_col4, gt_col5, gt_col6 = st.columns(3); gt_col4.metric("Total Net Weight (KG)", f"{total_net_sum:,.2f}"); gt_col5.metric("Total Gross Weight (KG)", f"{total_gross_sum:,.2f}"); gt_col6.metric("Total CBM", f"{total_cbm_sum:,.3f}")

# ==============================================================================
# --- TAB 2: Detailed View (WITH PAGINATION) ---
# ==============================================================================
with tab2:
    st.header("Detailed Line-Item View")
    
    # --- State and Reset for Detailed Filters ---
    detailed_filter_keys = ['view_option', 'ref_filter', 'no_filter', 'po_filter', 'item_filter', 'inv_date_text_filter', 'prod_order_filter', 'date_range', 'container_filter']
    if 'detailed_current_page' not in st.session_state:
        st.session_state.detailed_current_page = 1

    def reset_detailed_filters_and_page():
        for key in detailed_filter_keys: st.session_state[key] = None if key == 'date_range' else ("Active" if key == 'view_option' else "")
        st.session_state.detailed_current_page = 1

    with st.expander("🔍 Filters for Detailed View", expanded=True):
        st.radio("Choose which invoices to display:", ("Active", "Voided", "All"), horizontal=True, key='view_option')
        d_col1, d_col2, d_col3 = st.columns(3); d_col1.text_input("Filter by Invoice Ref:", key='ref_filter'); d_col1.text_input("Filter by Invoice No:", key='no_filter'); d_col2.text_input("Filter by PO:", key='po_filter'); d_col2.text_input("Filter by Item Code:", key='item_filter'); d_col3.text_input("Filter by Production Order No:", key='prod_order_filter'); d_col3.text_input("Filter by Container/Truck:", key='container_filter')
        today_date = datetime.now().date(); st.date_input("Filter by Creation Date Range:", value=st.session_state.get('date_range') or (today_date, today_date), key='date_range')
        st.button("Reset All Detailed Filters", on_click=reset_detailed_filters_and_page, use_container_width=True, key="reset_detailed")
    
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            base_query = f"""SELECT i.*, (SELECT GROUP_CONCAT(c.container_description, ', ') FROM {CONTAINER_TABLE_NAME} c WHERE c.inv_ref = i.inv_ref) AS containers FROM {TABLE_NAME} i"""; conditions, params = [], []
            if st.session_state.view_option == "Active": conditions.append("i.status = ?"); params.append('active')
            elif st.session_state.view_option == "Voided": conditions.append("i.status = ?"); params.append('voided')
            text_filters_config = {'ref_filter': 'i.inv_ref', 'no_filter': 'i.inv_no', 'po_filter': 'i.po', 'item_filter': 'i.item', 'prod_order_filter': 'i.production_order_no'}
            for key, column in text_filters_config.items():
                if st.session_state.get(key): conditions.append(f"LOWER({column}) LIKE ?"); params.append(f"%{st.session_state[key].lower()}%")
            if st.session_state.get('container_filter'): conditions.append(f"i.inv_ref IN (SELECT c.inv_ref FROM {CONTAINER_TABLE_NAME} c WHERE LOWER(c.container_description) LIKE ?)"); params.append(f"%{st.session_state.container_filter.lower()}%")
            if st.session_state.get('date_range') and len(st.session_state.date_range) == 2: start_date, end_date = st.session_state.date_range; start_dt = datetime.combine(start_date, datetime.min.time()).strftime('%Y-%m-%d %H:%M:%S'); end_dt = datetime.combine(end_date, datetime.max.time()).strftime('%Y-%m-%d %H:%M:%S'); conditions.append("i.creating_date BETWEEN ? AND ?"); params.extend([start_dt, end_dt])
            query = f"{base_query} WHERE {' AND '.join(conditions)}" if conditions else base_query; query += " ORDER BY i.creating_date DESC, i.inv_ref, i.id"
            df_detailed = pd.read_sql_query(query, conn, params=params)
    except Exception as e: st.error(f"Could not read detailed data from the database. Error: {e}"); st.exception(e); st.stop()
    
    if df_detailed.empty:
        st.info("No records match your current filter criteria in the detailed view.")
    else:
        ITEMS_PER_PAGE_DETAILED = 50
        total_items_detailed = len(df_detailed)
        total_pages_detailed = math.ceil(total_items_detailed / ITEMS_PER_PAGE_DETAILED)

        if st.session_state.detailed_current_page > total_pages_detailed:
            st.session_state.detailed_current_page = total_pages_detailed if total_pages_detailed > 0 else 1

        start_idx_detailed = (st.session_state.detailed_current_page - 1) * ITEMS_PER_PAGE_DETAILED
        end_idx_detailed = start_idx_detailed + ITEMS_PER_PAGE_DETAILED
        paginated_df_detailed = df_detailed.iloc[start_idx_detailed:end_idx_detailed]

        st.success(f"Found {total_items_detailed} matching line items. Showing page {st.session_state.detailed_current_page} of {total_pages_detailed}.")
        st.dataframe(paginated_df_detailed, use_container_width=True)

        st.markdown("---")
        p2_col1, p2_col2, p2_col3 = st.columns([1.5, 1, 1.5])
        if p2_col1.button("⬅️ Previous Detail Page", use_container_width=True, disabled=(st.session_state.detailed_current_page <= 1)):
            st.session_state.detailed_current_page -= 1; st.rerun()
        p2_col2.markdown(f"<div style='text-align: center; font-weight: bold;'>Page {st.session_state.detailed_current_page} of {total_pages_detailed}</div>", unsafe_allow_html=True)
        if p2_col3.button("Next Detail Page ➡️", use_container_width=True, disabled=(st.session_state.detailed_current_page >= total_pages_detailed)):
            st.session_state.detailed_current_page += 1; st.rerun()

# ==============================================================================
# --- TAB 3: Edit Invoice (No Changes) ---
# ==============================================================================
with tab3:
    # ... Code for Edit Invoice tab is unchanged ...
    st.header("Find & Edit an Invoice")
    st.info("Select an invoice from the 'Invoice Summary' tab by clicking its 'Edit' button, or use the search below.")
    search_mode_label = st.radio("Search By:", ("Invoice Number", "Invoice Reference"), key="edit_search_mode", horizontal=True)
    search_column = "inv_no" if search_mode_label == "Invoice Number" else "inv_ref"
    search_term = st.text_input(f"Enter part of the {search_mode_label}:", key="edit_search_term")
    if search_term:
        matches = find_active_invoices(search_column, search_term)
        if not matches: st.warning(f"No active invoices found matching '{search_term}'.")
        else:
            display_map = {f"Inv No: {m['inv_no']} (Ref: {m['inv_ref']})": m['inv_ref'] for m in matches}
            is_pre_selected = st.session_state.get('edit_search_term', '') in display_map.values()
            selected_display_option = st.selectbox("Select an invoice to edit:", options=[""] + list(display_map.keys()), key="edit_selection", index=1 if len(matches) == 1 or is_pre_selected else 0)
            if selected_display_option:
                selected_ref = display_map[selected_display_option]
                history_key = f"history_{selected_ref}"; history_index_key = f"history_index_{selected_ref}"
                if history_key not in st.session_state:
                    initial_df = get_invoice_line_items(selected_ref); initial_containers = get_invoice_containers(selected_ref)
                    st.session_state[history_key] = [{'df': initial_df, 'containers_text': "\n".join(initial_containers)}]
                    st.session_state[history_index_key] = 0
                st.subheader(f"Editing Invoice: {selected_ref}")
                current_state = st.session_state[history_key][st.session_state[history_index_key]]
                df_to_display = current_state['df']; containers_to_display = current_state['containers_text']
                edited_df = st.data_editor(df_to_display, num_rows="dynamic", key=f"editor_{selected_ref}", use_container_width=True, disabled=['id', 'inv_ref'])
                st.subheader("Containers / Trucks (One per line)"); edited_containers_text = st.text_area("Containers:", value=containers_to_display, key=f"containers_{selected_ref}", height=100)
                df_changed = not edited_df.equals(df_to_display); containers_changed = (edited_containers_text != containers_to_display)
                if df_changed or containers_changed:
                    st.session_state[history_key] = st.session_state[history_key][:st.session_state[history_index_key] + 1]
                    st.session_state[history_key].append({'df': edited_df, 'containers_text': edited_containers_text})
                    st.session_state[history_index_key] = len(st.session_state[history_key]) - 1
                    st.rerun()
                st.markdown("---")
                e_col1, e_col2, e_col3, _ = st.columns([1, 1, 1, 5])
                e_col1.button("↩️ Undo", on_click=undo, args=(history_index_key,), disabled=(st.session_state.get(history_index_key, 0) <= 0), use_container_width=True)
                e_col2.button("↪️ Redo", on_click=redo, args=(history_key, history_index_key), disabled=(st.session_state.get(history_index_key, 0) >= len(st.session_state.get(history_key, [])) - 1), use_container_width=True)
                if e_col3.button("💾 Save Changes", type="primary", use_container_width=True):
                    state_to_save = st.session_state[history_key][st.session_state[history_index_key]]
                    df_to_save = state_to_save['df']; containers_to_save = [line.strip() for line in state_to_save['containers_text'].split('\n') if line.strip()]
                    if not (df_to_save['inv_ref'] == selected_ref).all(): st.error(f"Error: The 'inv_ref' column cannot be changed. It must remain '{selected_ref}'.")
                    else:
                        try:
                            update_invoice_data(selected_ref, df_to_save, containers_to_save)
                            st.success(f"Invoice '{selected_ref}' has been updated successfully!")
                            keys_to_delete = [history_key, history_index_key, f"editor_{selected_ref}", f"containers_{selected_ref}", "edit_selection", "edit_search_term"]
                            for key in keys_to_delete:
                                if key in st.session_state: del st.session_state[key]
                            st.rerun()
                        except Exception as e: st.error(f"Failed to save changes. Error: {e}")