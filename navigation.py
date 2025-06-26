import streamlit as st
import pandas as pd
import logging
import traceback
from data_visualization import (
    create_monthly_trends,
    create_budget_distribution_chart,
    create_widows_support_chart,
    create_donor_contribution_chart,
    create_comparison_chart
)
from data_processing import (
    calculate_monthly_averages,
    calculate_total_support,
    calculate_monthly_budget,
    calculate_donor_statistics,
    calculate_expense_statistics,
    calculate_widow_statistics,
    calculate_monthly_trends
)
from reports import (
    generate_monthly_report,
    generate_widows_report,
    generate_donor_report,
    generate_budget_report
)
from utils import format_currency

def show_navigation(expenses_df, donations_df, widows_df):
    """Show navigation sidebar and handle page selection"""
    try:
        st.sidebar.title("ניווט")
        page = st.sidebar.radio(
            "בחר דף",
            ["דף הבית", "ניהול תמיכה", "ניהול תרומות", "ניהול הוצאות", "דוחות", "הגדרות"]
        )
        
        if page == "דף הבית":
            show_home_page(expenses_df, donations_df, widows_df)
        elif page == "ניהול תמיכה":
            show_support_management_page(widows_df)
        elif page == "ניהול תרומות":
            show_donations_management_page(donations_df)
        elif page == "ניהול הוצאות":
            show_expenses_management_page(expenses_df)
        elif page == "דוחות":
            show_reports_page(expenses_df, donations_df, widows_df)
        elif page == "הגדרות":
            show_settings_page()
            
    except Exception as e:
        logging.error(f"Error in navigation: {str(e)}")
        logging.error(traceback.format_exc())
        st.error("שגיאה בניווט. אנא נסה שוב.")

def show_home_page(expenses_df, donations_df, widows_df):
    """Show home page with key metrics and charts"""
    try:
        st.title("דשבורד - עמותת עמרי")
        
        # Calculate key metrics
        monthly_avg_expenses = calculate_monthly_averages(expenses_df, 'שקלים')
        monthly_avg_donations = calculate_monthly_averages(donations_df, 'סכום חודשי')
        total_support = calculate_total_support(widows_df, 'סכום חודשי')
        
        # Display metrics in cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>ממוצע הוצאות חודשי</h3>
                <h2>₪{:,}</h2>
            </div>
            """.format(int(monthly_avg_expenses)), unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>ממוצע תרומות חודשי</h3>
                <h2>₪{:,}</h2>
            </div>
            """.format(int(monthly_avg_donations)), unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>סה״כ תמיכה באלמנות</h3>
                <h2>₪{:,}</h2>
            </div>
            """.format(int(total_support)), unsafe_allow_html=True)
        
        # Display charts
        st.subheader("מגמות חודשיות")
        create_monthly_trends(expenses_df, donations_df)
        
        # הסרת הגרפים הכפולים - הם כבר מופיעים ב-dashboard.py
        # st.subheader("השוואת הוצאות ותרומות")
        # create_comparison_chart(expenses_df, donations_df)
        
        # st.subheader("התפלגות תקציב")
        # create_budget_distribution_chart(expenses_df)
        
    except Exception as e:
        logging.error(f"Error in home page: {str(e)}")
        logging.error(traceback.format_exc())
        st.error("שגיאה בטעינת דף הבית. אנא נסה שוב.")

def show_support_management_page(widows_df):
    """Show widows support management page"""
    try:
        st.title("ניהול תמיכה באלמנות")
        
        # Calculate statistics
        stats = calculate_widow_statistics(widows_df, 'סכום חודשי')
        
        # Display statistics in cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>מספר אלמנות</h3>
                <h2>{:,}</h2>
            </div>
            """.format(stats['total_widows']), unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>סכום תמיכה ממוצע</h3>
                <h2>₪{:,}</h2>
            </div>
            """.format(int(stats['avg_support'])), unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>סה״כ תמיכה</h3>
                <h2>₪{:,}</h2>
            </div>
            """.format(int(stats['total_support'])), unsafe_allow_html=True)
        
        # Display chart
        st.subheader("תמיכה באלמנות")
        # הסרת הגרף הכפול - הוא כבר מופיע ב-dashboard.py
        # create_widows_support_chart(widows_df)
        
        # Display data
        st.subheader("נתוני תמיכה")
        st.dataframe(widows_df)
        
    except Exception as e:
        logging.error(f"Error in support management page: {str(e)}")
        logging.error(traceback.format_exc())
        st.error("שגיאה בטעינת דף ניהול התמיכה. אנא נסה שוב.")

