import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import logging
import traceback
import sys
import os
from data_visualization import (
    create_monthly_trends,
    create_budget_distribution_chart,
    create_widows_support_chart,
    create_donor_contribution_chart,
    create_comparison_chart,
    create_monthly_budget_chart,
    create_forecast_chart
)
from data_processing import (
    calculate_monthly_averages,
    calculate_total_support,
    calculate_monthly_budget,
    calculate_donor_statistics,
    calculate_expense_statistics,
    calculate_widow_statistics,
    calculate_monthly_trends,
    calculate_budget_forecast,
    calculate_36_month_budget
)
from reports import (
    generate_monthly_report,
    generate_widows_report,
    generate_donor_report,
    generate_budget_report
)
from alerts import (
    check_budget_alerts,
    check_data_quality_alerts,
    check_widows_alerts,
    check_donations_alerts,
    display_alerts
)
import streamlit.components.v1 as components
from pyvis.network import Network
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Set page config
st.set_page_config(
    page_title="מערכת ניהול עמותת עמרי",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add success message function
def show_success_message(message):
    """Show a success message with custom styling that auto-dismisses after 3 seconds"""
    # Create a placeholder for the message
    message_placeholder = st.empty()
    
    # Show the message
    message_placeholder.success(f"✅ {message}")
    
    # Auto-dismiss after 3 seconds using JavaScript
    st.markdown(f"""
    <script>
    setTimeout(function() {{
        // Find and hide the success message
        var successElements = document.querySelectorAll('.stAlert');
        successElements.forEach(function(element) {{
            if (element.textContent.includes('{message}')) {{
                element.style.display = 'none';
            }}
        }});
    }}, 3000);
    </script>
    """, unsafe_allow_html=True)

# Add custom CSS for RTL support and styling
st.markdown("""
    <style>
    /* RTL Support */
    .stApp {
            direction: rtl;
        text-align: right;
    }
    
    /* Typography improvements */
    h1 {
        font-size: 2.5rem !important;
        font-weight: bold !important;
        color: #1f2937 !important;
        margin-bottom: 1.5rem !important;
    }
    
    h2 {
        font-size: 2rem !important;
        font-weight: bold !important;
        color: #374151 !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #4b5563 !important;
        margin-bottom: 0.75rem !important;
    }
    
    .stSubheader {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: #6b7280 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Sidebar typography */
    .css-1d391kg {
        font-size: 1.1rem !important;
    }
    
    .css-1d391kg h1 {
        font-size: 1.8rem !important;
    }
    
    .css-1d391kg h2 {
        font-size: 1.4rem !important;
    }
    
    .css-1d391kg h3 {
        font-size: 1.2rem !important;
    }
    
    /* Google Docs style tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: #f8f9fa;
        border-bottom: 1px solid #e1e5ea;
        padding: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: nowrap;
        background-color: transparent;
        border-radius: 0;
        border: none;
        border-bottom: 2px solid transparent;
        color: #5f6368;
        font-weight: 500;
        font-size: 14px;
        padding: 0 24px;
        margin: 0;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f1f3f4;
        color: #202124;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: white;
        color: #1a73e8;
        border-bottom: 2px solid #1a73e8;
        font-weight: 600;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding: 24px 0;
    }
    
    /* Metric Cards */
        .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
            text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card h3 {
        color: #666;
        font-size: 1.1em;
        margin-bottom: 10px;
    }
    .metric-card h2 {
        color: #1f77b4;
        font-size: 1.8em;
        margin: 0;
    }
    
    /* Tables */
    .stDataFrame {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Charts */
    .stPlotlyChart {
            background-color: white;
        border-radius: 10px;
        padding: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 10px;
        margin: 10px 0;
        font-size: 1rem !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #1f77b4;
            color: white;
            border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 1rem !important;
    }
    .stButton button:hover {
        background-color: #1668a1;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-size: 1rem !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
    
    /* Data editor */
    .stDataEditor {
        font-size: 0.9rem !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    /* Metric styling */
    .css-1wivap2 {
        font-size: 1.2rem !important;
    }
    
    .css-1wivap2 > div > div > div {
        font-size: 1.5rem !important;
        font-weight: bold !important;
    }
    
    /* General text */
    p, div, span {
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
    
    /* Strong text */
    strong {
        font-weight: 600 !important;
        color: #374151 !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_cached_data():
    """Load and cache data from Excel files"""
    try:
        logging.info("Loading data...")
        
        # Check if files exist
        if not os.path.exists('omri.xlsx'):
            error_msg = "קובץ omri.xlsx לא נמצא"
            logging.error(error_msg)
            st.error(error_msg)
            return None, None, None, None, None
            
        if not os.path.exists('almanot.xlsx'):
            error_msg = "קובץ almanot.xlsx לא נמצא"
            logging.error(error_msg)
            st.error(error_msg)
            return None, None, None, None, None
            
        # Load data
        try:
            # Load expenses data
            expenses_df = pd.read_excel('omri.xlsx', sheet_name='Expenses', engine='openpyxl')
            expenses_df = expenses_df.dropna(subset=['תאריך', 'שם', 'שקלים'])  # Remove rows with missing values
            expenses_df = expenses_df[expenses_df['שקלים'] != 0]  # Remove rows with zero amounts
            expenses_df['שקלים'] = expenses_df['שקלים'].abs()  # Convert to positive for display
            logging.info(f"קובץ Expenses נטען בהצלחה")
            
            # Load donations data
            donations_df = pd.read_excel('omri.xlsx', sheet_name='Donations', engine='openpyxl')
            donations_df = donations_df.dropna(subset=['תאריך', 'שם', 'שקלים'])  # Remove rows with missing values
            donations_df = donations_df[donations_df['שקלים'] != 0]  # Remove rows with zero amounts
            logging.info(f"קובץ Donations נטען בהצלחה")
            
            # Load investors data
            investors_df = pd.read_excel('omri.xlsx', sheet_name='Investors', engine='openpyxl')
            investors_df = investors_df.dropna(subset=['תאריך', 'שם', 'שקלים'])  # Remove rows with missing values
            investors_df = investors_df[investors_df['שקלים'] != 0]  # Remove rows with zero amounts
            logging.info(f"קובץ Investors נטען בהצלחה")
            
            # Combine all data into one dataframe
            omri_df = pd.concat([expenses_df, donations_df, investors_df], ignore_index=True)
            logging.info(f"נוצר DataFrame מאוחד עם {len(omri_df)} שורות")
            
        except Exception as e:
            error_msg = f"שגיאה בטעינת קובץ omri.xlsx: {str(e)}"
            logging.error(error_msg)
            st.error(error_msg)
            return None, None, None, None, None
            
        try:
            # Load widows data
            almanot_df = pd.read_excel('almanot.xlsx', engine='openpyxl')
            
            # Check required columns
            required_columns = ['שם ', 'סכום חודשי', 'חודש התחלה']
            missing_columns = [col for col in required_columns if col not in almanot_df.columns]
            if missing_columns:
                error_msg = f"חסרות עמודות בקובץ almanot.xlsx: {', '.join(missing_columns)}"
                logging.error(error_msg)
                st.error(error_msg)
                return None, None, None, None, None
            
            # Convert problematic columns to string to avoid type conflicts
            string_columns = ['טלפון', 'תעודת זהות', 'מייל', 'תורם', 'איש קשר לתרומה', 'הערות']
            for col in string_columns:
                if col in almanot_df.columns:
                    almanot_df[col] = almanot_df[col].astype(str)
            
            # Remove rows with missing values
            almanot_df = almanot_df.dropna(subset=['שם ', 'סכום חודשי', 'חודש התחלה'])
            logging.info(f"קובץ almanot.xlsx נטען בהצלחה")
            
        except Exception as e:
            error_msg = f"שגיאה בטעינת קובץ almanot.xlsx: {str(e)}"
            logging.error(error_msg)
            st.error(error_msg)
            return None, None, None, None, None
        
        # Convert date columns
        try:
            omri_df['תאריך'] = pd.to_datetime(omri_df['תאריך'], errors='coerce')
            logging.info("עמודת תאריך הומרה בהצלחה")
        except Exception as e:
            error_msg = f"שגיאה בהמרת עמודת תאריך: {str(e)}"
            logging.error(error_msg)
            st.error(error_msg)
            return None, None, None, None, None
            
        try:
            almanot_df['חודש התחלה'] = pd.to_datetime(almanot_df['חודש התחלה'], errors='coerce')
            logging.info("עמודת חודש התחלה הומרה בהצלחה")
        except Exception as e:
            error_msg = f"שגיאה בהמרת עמודת חודש התחלה: {str(e)}"
            logging.error(error_msg)
            st.error(error_msg)
            return None, None, None, None, None
        
        # Convert numeric columns
        try:
            omri_df['שקלים'] = pd.to_numeric(omri_df['שקלים'], errors='coerce')
            logging.info("עמודת שקלים הומרה למספרים")
        except Exception as e:
            error_msg = f"שגיאה בהמרת עמודת שקלים למספרים: {str(e)}"
            logging.error(error_msg)
            st.error(error_msg)
            return None, None, None, None, None
            
        try:
            almanot_df['סכום חודשי'] = pd.to_numeric(almanot_df['סכום חודשי'], errors='coerce')
            logging.info("עמודת סכום חודשי הומרה למספרים")
        except Exception as e:
            error_msg = f"שגיאה בהמרת עמודת סכום חודשי למספרים: {str(e)}"
            logging.error(error_msg)
            st.error(error_msg)
            return None, None, None, None, None
        
        # Create donations dataframe
        try:
            donations_df = omri_df[omri_df['שקלים'] > 0].copy()
            logging.info(f"נוצר DataFrame תרומות עם {len(donations_df)} שורות")
        except Exception as e:
            error_msg = f"שגיאה ביצירת DataFrame תרומות: {str(e)}"
            logging.error(error_msg)
            st.error(error_msg)
            return None, None, None, None, None
        
        # Create expenses dataframe - use the original Expenses sheet
        try:
            expenses_df = pd.read_excel('omri.xlsx', sheet_name='Expenses', engine='openpyxl')
            expenses_df = expenses_df.dropna(subset=['תאריך', 'שם', 'שקלים'])  # Remove rows with missing values
            expenses_df = expenses_df[expenses_df['שקלים'] != 0]  # Remove rows with zero amounts
            expenses_df['שקלים'] = expenses_df['שקלים'].abs()  # Convert to positive for display
            logging.info(f"נוצר DataFrame הוצאות עם {len(expenses_df)} שורות")
        except Exception as e:
            error_msg = f"שגיאה ביצירת DataFrame הוצאות: {str(e)}"
            logging.error(error_msg)
            st.error(error_msg)
            return None, None, None, None, None
        
        logging.info("כל הנתונים נטענו בהצלחה")
        return omri_df, almanot_df, donations_df, expenses_df, investors_df
        
    except Exception as e:
        error_msg = f"שגיאה כללית בטעינת הנתונים: {str(e)}"
        logging.error(error_msg)
        logging.error(traceback.format_exc())
        st.error(error_msg)
        return None, None, None, None, None

def save_expenses_data(expenses_df):
    """Save expenses data to Excel file"""
    try:
        with pd.ExcelWriter("omri.xlsx", engine="openpyxl", mode="a") as writer:
            expenses_df.to_excel(writer, sheet_name="Expenses", index=False)
        st.session_state.changes_made['expenses'] = False
        st.success("הוצאות נשמרו בהצלחה!")
    except Exception as e:
        st.error(f"שגיאה בשמירת הוצאות: {str(e)}")

def save_donations_data(donations_df):
    """Save donations data to Excel file"""
    try:
        with pd.ExcelWriter("omri.xlsx", engine="openpyxl", mode="a") as writer:
            donations_df.to_excel(writer, sheet_name="Donations", index=False)
        st.session_state.changes_made['donations'] = False
        st.success("תרומות נשמרו בהצלחה!")
    except Exception as e:
        st.error(f"שגיאה בשמירת תרומות: {str(e)}")

def save_widows_data(almanot_df):
    """Save widows data to Excel file"""
    try:
        almanot_df.to_excel("almanot.xlsx", index=False)
        st.session_state.changes_made['widows'] = False
        st.success("נתוני אלמנות נשמרו בהצלחה!")
    except Exception as e:
        st.error(f"שגיאה בשמירת נתוני אלמנות: {str(e)}")

def main():
    """Main function to run the dashboard"""
    try:
        # Initialize session state for tracking changes
        if 'changes_made' not in st.session_state:
            st.session_state.changes_made = {
                'expenses': False,
                'donations': False,
                'investors': False,
                'widows': False
            }
        
        # Load data
        omri_df, almanot_df, donations_df, expenses_df, investors_df = load_cached_data()
        
        # Check if data was loaded successfully
        if omri_df is None or almanot_df is None or donations_df is None or expenses_df is None or investors_df is None:
            st.error("לא ניתן להמשיך ללא נתונים תקינים")
            return
        
        # Show success message for data loading
        show_success_message("הנתונים נטענו בהצלחה!")
        
        # Calculate statistics for alerts
        budget_status = calculate_monthly_budget(expenses_df, donations_df)
        donor_stats = calculate_donor_statistics(donations_df)
        widow_stats = calculate_widow_statistics(almanot_df)
        
        # Calculate missing variables for budget summary
        total_don = donations_df['שקלים'].sum() if 'שקלים' in donations_df.columns else 0
        sum_exp = expenses_df['שקלים'].sum() if 'שקלים' in expenses_df.columns else 0
        available = total_don - sum_exp
        
        # Add monthly_budget to budget_status if it doesn't exist
        if 'monthly_budget' not in budget_status:
            try:
                monthly_expenses = expenses_df.groupby(expenses_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum()
                monthly_donations = donations_df.groupby(donations_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum()
                
                monthly_budget_data = []
                all_months = sorted(set(monthly_expenses.index) | set(monthly_donations.index))
                
                for month in all_months:
                    expenses = monthly_expenses.get(month, 0)
                    donations = monthly_donations.get(month, 0)
                    balance = donations - expenses
                    coverage_ratio = (donations / expenses * 100) if expenses > 0 else 0
                    
                    monthly_budget_data.append({
                        'חודש': month,
                        'הוצאות': expenses,
                        'תרומות': donations,
                        'יתרה': balance,
                        'יחס כיסוי': coverage_ratio / 100
                    })
                
                budget_status['monthly_budget'] = monthly_budget_data
            except Exception as e:
                logging.error(f"Error creating monthly budget: {str(e)}")
                budget_status['monthly_budget'] = []
        
        # Navigation with tabs like Google Docs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["דף הבית", "ניהול תקציב", "ניהול תורמים", "ניהול אלמנות", "דוחות", "מפת קשרים"])
        
        # Display page content based on tab selection
        with tab1:
            st.markdown("<h1 style='text-align: center; color: #1f77b4; margin-bottom: 2rem;'>דף הבית - עמותת עמרי</h1>", unsafe_allow_html=True)
            
            # Quick Actions Row
            st.markdown("<h2 style='color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem;'>פעולות מהירות</h2>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("📊 דוח חודשי", use_container_width=True):
                    filename = generate_monthly_report(expenses_df, donations_df, almanot_df)
                    if filename:
                        show_success_message("דוח חודשי נוצר בהצלחה!")
                        with open(filename, "rb") as file:
                            st.download_button(
                                label="הורד דוח חודשי",
                                data=file.read(),
                                file_name=filename,
                                mime="application/pdf"
                            )
            with col2:
                if st.button("👥 דוח תורמים", use_container_width=True):
                    filename = generate_donor_report(donations_df)
                    if filename:
                        show_success_message("דוח תורמים נוצר בהצלחה!")
                        with open(filename, "rb") as file:
                            st.download_button(
                                label="הורד דוח תורמים",
                                data=file.read(),
                                file_name=filename,
                                mime="application/pdf"
                            )
            with col3:
                if st.button("👩 דוח אלמנות", use_container_width=True):
                    filename = generate_widows_report(almanot_df)
                    if filename:
                        show_success_message("דוח אלמנות נוצר בהצלחה!")
                        with open(filename, "rb") as file:
                            st.download_button(
                                label="הורד דוח אלמנות",
                                data=file.read(),
                                file_name=filename,
                                mime="application/pdf"
                            )
            with col4:
                if st.button("💰 דוח תקציב", use_container_width=True):
                    filename = generate_budget_report(expenses_df, donations_df)
                    if filename:
                        show_success_message("דוח תקציב נוצר בהצלחה!")
                        with open(filename, "rb") as file:
                            st.download_button(
                                label="הורד דוח תקציב",
                                data=file.read(),
                                file_name=filename,
                                mime="application/pdf"
                            )
            
            # General Statistics
            st.markdown("<h2 style='color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem;'>סטטיסטיקות כלליות</h2>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("סך תרומות", f"₪{total_don:,.0f}")
            with col2:
                st.metric("סך הוצאות", f"₪{sum_exp:,.0f}")
            with col3:
                st.metric("יתרה", f"₪{available:,.0f}")
            with col4:
                coverage = (total_don / sum_exp * 100) if sum_exp > 0 else 0
                st.metric("יחס כיסוי", f"{coverage:.1f}%")
            
            # Budget status indicator
            if available >= 0:
                status_color = "green"
                status_text = "עודף תקציב"
            else:
                status_color = "red"
                status_text = "גירעון תקציב"
            
            st.markdown(f"""
                <div style='text-align: center; padding: 15px; background-color: {status_color}; color: white; border-radius: 10px; font-size: 1.2rem; font-weight: bold; margin: 1rem 0;'>
                    {status_text}: ₪{abs(available):,.0f}
                </div>
            """, unsafe_allow_html=True)
            
            # Key Metrics Row
            st.markdown("<h2 style='color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem;'>מדדים מרכזיים</h2>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("מספר תורמים", f"{donor_stats['total_donors']:,}")
            with col2:
                st.metric("מספר אלמנות", f"{widow_stats['total_widows']:,}")
            with col3:
                st.metric("תמיכה חודשית", f"₪{widow_stats['total_support']:,.0f}")
            with col4:
                st.metric("תרומה ממוצעת", f"₪{donor_stats['avg_donation']:,.0f}")
            
            # Charts
            st.markdown("<h2 style='color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem;'>גרפים</h2>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                create_monthly_trends(expenses_df, donations_df)
            with col2:
                create_comparison_chart(expenses_df, donations_df)
            
            col3, col4 = st.columns(2)
            with col3:
                create_budget_distribution_chart(expenses_df)
            with col4:
                create_widows_support_chart(almanot_df)
            
            # Recent Activity
            st.markdown("<h2 style='color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem;'>פעילות אחרונה</h2>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<h3 style='color: #4b5563; margin-bottom: 1rem;'>תרומות אחרונות</h3>", unsafe_allow_html=True)
                recent_donations = donations_df.sort_values('תאריך', ascending=False).head(5)
                for _, donation in recent_donations.iterrows():
                    st.write(f"**{donation['שם']}** - ₪{donation['שקלים']:,.0f} ({donation['תאריך'].strftime('%d/%m/%Y')})")
            
            with col2:
                st.markdown("<h3 style='color: #4b5563; margin-bottom: 1rem;'>הוצאות אחרונות</h3>", unsafe_allow_html=True)
                recent_expenses = expenses_df.sort_values('תאריך', ascending=False).head(5)
                for _, expense in recent_expenses.iterrows():
                    st.write(f"**{expense['שם']}** - ₪{expense['שקלים']:,.0f} ({expense['תאריך'].strftime('%d/%m/%Y')})")
            
            # Alerts
            st.markdown("<h2 style='color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem;'>התראות</h2>", unsafe_allow_html=True)
            
            # Check for various alerts
            all_alerts = []
            
            # Budget alerts
            budget_alerts = check_budget_alerts(budget_status, donations_df)
            if budget_alerts:
                all_alerts.extend(budget_alerts)
            
            # Data quality alerts
            data_alerts = check_data_quality_alerts(expenses_df, donations_df, almanot_df)
            if data_alerts:
                all_alerts.extend(data_alerts)
            
            # Widows alerts
            widows_alerts = check_widows_alerts(widow_stats)
            if widows_alerts:
                all_alerts.extend(widows_alerts)
            
            # Donations alerts
            donations_alerts = check_donations_alerts(donor_stats)
            if donations_alerts:
                all_alerts.extend(donations_alerts)
            
            if all_alerts:
                for alert in all_alerts:
                    st.warning(alert)
            else:
                st.success("אין התראות פעילות")
        
        with tab2:
            st.markdown("<h1 style='text-align: center; color: #1f77b4; margin-bottom: 2rem;'>ניהול תקציב</h1>", unsafe_allow_html=True)
            
            # Budget Status
            st.markdown("<h2 style='color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem;'>סטטוס תקציב</h2>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("סך הוצאות", f"₪{budget_status['total_expenses']:,.2f}")
            with col2:
                st.metric("סך תרומות", f"₪{budget_status['total_donations']:,.2f}")
            with col3:
                st.metric("יתרה", f"₪{budget_status['balance']:,.2f}")
            with col4:
                st.metric("יחס כיסוי", f"{budget_status['coverage_ratio']:.1f}%")
            
            # Display budget status indicator
            status_color = {
                "עודף": "green",
                "מאוזן": "blue",
                "גירעון": "red"
            }.get(budget_status['status'], "gray")
            
            st.markdown(f"""
                <div style='text-align: center; padding: 15px; background-color: {status_color}; color: white; border-radius: 10px; font-size: 1.2rem; font-weight: bold; margin: 1rem 0;'>
                    סטטוס תקציב: {budget_status['status']}
                </div>
            """, unsafe_allow_html=True)
            
            # Monthly Trends
            st.markdown("<h2 style='color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem;'>מגמות חודשיות</h2>", unsafe_allow_html=True)
            trends = calculate_monthly_trends(expenses_df, donations_df)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "שינוי בהוצאות",
                    f"{trends['expenses_change']:.1f}%",
                    f"מגמה: {trends['expenses_trend']}"
                )
            with col2:
                st.metric(
                    "שינוי בתרומות",
                    f"{trends['donations_change']:.1f}%",
                    f"מגמה: {trends['donations_trend']}"
                )
            
            # Monthly Comparison
            st.markdown("<h2 style='color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem;'>השוואה חודשית</h2>", unsafe_allow_html=True)
            if trends['monthly_comparison']:
                st.markdown("<h3 style='color: #4b5563; margin-bottom: 1rem;'>השוואה חודשית</h3>", unsafe_allow_html=True)
                monthly_data = []
                for month, data in trends['monthly_comparison'].items():
                    monthly_data.append({
                        'חודש': month,
                        'הוצאות': data['expenses'],
                        'תרומות': data['donations'],
                        'יתרה': data['balance']
                    })
                
                monthly_df = pd.DataFrame(monthly_data)
                st.dataframe(
                    monthly_df.style.format({
                        'הוצאות': '₪{:,.0f}',
                        'תרומות': '₪{:,.0f}',
                        'יתרה': '₪{:,.0f}'
                    }),
                    use_container_width=True
                )
            
            # Donations Distribution
            st.markdown("<h2 style='color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem;'>התפלגות תרומות</h2>", unsafe_allow_html=True)
            donation_counts = donations_df['שקלים'].value_counts().sort_index()
            
            col1, col2 = st.columns(2)
            with col1:
                # Show top donation amounts
                st.markdown("<h3 style='color: #4b5563; margin-bottom: 1rem;'>🏆 סכומי תרומה נפוצים</h3>", unsafe_allow_html=True)
                for amount, count in donation_counts.head(10).items():
                    st.write(f"**₪{amount:,.0f}:** {count} תרומות")
            
            with col2:
                # Show donation statistics
                st.markdown("<h3 style='color: #4b5563; margin-bottom: 1rem;'>סטטיסטיקות תרומות</h3>", unsafe_allow_html=True)
                st.write(f"**תרומה ממוצעת:** ₪{donations_df['שקלים'].mean():,.0f}")
                st.write(f"**תרומה מקסימלית:** ₪{donations_df['שקלים'].max():,.0f}")
                st.write(f"**תרומה מינימלית:** ₪{donations_df['שקלים'].min():,.0f}")
                st.write(f"**חציון:** ₪{donations_df['שקלים'].median():,.0f}")
            
            # Charts
            st.markdown("<h2 style='color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem;'>גרפים</h2>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                create_monthly_trends(expenses_df, donations_df)
            with col2:
                create_comparison_chart(expenses_df, donations_df)
            
            # Display editable data tables
            st.subheader("עריכת נתונים")
            
            with st.expander("עריכת הוצאות"):
                edited_expenses = st.data_editor(
                    expenses_df,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "תאריך": st.column_config.DateColumn("תאריך", format="DD/MM/YYYY"),
                        "שקלים": st.column_config.NumberColumn("שקלים", format="₪%d")
                    },
                    key="expenses_editor"
                )
                # Check if expenses were changed
                if not edited_expenses.equals(expenses_df):
                    st.session_state.changes_made['expenses'] = True
            
            with st.expander("עריכת תרומות"):
                column_config = {}
                if "שם" in donations_df.columns:
                    column_config["שם"] = st.column_config.TextColumn("שם", required=True)
                if "שקלים" in donations_df.columns:
                    column_config["שקלים"] = st.column_config.NumberColumn("שקלים", format="₪%d")
                if "תאריך" in donations_df.columns:
                    column_config["תאריך"] = st.column_config.DateColumn("תאריך", format="DD/MM/YYYY")
                if "הערות" in donations_df.columns:
                    column_config["הערות"] = st.column_config.TextColumn("הערות")
                
                edited_donations = st.data_editor(
                    donations_df,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config=column_config,
                    key="donations_budget_editor"
                )
                # Check if donations were changed
                if not edited_donations.equals(donations_df):
                    st.session_state.changes_made['donations'] = True
            
            with st.expander("עריכת משקיעים"):
                column_config = {}
                if "תאריך" in investors_df.columns:
                    column_config["תאריך"] = st.column_config.DateColumn("תאריך", format="DD/MM/YYYY")
                if "שקלים" in investors_df.columns:
                    column_config["שקלים"] = st.column_config.NumberColumn("שקלים", format="₪%d")
                
                edited_investors = st.data_editor(
                    investors_df,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config=column_config,
                    key="investors_budget_editor"
                )
                # Check if investors were changed
                if not edited_investors.equals(investors_df):
                    st.session_state.changes_made['investors'] = True
            
            with st.expander("עריכת אלמנות"):
                column_config = {}
                if "חודש התחלה" in almanot_df.columns:
                    column_config["חודש התחלה"] = st.column_config.DateColumn("חודש התחלה", format="DD/MM/YYYY")
                if "סכום חודשי" in almanot_df.columns:
                    column_config["סכום חודשי"] = st.column_config.NumberColumn("סכום חודשי", format="₪%d")
                if "שם " in almanot_df.columns:
                    column_config["שם "] = st.column_config.TextColumn("שם", required=True)
                if "מייל" in almanot_df.columns:
                    column_config["מייל"] = st.column_config.TextColumn("מייל")
                if "טלפון" in almanot_df.columns:
                    column_config["טלפון"] = st.column_config.TextColumn("טלפון")
                if "תעודת זהות" in almanot_df.columns:
                    column_config["תעודת זהות"] = st.column_config.TextColumn("תעודת זהות")
                if "מספר ילדים" in almanot_df.columns:
                    column_config["מספר ילדים"] = st.column_config.NumberColumn("מספר ילדים", min_value=0)
                if "חללים" in almanot_df.columns:
                    column_config["חללים"] = st.column_config.CheckboxColumn("חללים")
                if "הערות" in almanot_df.columns:
                    column_config["הערות"] = st.column_config.TextColumn("הערות")
                if "תורם" in almanot_df.columns:
                    column_config["תורם"] = st.column_config.TextColumn("תורם")
                if "איש קשר לתרומה" in almanot_df.columns:
                    column_config["איש קשר לתרומה"] = st.column_config.TextColumn("איש קשר לתרומה")
                
                edited_almanot = st.data_editor(
                    almanot_df,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config=column_config,
                    key="widows_budget_editor"
                )
                # Check if widows were changed
                if not edited_almanot.equals(almanot_df):
                    st.session_state.changes_made['widows'] = True
            
            # Save edited data - only show if there are changes
            if any(st.session_state.changes_made.values()):
                if st.button("שמור שינויים", type="primary"):
                    try:
                        with pd.ExcelWriter("omri.xlsx", engine="openpyxl") as writer:
                            expenses_df.to_excel(writer, sheet_name="Expenses", index=False)
                            edited_donations.to_excel(writer, sheet_name="Donations", index=False)
                            edited_investors.to_excel(writer, sheet_name="Investors", index=False)
                        
                        # Reset all change flags
                        for key in st.session_state.changes_made:
                            st.session_state.changes_made[key] = False
                        
                        st.success("השינויים נשמרו בהצלחה!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"שגיאה בשמירת השינויים: {str(e)}")
            else:
                st.info("אין שינויים לשמירה")
            
            # Display budget alerts
            st.subheader("התראות תקציב")
            budget_alerts = check_budget_alerts(budget_status, donations_df)
            if budget_alerts:
                for alert in budget_alerts:
                    st.warning(alert)
            else:
                st.success("אין התראות תקציב")
            
            # Calculate current monthly support for 36-month forecast
            if "סכום חודשי" in almanot_df.columns:
                count_1000 = int((almanot_df["סכום חודשי"] == 1000).sum())
                count_2000 = int((almanot_df["סכום חודשי"] == 2000).sum())
                current_monthly_support = (count_1000 * 1000) + (count_2000 * 2000)
                support_36_months = current_monthly_support * 36
            else:
                count_1000 = 0
                count_2000 = 0
                current_monthly_support = 0
                support_36_months = 0
            
            # Display 36-Month Budget Forecast
            st.markdown("<h2 style='color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem;'>תחזית תקציב (36 חודשים)</h2>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                n1 = st.slider(
                    "כמות אלמנות ₪1,000/קרן",
                    min_value=0,
                    max_value=int((available / (1000 * 36)) + 10),
                    value=0,
                    step=1
                )
                req1 = n1 * 1000 * 12 * 3
            
            with col2:
                n2 = st.slider(
                    "כמות אלמנות ₪2,000/קרן",
                    min_value=0,
                    max_value=int((available / (2000 * 36)) + 10),
                    value=0,
                    step=1
                )
                req2 = n2 * 2000 * 12 * 3
            
            # Calculate required budget
            total_required = req1 + req2
            diff = available - support_36_months
            
            st.write(f"**סכום נדרש לתמיכה:** ₪{total_required:,.0f}")
            st.write(f"**סכום זמין לתמיכה:** ₪{support_36_months:,.0f}")
            
            if diff >= 0:
                st.success(f"**יתרה חיובית:** ₪{diff:,.0f}")
            else:
                st.error(f"**גירעון:** ₪{abs(diff):,.0f}")
            
        with tab3:
            st.markdown("<h1 style='text-align: center; color: #1f77b4; margin-bottom: 2rem;'>ניהול תורמים</h1>", unsafe_allow_html=True)
            
            # Display donor statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("מספר תורמים", f"{donor_stats['total_donors']:,}")
            with col2:
                st.metric("סך תרומות", f"₪{donor_stats['total_donations']:,.2f}")
            with col3:
                st.metric("תרומה ממוצעת", f"₪{donor_stats['avg_donation']:,.2f}")
            with col4:
                st.metric("תרומה מקסימלית", f"₪{donor_stats['max_donation']:,.2f}")
            
            # Display top donors
            if donor_stats['top_donors']:
                st.subheader("תורמים מובילים")
                top_donors_df = pd.DataFrame(donor_stats['top_donors'])
                st.dataframe(
                    top_donors_df.style.format({
                        'sum': '₪{:,.0f}',
                        'count': '{:,.0f}'
                    }),
                    use_container_width=True
                )
            
            # Display donor contribution chart
            st.subheader("תרומות לפי תורם")
            create_donor_contribution_chart(donations_df)
            
            # Display monthly donations
            st.subheader("תרומות חודשיות")
            monthly_donations = donations_df.groupby(donations_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum().reset_index()
            monthly_donations.columns = ['חודש', 'סכום']
            monthly_donations = monthly_donations.sort_values('חודש', ascending=False)
            st.dataframe(
                monthly_donations.style.format({'סכום': '₪{:,.0f}'}),
                use_container_width=True
            )
            
            # Display editable donations table
            st.subheader("עריכת נתוני תרומות")
            edited_donations = st.data_editor(
                donations_df,
                num_rows="dynamic",
                use_container_width=True,
                column_config=column_config,
                key="donations_donors_editor"
            )
            
            # Check if donations were changed
            if not edited_donations.equals(donations_df):
                st.session_state.changes_made['donations'] = True
            
            # Save edited donations data - only show if there are changes
            if st.session_state.changes_made['donations']:
                if st.button("שמור שינויים", type="primary"):
                    try:
                        with pd.ExcelWriter("omri.xlsx", engine="openpyxl", mode="a") as writer:
                            edited_donations.to_excel(writer, sheet_name="Donations", index=False)
                        
                        # Reset changes flag
                        st.session_state.changes_made['donations'] = False
                        st.success("השינויים נשמרו בהצלחה!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"שגיאה בשמירת השינויים: {str(e)}")
            else:
                st.info("אין שינויים לשמירה")
            
            # Display donations alerts
            st.subheader("התראות תרומות")
            donations_alerts = check_donations_alerts(donor_stats)
            if donations_alerts:
                for alert in donations_alerts:
                    st.warning(alert)
            else:
                st.success("אין התראות תרומות")
            
            # Display detailed donor information
            st.subheader("פרטי תורמים")
            donor_summary = donations_df.groupby("שם").agg({
                "שקלים": ["sum", "count", "mean"],
                "תאריך": ["min", "max"]
            }).reset_index()
            donor_summary.columns = ["שם", "סך תרומות", "מספר תרומות", "תרומה ממוצעת", "תרומה ראשונה", "תרומה אחרונה"]
            
            for _, donor in donor_summary.iterrows():
                with st.expander(f"{donor['שם']} - ₪{donor['סך תרומות']:,.0f}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**סך תרומות:** ₪{donor['סך תרומות']:,.0f}")
                        st.write(f"**מספר תרומות:** {donor['מספר תרומות']}")
                        st.write(f"**תרומה ממוצעת:** ₪{donor['תרומה ממוצעת']:,.0f}")
                    with col2:
                        st.write(f"**תרומה ראשונה:** {donor['תרומה ראשונה'].strftime('%d/%m/%Y')}")
                        st.write(f"**תרומה אחרונה:** {donor['תרומה אחרונה'].strftime('%d/%m/%Y')}")
                    
                    # Display donor's donations history
                    st.subheader("היסטוריית תרומות")
                    donor_history = donations_df[donations_df["שם"] == donor["שם"]].sort_values("תאריך", ascending=False)
                    st.dataframe(
                        donor_history.style.format({
                            "שקלים": "₪{:,.0f}",
                            "תאריך": lambda x: x.strftime("%d/%m/%Y")
                        }),
                        use_container_width=True
                    )
            
        with tab4:
            st.markdown("<h1 style='text-align: center; color: #1f77b4; margin-bottom: 2rem;'>ניהול אלמנות</h1>", unsafe_allow_html=True)
            
            # Display widow statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("מספר אלמנות", f"{widow_stats['total_widows']:,}")
            with col2:
                st.metric("סך תמיכה", f"₪{widow_stats['total_support']:,.2f}")
            with col3:
                st.metric("אלמנות ₪1,000", f"{widow_stats['support_1000_count']}")
            with col4:
                st.metric("אלמנות ₪2,000", f"{widow_stats['support_2000_count']}")
            
            # Display support distribution
            if widow_stats['support_distribution']:
                st.subheader("התפלגות תמיכה")
                support_df = pd.DataFrame([
                    {'שם': k, 'סכום': v}
                    for k, v in widow_stats['support_distribution'].items()
                ])
                st.dataframe(
                    support_df.style.format({'סכום': '₪{:,.0f}'}),
                    use_container_width=True
                )
            
            # Display widows support chart
            st.subheader("תמיכה באלמנות")
            create_widows_support_chart(almanot_df)
            
            # Display 36-month budget projection
            st.subheader("תחזית תקציב ל-36 חודשים")
            # Calculate current monthly support based on actual counts
            current_monthly_support = (widow_stats['support_1000_count'] * 1000) + (widow_stats['support_2000_count'] * 2000)
            budget_projection = calculate_36_month_budget(almanot_df, current_monthly_support)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "תמיכה נדרשת",
                    f"₪{budget_projection['total_required']:,.2f}",
                    f"לחודש: ₪{current_monthly_support:,.2f}"
                )
            with col2:
                st.metric(
                    "תמיכה זמינה",
                    f"₪{budget_projection['support_36_months']:,.2f}",
                    f"אחוז כיסוי: {budget_projection['coverage_percentage']:.1f}%"
                )
            with col3:
                st.metric(
                    "הפרש",
                    f"₪{budget_projection['diff']:,.2f}",
                    f"סטטוס: {budget_projection['status']}"
                )
            
            # Display monthly breakdown
            if budget_projection['monthly_breakdown']:
                st.subheader("פירוט חודשי")
                breakdown_df = pd.DataFrame(budget_projection['monthly_breakdown'])
                st.dataframe(
                    breakdown_df.style.format({
                        'amount': '₪{:,.0f}',
                        'required': '₪{:,.0f}',
                        'difference': '₪{:,.0f}'
                    }),
                    use_container_width=True
                )
            
            # Display monthly support
            st.subheader("תמיכה חודשית")
            if 'חודש התחלה' in almanot_df.columns and 'סכום חודשי' in almanot_df.columns:
                monthly_support = almanot_df.groupby(almanot_df['חודש התחלה'].dt.strftime('%Y-%m'))['סכום חודשי'].sum().reset_index()
                monthly_support.columns = ['חודש', 'סכום']
                monthly_support = monthly_support.sort_values('חודש', ascending=False)
                st.dataframe(
                    monthly_support.style.format({'סכום': '₪{:,.0f}'}),
                    use_container_width=True
                )
            else:
                st.warning("חסרות עמודות נדרשות לתצוגת תמיכה חודשית")
            
            # Display editable widows table
            st.subheader("עריכת נתוני אלמנות")
            
            # Convert phone column to string to avoid type conflicts
            almanot_df_for_edit = almanot_df.copy()
            if 'טלפון' in almanot_df_for_edit.columns:
                almanot_df_for_edit['טלפון'] = almanot_df_for_edit['טלפון'].astype(str)
            
            # Create column config only for existing columns
            column_config = {}
            if "שם " in almanot_df_for_edit.columns:
                column_config["שם "] = st.column_config.TextColumn("שם", required=True)
            if "מייל" in almanot_df_for_edit.columns:
                column_config["מייל"] = st.column_config.TextColumn("מייל")
            if "טלפון" in almanot_df_for_edit.columns:
                column_config["טלפון"] = st.column_config.TextColumn("טלפון")
            if "תעודת זהות" in almanot_df_for_edit.columns:
                column_config["תעודת זהות"] = st.column_config.TextColumn("תעודת זהות")
            if "מספר ילדים" in almanot_df_for_edit.columns:
                column_config["מספר ילדים"] = st.column_config.NumberColumn("מספר ילדים", min_value=0)
            if "חודש התחלה" in almanot_df_for_edit.columns:
                column_config["חודש התחלה"] = st.column_config.DateColumn("חודש התחלה", format="DD/MM/YYYY")
            if "סכום חודשי" in almanot_df_for_edit.columns:
                column_config["סכום חודשי"] = st.column_config.NumberColumn("סכום חודשי", format="₪%d")
            if "חללים" in almanot_df_for_edit.columns:
                column_config["חללים"] = st.column_config.CheckboxColumn("חללים")
            if "הערות" in almanot_df_for_edit.columns:
                column_config["הערות"] = st.column_config.TextColumn("הערות")
            if "תורם" in almanot_df_for_edit.columns:
                column_config["תורם"] = st.column_config.TextColumn("תורם")
            if "איש קשר לתרומה" in almanot_df_for_edit.columns:
                column_config["איש קשר לתרומה"] = st.column_config.TextColumn("איש קשר לתרומה")
            
            edited_almanot = st.data_editor(
                almanot_df_for_edit,
                num_rows="dynamic",
                use_container_width=True,
                column_config=column_config,
                key="widows_widows_editor"
            )
            
            # Check if widows were changed
            if not edited_almanot.equals(almanot_df_for_edit):
                st.session_state.changes_made['widows'] = True
            
            # Save edited widows data - only show if there are changes
            if st.session_state.changes_made['widows']:
                if st.button("שמור שינויים", type="primary"):
                    try:
                        edited_almanot.to_excel("almanot.xlsx", index=False)
                        
                        # Reset changes flag
                        st.session_state.changes_made['widows'] = False
                        st.success("השינויים נשמרו בהצלחה!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"שגיאה בשמירת השינויים: {str(e)}")
            else:
                st.info("אין שינויים לשמירה")
            
            # Display widows alerts
            st.subheader("התראות אלמנות")
            widows_alerts = check_widows_alerts(widow_stats)
            if widows_alerts:
                for alert in widows_alerts:
                    st.warning(alert)
            else:
                st.success("אין התראות אלמנות")
            
            # Display detailed widow information
            st.subheader("פרטי אלמנות")
            for _, widow in almanot_df.iterrows():
                with st.expander(f"{widow['שם ']} - ₪{widow['סכום חודשי']:,.0f}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**מייל:** {widow['מייל']}")
                        st.write(f"**טלפון:** {widow['טלפון']}")
                        st.write(f"**תעודת זהות:** {widow['תעודת זהות']}")
                        st.write(f"**מספר ילדים:** {widow['מספר ילדים']}")
                    with col2:
                        # Handle NaT values in date fields
                        start_date = widow['חודש התחלה']
                        if pd.notna(start_date):
                            st.write(f"**חודש התחלה:** {start_date.strftime('%d/%m/%Y')}")
                        else:
                            st.write(f"**חודש התחלה:** לא מוגדר")
                        
                        st.write(f"**סכום חודשי:** ₪{widow['סכום חודשי']:,.0f}")
                        
                        # Handle checkbox values
                        if 'חללים' in widow and pd.notna(widow['חללים']):
                            st.write(f"**חללים:** {'כן' if widow['חללים'] else 'לא'}")
                        else:
                            st.write(f"**חללים:** לא מוגדר")
                        
                        st.write(f"**תורם:** {widow['תורם']}")
                        st.write(f"**איש קשר לתרומה:** {widow['איש קשר לתרומה']}")
                    
                    if pd.notna(widow['הערות']):
                        st.write(f"**הערות:** {widow['הערות']}")
        
        with tab5:
            st.markdown("<h1 style='text-align: center; color: #1f77b4; margin-bottom: 2rem;'>דוחות</h1>", unsafe_allow_html=True)
            
            # Report Generation Section
            st.markdown("<h2 style='color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem;'>יצירת דוחות</h2>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h3 style='color: #4b5563; margin-bottom: 1rem;'>דוחות מהירים</h3>", unsafe_allow_html=True)
                
                if st.button("📊 דוח חודשי מלא", use_container_width=True):
                    filename = generate_monthly_report(expenses_df, donations_df, almanot_df)
                    if filename:
                        show_success_message("דוח חודשי מלא נוצר בהצלחה!")
                        with open(filename, "rb") as file:
                            st.download_button(
                                label="הורד דוח חודשי",
                                data=file.read(),
                                file_name=filename,
                                mime="application/pdf"
                            )
                
                if st.button("👥 דוח תורמים מפורט", use_container_width=True):
                    filename = generate_donor_report(donations_df)
                    if filename:
                        show_success_message("דוח תורמים מפורט נוצר בהצלחה!")
                        with open(filename, "rb") as file:
                            st.download_button(
                                label="הורד דוח תורמים",
                                data=file.read(),
                                file_name=filename,
                                mime="application/pdf"
                            )
                
                if st.button("👩 דוח אלמנות מפורט", use_container_width=True):
                    filename = generate_widows_report(almanot_df)
                    if filename:
                        show_success_message("דוח אלמנות מפורט נוצר בהצלחה!")
                        with open(filename, "rb") as file:
                            st.download_button(
                                label="הורד דוח אלמנות",
                                data=file.read(),
                                file_name=filename,
                                mime="application/pdf"
                            )
                
                if st.button("💰 דוח תקציב מפורט", use_container_width=True):
                    filename = generate_budget_report(expenses_df, donations_df)
                    if filename:
                        show_success_message("דוח תקציב מפורט נוצר בהצלחה!")
                        with open(filename, "rb") as file:
                            st.download_button(
                                label="הורד דוח תקציב",
                                data=file.read(),
                                file_name=filename,
                                mime="application/pdf"
                            )
            
            with col2:
                st.markdown("<h3 style='color: #4b5563; margin-bottom: 1rem;'>סטטיסטיקות מהירות</h3>", unsafe_allow_html=True)
                
                # Quick stats
                st.metric("סך תרומות", f"₪{total_don:,.0f}")
                st.metric("סך הוצאות", f"₪{sum_exp:,.0f}")
                st.metric("יתרה", f"₪{available:,.0f}")
                st.metric("מספר תורמים", f"{donor_stats['total_donors']:,}")
                st.metric("מספר אלמנות", f"{widow_stats['total_widows']:,}")
                st.metric("תמיכה חודשית", f"₪{widow_stats['total_support']:,.0f}")
            
            # Custom Report Builder
            st.markdown("<h2 style='color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem;'>בניית דוח מותאם</h2>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                report_type = st.selectbox(
                    "סוג דוח",
                    ["דוח חודשי", "דוח תורמים", "דוח אלמנות", "דוח תקציב"]
                )
            
            with col2:
                date_from = st.date_input("מתאריך", value=donations_df['תאריך'].min())
            
            with col3:
                date_to = st.date_input("עד תאריך", value=donations_df['תאריך'].max())
            
            if st.button("יצור דוח מותאם", type="primary"):
                # Filter data by date range
                filtered_donations = donations_df[
                    (donations_df['תאריך'] >= pd.Timestamp(date_from)) & 
                    (donations_df['תאריך'] <= pd.Timestamp(date_to))
                ]
                filtered_expenses = expenses_df[
                    (expenses_df['תאריך'] >= pd.Timestamp(date_from)) & 
                    (expenses_df['תאריך'] <= pd.Timestamp(date_to))
                ]
                
                if report_type == "דוח חודשי":
                    filename = generate_monthly_report(filtered_expenses, filtered_donations, almanot_df)
                elif report_type == "דוח תורמים":
                    filename = generate_donor_report(filtered_donations)
                elif report_type == "דוח אלמנות":
                    filename = generate_widows_report(almanot_df)
                elif report_type == "דוח תקציב":
                    filename = generate_budget_report(filtered_expenses, filtered_donations)
                
                if filename:
                    show_success_message(f"{report_type} נוצר בהצלחה!")
                    with open(filename, "rb") as file:
                        st.download_button(
                            label=f"הורד {report_type}",
                            data=file.read(),
                            file_name=filename,
                            mime="application/pdf"
                        )

        with tab6:
            st.markdown("<h1 style='text-align: center; color: #1f77b4; margin-bottom: 2rem;'>מפת קשרים - תרומות ואלמנות</h1>", unsafe_allow_html=True)
            st.write("מפה אינטראקטיבית: כל אלמנה מחוברת לתורם הגדול ביותר, עם סכום התרומה ותאריך.")
            
            # יצירת גרף קשרים
            net = Network(height="600px", width="100%", bgcolor="#f8f9fa", font_color="#222")
            net.barnes_hut()

            # הוספת תורמים כ-nodes
            donors = donations_df['שם'].unique()
            for donor in donors:
                net.add_node(f"donor_{donor}", label=donor, color="#1f77b4", shape="ellipse", size=30)

            # הוספת אלמנות כ-nodes
            widows = almanot_df['שם '].unique()
            for widow in widows:
                net.add_node(f"widow_{widow}", label=widow, color="#e45756", shape="box", size=20)

            # חיבור כל אלמנה לתורם שונה (הפצה)
            connections_count = 0
            
            # מיון התורמים לפי גודל התרומה
            donor_totals = donations_df.groupby('שם')['שקלים'].sum().sort_values(ascending=False)
            donor_list = donor_totals.index.tolist()
            
            for i, (_, widow_row) in enumerate(almanot_df.iterrows()):
                widow_name = widow_row['שם ']
                
                # בחר תורם לפי האינדקס (הפצה מעגלית)
                if donor_list:
                    donor_index = i % len(donor_list)
                    donor_name = donor_list[donor_index]
                    
                    # חפש את התרומה האחרונה של התורם הזה
                    donor_donations = donations_df[donations_df['שם'] == donor_name]
                    if not donor_donations.empty:
                        last_row = donor_donations.sort_values('תאריך', ascending=False).iloc[0]
                        last_amount = last_row['שקלים']
                        last_date = last_row['תאריך']
                        
                        donation_k = last_amount / 1000
                        edge_width = max(1, min(6, donation_k / 10))
                        
                        if donation_k > 50:
                            edge_color = "#2E8B57"
                        elif donation_k > 20:
                            edge_color = "#32CD32"
                        elif donation_k > 10:
                            edge_color = "#FFD700"
                        else:
                            edge_color = "#D3D3D3"
                        
                        net.add_edge(
                            f"donor_{donor_name}",
                            f"widow_{widow_name}",
                            color=edge_color,
                            width=edge_width,
                            title=f"{donor_name} → {widow_name}: {donation_k:.1f}k ₪ ({last_date.strftime('%d/%m/%Y')})"
                        )
                        connections_count += 1
            
            # הגדרות נוספות לגרף
            net.set_options("""
            var options = {
              "physics": {
                "forceAtlas2Based": {
                  "gravitationalConstant": -50,
                  "centralGravity": 0.01,
                  "springLength": 200,
                  "springConstant": 0.08
                },
                "maxVelocity": 50,
                "minVelocity": 0.1,
                "solver": "forceAtlas2Based",
                "timestep": 0.35
              },
              "edges": {
                "color": {
                  "inherit": false
                },
                "smooth": {
                  "type": "continuous"
                }
              },
              "nodes": {
                "font": {
                  "size": 14,
                  "face": "Arial"
                }
              }
            }
            """)

            # שמירת הגרף כ-HTML זמני
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
                net.save_graph(tmp_file.name)
                html_content = open(tmp_file.name, 'r', encoding='utf-8').read()
                components.html(html_content, height=650, scrolling=True)
            
            # מידע על הגרף
            st.info(f"📊 **מידע על הגרף**: מוצגים {connections_count} קשרים מתוך {len(donors)} תורמים ו-{len(widows)} אלמנות")
            
            # הסבר על הצבעים
            st.markdown("### הסבר על הצבעים:")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown("🟢 **ירוק כהה**: תרומות מעל 50k ₪")
            with col2:
                st.markdown("🟢 **ירוק**: תרומות 20-50k ₪")
            with col3:
                st.markdown("🟡 **צהוב**: תרומות 10-20k ₪")
            with col4:
                st.markdown("⚪ **אפור**: תרומות מתחת ל-10k ₪")
            
            st.info("💡 **טיפ**: העבר את העכבר מעל הקשתות כדי לראות את גודל התרומה המדויק.")
        
    except Exception as e:
        logging.error(f"Error in main function: {str(e)}")
        logging.error(traceback.format_exc())
        st.error("שגיאה בהצגת הדשבורד. אנא נסה לרענן את הדף.")

if __name__ == "__main__":
    main()