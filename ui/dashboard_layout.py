#!/usr/bin/env python3
"""
Dashboard Layout Module
Handles the main dashboard structure, tabs, and layout
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

def create_main_tabs():
    """Create the main tab structure"""
    return st.tabs(["🏠 דף הבית", "🕸️ מפת קשרים", "⚙️ הגדרות", "📊 ניטור", "🧪 בדיקות"])

def create_dashboard_header():
    """Create the main dashboard header with refresh button and system status"""
    # Main title
    st.markdown("<h1 style='text-align: center; color: #1f77b4; margin-bottom: 1rem;'>מערכת ניהול עמותת עמרי</h1>", unsafe_allow_html=True)
    
    # System status and refresh section
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown("**מערכת פעילה** ✅")
    
    with col2:
        if st.button("🔄 רענן נתונים", use_container_width=True):
            # Clear session state to force data reload
            if 'expenses_df' in st.session_state:
                del st.session_state.expenses_df
            if 'donations_df' in st.session_state:
                del st.session_state.donations_df
            if 'almanot_df' in st.session_state:
                del st.session_state.almanot_df
            if 'investors_df' in st.session_state:
                del st.session_state.investors_df
            st.rerun()
    
    with col3:
        # Show last update time
        if 'last_update' not in st.session_state:
            st.session_state.last_update = pd.Timestamp.now()
        
        st.markdown(f"**עודכן לאחרונה:** {st.session_state.last_update.strftime('%H:%M')}")
    
    with col4:
        # Show data status
        if ('expenses_df' in st.session_state and 'donations_df' in st.session_state and 
            'almanot_df' in st.session_state and 'investors_df' in st.session_state):
            st.markdown("**נתונים:** ✅")
        else:
            st.markdown("**נתונים:** ⏳")
    
    # Quick theme toggle
    try:
        from theme_manager import get_current_theme, switch_theme
        current_theme = get_current_theme()
        
        if st.button("🌙" if current_theme == 'light' else "☀️", 
                    help="החלף עיצוב"):
            new_theme = 'dark' if current_theme == 'light' else 'light'
            switch_theme(new_theme)
            st.rerun()
    except ImportError:
        pass  # Theme manager not available
    
    add_spacing(1)

def create_section_header(title: str, icon: str = ""):
    """Create a consistent section header"""
    icon_text = f"{icon} " if icon else ""
    st.markdown(f"<h2 style='color: #000000; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem; margin-bottom: 2rem;'>{icon_text}{title}</h2>", unsafe_allow_html=True)

def create_metric_row(metrics: list, columns: int = 4):
    """Create a row of metrics with specified number of columns"""
    cols = st.columns(columns)
    for i, metric in enumerate(metrics):
        if i < len(cols):
            with cols[i]:
                st.metric(metric['label'], metric['value'], metric.get('delta', None), help=metric.get('help', None))
    return cols

def create_two_column_layout():
    """Create a two-column layout"""
    return st.columns(2)

def create_three_column_layout():
    """Create a three-column layout"""
    return st.columns(3)

def add_spacing(rem: float = 2):
    """Add consistent spacing between sections"""
    st.markdown(f"<div style='margin: {rem}rem 0;'></div>", unsafe_allow_html=True)

def create_recent_activity_section(expenses_df: pd.DataFrame, donations_df: pd.DataFrame):
    """Create the recent activity section"""
    col1, col2 = create_two_column_layout()
    
    with col1:
        st.markdown("<h4>🎁 תרומות אחרונות</h4>", unsafe_allow_html=True)
        try:
            recent_donations = donations_df.sort_values('תאריך', ascending=False).head(5)
            if len(recent_donations) > 0:
                for _, donation in recent_donations.iterrows():
                    donation_date = donation['תאריך']
                    if pd.notna(donation_date):
                        st.write(f"**{donation['שם']}** - ₪{donation['שקלים']:,.0f} ({donation_date.strftime('%d/%m/%Y')})")
                    else:
                        st.write(f"**{donation['שם']}** - ₪{donation['שקלים']:,.0f} (תאריך לא מוגדר)")
            else:
                st.info("אין תרומות להצגה")
        except Exception as e:
            st.error("שגיאה בטעינת תרומות אחרונות")
    
    with col2:
        st.markdown("<h4>💸 הוצאות אחרונות</h4>", unsafe_allow_html=True)
        try:
            recent_expenses = expenses_df.sort_values('תאריך', ascending=False).head(5)
            if len(recent_expenses) > 0:
                for _, expense in recent_expenses.iterrows():
                    expense_date = expense['תאריך']
                    if pd.notna(expense_date):
                        st.write(f"**{expense['שם']}** - ₪{expense['שקלים']:,.0f} ({expense_date.strftime('%d/%m/%Y')})")
                    else:
                        st.write(f"**{expense['שם']}** - ₪{expense['שקלים']:,.0f} (תאריך לא מוגדר)")
            else:
                st.info("אין הוצאות להצגה")
        except Exception as e:
            st.error("שגיאה בטעינת הוצאות אחרונות")

def create_reports_section(expenses_df: pd.DataFrame, donations_df: pd.DataFrame, almanot_df: pd.DataFrame):
    """Create the reports section"""
    create_section_header("📋 דוחות")
    
    col1, col2 = create_two_column_layout()
    
    with col1:
        if st.button("📊 דוח חודשי מפורט", use_container_width=True):
            try:
                from reports.reports import generate_monthly_report
                filename = generate_monthly_report(expenses_df, donations_df, almanot_df)
                if filename:
                    with open(filename, "rb") as file:
                        st.download_button(
                            label="הורד דוח חודשי",
                            data=file.read(),
                            file_name=filename,
                            mime="application/pdf"
                        )
            except Exception as e:
                st.error("שגיאה ביצירת דוח חודשי")
        
        if st.button("👥 דוח תורמים מפורט", use_container_width=True):
            try:
                from reports.reports import generate_donor_report
                filename = generate_donor_report(donations_df)
                if filename:
                    with open(filename, "rb") as file:
                        st.download_button(
                            label="הורד דוח תורמים",
                            data=file.read(),
                            file_name=filename,
                            mime="application/pdf"
                        )
            except Exception as e:
                st.error("שגיאה ביצירת דוח תורמים")
    
    with col2:
        if st.button("👩 דוח אלמנות מפורט", use_container_width=True):
            try:
                from reports.reports import generate_widows_report
                filename = generate_widows_report(almanot_df)
                if filename:
                    with open(filename, "rb") as file:
                        st.download_button(
                            label="הורד דוח אלמנות",
                            data=file.read(),
                            file_name=filename,
                            mime="application/pdf"
                        )
            except Exception as e:
                st.error("שגיאה ביצירת דוח אלמנות")
        
        if st.button("💰 דוח תקציב מפורט", use_container_width=True):
            try:
                from reports.reports import generate_budget_report
                filename = generate_budget_report(expenses_df, donations_df)
                if filename:
                    with open(filename, "rb") as file:
                        st.download_button(
                            label="הורד דוח תקציב",
                            data=file.read(),
                            file_name=filename,
                            mime="application/pdf"
                        )
            except Exception as e:
                st.error("שגיאה ביצירת דוח תקציב")
