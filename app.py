import streamlit as st
import pandas as pd
from datetime import date
import database as db
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(page_title="PG Lead CRM", layout="wide", page_icon="🏢", initial_sidebar_state="expanded")

# --- Initialize Database ---
db.init_db()

# --- Custom CSS Injection (Minimal Strict Light Theme) ---
st.markdown("""
<style>
/* Global Light Theme */
.stApp {
    background-color: #f8fafc !important;
}
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}
/* Ensure general text remains dark for readability */
h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: #0f172a;
}
/* Form inputs light */
.stTextInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #0f172a !important;
}
/* Primary Button styling to ensure text is white */
div[data-testid="stFormSubmitButton"] button p, div[data-testid="stButton"] button[kind="primary"] p {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# --- Constants ---
STATUS_OPTIONS = ['New', 'Contacted', 'Visit Scheduled', 'Won', 'Lost']
PG_LOCATIONS = [
    'Koramangala Phase 1', 
    'HSR Layout Sector 2', 
    'Indiranagar 100ft', 
    'Whitefield Main',
    'BTM Layout Stage 2'
]

# --- Navigation Sidebar ---
with st.sidebar:
    st.title("🏢 PG Admin")
    st.divider()
    page = st.radio("Navigation", ["📊 Dashboard", "📝 Capture Lead", "⚙️ Pipeline Operations"])

# --- View 1: Dashboard ---
if page == "📊 Dashboard":
    st.title("Enterprise CRM Dashboard")
    st.caption("Overview of your sales pipeline, key metrics, and recent activity.")
    st.divider()
    
    stats = db.get_dashboard_stats()
    metrics = stats['metrics']
    
    # Top Row: 4 Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        with st.container(border=True):
            st.metric("Total Leads", metrics['Total Leads'])
    with col2:
        with st.container(border=True):
            st.metric("New Leads", metrics['New Leads'])
    with col3:
        with st.container(border=True):
            st.metric("Visits Scheduled", metrics['Upcoming Visits'])
    with col4:
        with st.container(border=True):
            st.metric("Conversions (Won)", metrics['Conversions (Won)'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Middle Row: Charts and Recent Leads
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Stacked Chart 1
        with st.container(border=True):
            st.subheader("Lead Pipeline")
            st.caption("Conversion funnel from New to Won.")
            st.divider()
            funnel_data = stats['funnel_data']
            stages = ['New', 'Contacted', 'Visit Scheduled', 'Won']
            values = [funnel_data.get(s, 0) for s in stages]
            
            if sum(values) > 0:
                fig_funnel = px.funnel(x=values, y=stages, color_discrete_sequence=['#3B82F6'], template="plotly_white")
                fig_funnel.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_funnel, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Not enough data to display funnel chart.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Stacked Chart 2
        with st.container(border=True):
            st.subheader("Leads by Location")
            st.caption("Distribution of prospective residents across properties.")
            st.divider()
            loc_data = stats['location_data']
            if loc_data:
                loc_df = pd.DataFrame(loc_data, columns=['Location', 'Count'])
                fig_donut = px.pie(loc_df, values='Count', names='Location', hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel, template="plotly_white")
                fig_donut.update_traces(textposition='inside', textinfo='percent+label')
                fig_donut.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
                st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Not enough data to display location chart.")
                
    with col_right:
        # Recent Leads Feed
        with st.container(border=True):
            st.subheader("📋 Latest Leads")
            st.caption("Most recently captured prospects.")
            st.divider()
            
            all_leads_df = db.get_leads()
            if not all_leads_df.empty:
                recent_leads = all_leads_df.head(5)[['name', 'status']]
                st.dataframe(
                    recent_leads,
                    column_config={
                        "name": "Name",
                        "status": "Status"
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No recent leads available.")

# --- View 2: Capture Lead ---
elif page == "📝 Capture Lead":
    st.title("Capture New Lead")
    st.caption("Enter details for a new prospective resident into the system.")
    st.divider()
    
    with st.container(border=True):
        with st.form("capture_lead_form", clear_on_submit=True):
            st.subheader("Prospect Information")
            st.caption("Ensure all required fields are filled accurately.")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name *", placeholder="e.g., Jane Smith")
                phone = st.text_input("Phone Number *", placeholder="e.g., +91 9876543210")
            with col2:
                pg_location = st.selectbox("PG Location *", PG_LOCATIONS)
                move_in_date = st.date_input("Expected Move-in Date *", min_value=date.today())
                
            st.markdown("<br>", unsafe_allow_html=True)
            submit_button = st.form_submit_button("Save Lead", type="primary")
            
            if submit_button:
                if not name.strip() or not phone.strip():
                    st.error("⚠️ Name and Phone Number are required fields.")
                else:
                    db.add_lead(name, phone, pg_location, move_in_date.strftime('%Y-%m-%d'))
                    st.success(f"✅ Lead '{name}' successfully captured and added to pipeline!")

# --- View 3: Pipeline Operations ---
elif page == "⚙️ Pipeline Operations":
    st.title("Pipeline Operations")
    st.caption("Manage lead statuses, assign agents, and schedule visits efficiently.")
    st.divider()
    
    leads_df = db.get_leads()
    agents_df = db.get_agents()
    
    # Safely convert string dates to actual datetime/date objects to prevent Streamlit compatibility crashes
    if not leads_df.empty:
        leads_df['visit_date'] = pd.to_datetime(leads_df['visit_date'], errors='coerce').dt.date
        leads_df['move_in_date'] = pd.to_datetime(leads_df['move_in_date'], errors='coerce').dt.date
        leads_df['created_at'] = pd.to_datetime(leads_df['created_at'], errors='coerce')
    
    if leads_df.empty:
        st.info("No leads available in the pipeline yet.")
    else:
        agent_names = ["Unassigned"] + list(agents_df['name'])
        
        # Prepare dataframe for editing
        edit_df = leads_df[['id', 'name', 'phone', 'pg_location', 'status', 'agent_name', 'visit_date', 'move_in_date', 'created_at']].copy()
        edit_df['agent_name'] = edit_df['agent_name'].fillna("Unassigned")
        
        with st.container(border=True):
            st.subheader("Interactive Pipeline Data-Grid")
            st.caption("Double-click cells to update lead status, assign agents, or schedule visits.")
            
            edited_df = st.data_editor(
                edit_df,
                column_config={
                    "id": None, # Hide ID
                    "name": st.column_config.TextColumn("Name", disabled=True),
                    "phone": st.column_config.TextColumn("Phone", disabled=True),
                    "pg_location": st.column_config.TextColumn("Location", disabled=True),
                    "status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS, required=True),
                    "agent_name": st.column_config.SelectboxColumn("Agent", options=agent_names, required=True),
                    "visit_date": st.column_config.DateColumn("Visit Date", format="YYYY-MM-DD"),
                    "move_in_date": st.column_config.DateColumn("Move-in Date", disabled=True),
                    "created_at": st.column_config.DatetimeColumn("Created At", disabled=True, format="YYYY-MM-DD HH:mm"),
                },
                hide_index=True,
                use_container_width=True,
                num_rows="fixed"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Save Changes", type="primary"):
                changes_made = 0
                
                # Use fillna to safely compare edited rows
                edit_df_comp = edit_df.fillna("")
                edited_df_comp = edited_df.fillna("")
                
                for idx in range(len(edit_df)):
                    orig = edit_df_comp.iloc[idx]
                    new = edited_df_comp.iloc[idx]
                    
                    if (orig['status'] != new['status']) or (orig['agent_name'] != new['agent_name']) or (orig['visit_date'] != new['visit_date']):
                        
                        agent_id = None
                        if new['agent_name'] != "Unassigned" and new['agent_name'] != "":
                            match = agents_df[agents_df['name'] == new['agent_name']]
                            if not match.empty:
                                agent_id = int(match['id'].iloc[0])
                        
                        v_date = new['visit_date']
                        v_date_str = str(v_date) if v_date != "" else None
                        
                        db.update_lead(orig['id'], new['status'], agent_id, v_date_str)
                        changes_made += 1
                        
                if changes_made > 0:
                    st.success(f"✅ Successfully updated {changes_made} lead(s)!")
                    st.rerun()
                else:
                    st.info("No changes detected.")

# --- Footer ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("<center><p style='color: #64748b; font-size: 0.85rem;'>© 2026 Gharpayy CRM MVP | Enterprise Edition</p></center>", unsafe_allow_html=True)