def show_donations_management_page(donations_df):
    """Show donations management page"""
    try:
        st.title("ניהול תרומות")
        
        # Calculate statistics
        stats = calculate_donor_statistics(donations_df, 'סכום חודשי')
        
        # Display statistics in cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>מספר תורמים</h3>
                <h2>{:,}</h2>
            </div>
            """.format(stats['total_donors']), unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>סכום תרומה ממוצע</h3>
                <h2>₪{:,}</h2>
            </div>
            """.format(int(stats['avg_donation'])), unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>סה״כ תרומות</h3>
                <h2>₪{:,}</h2>
            </div>
            """.format(int(stats['total_donations'])), unsafe_allow_html=True)
        
        # Display chart
        st.subheader("תרומות לפי תורם")
        # הסרת הגרף הכפול - הוא כבר מופיע ב-dashboard.py
        # create_donor_contribution_chart(donations_df)
        
        # Display data
        st.subheader("נתוני תרומות")
        st.dataframe(donations_df)
        
    except Exception as e:
        logging.error(f"Error in donations management page: {str(e)}")
        logging.error(traceback.format_exc())
        st.error("שגיאה בטעינת דף ניהול התרומות. אנא נסה שוב.")

def show_expenses_management_page(expenses_df):
    """Show expenses management page"""
    try:
        st.title("ניהול הוצאות")
        
        # Calculate statistics
        stats = calculate_expense_statistics(expenses_df, 'שקלים')
        
        # Display statistics in cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>מספר הוצאות</h3>
                <h2>{:,}</h2>
            </div>
            """.format(stats['total_expenses']), unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>סכום הוצאה ממוצע</h3>
                <h2>₪{:,}</h2>
            </div>
            """.format(int(stats['avg_expense'])), unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>סה״כ הוצאות</h3>
                <h2>₪{:,}</h2>
            </div>
            """.format(int(stats['total_expenses'])), unsafe_allow_html=True)
        
        # Display chart
        st.subheader("התפלגות הוצאות")
        # הסרת הגרף הכפול - הוא כבר מופיע ב-dashboard.py
        # create_budget_distribution_chart(expenses_df)
        
        # Display data
        st.subheader("נתוני הוצאות")
        st.dataframe(expenses_df)
        
    except Exception as e:
        logging.error(f"Error in expenses management page: {str(e)}")
        logging.error(traceback.format_exc())
        st.error("שגיאה בטעינת דף ניהול ההוצאות. אנא נסה שוב.")

def show_reports_page(expenses_df, donations_df, widows_df):
    """Show reports page"""
    try:
        st.title("דוחות")
        
        # Create tabs for different reports
        tab1, tab2, tab3, tab4 = st.tabs(["דוח חודשי", "דוח אלמנות", "דוח תורמים", "דוח תקציב"])
        
        with tab1:
            st.subheader("דוח חודשי")
            if st.button("צור דוח חודשי"):
                report_file = generate_monthly_report(expenses_df, donations_df, widows_df)
                if report_file:
                    st.success(f"הדוח נוצר בהצלחה: {report_file}")
        
        with tab2:
            st.subheader("דוח אלמנות")
            if st.button("צור דוח אלמנות"):
                report_file = generate_widows_report(widows_df)
                if report_file:
                    st.success(f"הדוח נוצר בהצלחה: {report_file}")
        
        with tab3:
            st.subheader("דוח תורמים")
            if st.button("צור דוח תורמים"):
                report_file = generate_donor_report(donations_df)
                if report_file:
                    st.success(f"הדוח נוצר בהצלחה: {report_file}")
        
        with tab4:
            st.subheader("דוח תקציב")
            if st.button("צור דוח תקציב"):
                report_file = generate_budget_report(expenses_df, donations_df)
                if report_file:
                    st.success(f"הדוח נוצר בהצלחה: {report_file}")
            
    except Exception as e:
        logging.error(f"Error in reports page: {str(e)}")
        logging.error(traceback.format_exc())
        st.error("שגיאה בטעינת דף הדוחות. אנא נסה שוב.")

def show_settings_page():
    """Show settings page"""
    try:
        st.title("הגדרות")
        
        st.subheader("הגדרות מערכת")
        
        # Add settings options here
        st.write("הגדרות מערכת יופיעו כאן")
        
    except Exception as e:
        logging.error(f"Error in settings page: {str(e)}")
        logging.error(traceback.format_exc())
        st.error("שגיאה בטעינת דף ההגדרות. אנא נסה שוב.") 