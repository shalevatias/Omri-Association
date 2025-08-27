import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import logging

def check_budget_alerts(budget_status: dict, donations_df: pd.DataFrame = None) -> List[str]:
    """Check for budget-related alerts"""
    alerts = []
    try:
        if not isinstance(budget_status, dict):
            return alerts
            
        # Check utilization percentage
        utilization_percentage = budget_status.get('utilization_percentage', 0)
        if utilization_percentage > 90:
            alerts.append(f"אחוז ניצול גבוה: {utilization_percentage:.1f}%")
        elif utilization_percentage > 80:
            alerts.append(f"אחוז ניצול טוב: {utilization_percentage:.1f}%")
        elif utilization_percentage < 30:
            alerts.append(f"אחוז ניצול נמוך: {utilization_percentage:.1f}%")
            
        # Check balance
        balance = budget_status.get('balance', 0)
        if balance < 0:
            alerts.append(f"יתרה שלילית: ₪{balance:,.0f}")
        elif balance > 100000:
            alerts.append(f"יתרה חיובית גבוהה: ₪{balance:,.0f}")
            
        # Check status
        status = budget_status.get('status', '')
        if status in ['דורש תשומת לב', 'חסר']:
            alerts.append(f"סטטוס תקציב: {status}")
            
    except Exception as e:
        logging.error(f"Error checking budget alerts: {str(e)}")
        
    return alerts

def check_data_quality_alerts(expenses_df: pd.DataFrame, donations_df: pd.DataFrame, widows_df: pd.DataFrame) -> List[str]:
    """Check for data quality issues"""
    alerts = []
    try:
        # Check each dataframe
        for df, name, amount_col in [
            (expenses_df, 'הוצאות', 'שקלים'),
            (donations_df, 'תרומות', 'שקלים'),
            (widows_df, 'אלמנות', 'סכום חודשי')
        ]:
            if not isinstance(df, pd.DataFrame):
                alerts.append(f"נתוני {name} לא תקינים")
                continue
                
            # Check for missing values - but be more specific about what constitutes "missing"
            if amount_col in df.columns:
                null_count = df[amount_col].isnull().sum()
                empty_count = (df[amount_col] == '').sum() if amount_col in df.columns else 0
                total_count = len(df)
                
                # Skip alert for monthly amounts - we treat missing as 0
                if amount_col == 'סכום חודשי':
                    logging.info(f"Monthly amounts: {null_count}/{total_count} missing values (treated as 0)")
                    continue
                
                # Only alert if there are significant missing values (more than 10% of rows)
                if null_count > 0 and (null_count / total_count) > 0.1:
                    alerts.append(f"חסרים ערכים בעמודת {amount_col} בקובץ {name} ({null_count}/{total_count} שורות)")
                elif null_count > 0:
                    # Just log for debugging, don't show as alert
                    logging.info(f"Minor missing values in {amount_col} column of {name}: {null_count}/{total_count}")
                
            # Check for negative values only (not zero)
            if amount_col in df.columns and (df[amount_col] < 0).any():
                alerts.append(f"נמצאו ערכים שליליים בעמודת {amount_col} בקובץ {name}")
                
    except Exception as e:
        logging.error(f"Error checking data quality alerts: {str(e)}")
        
    return alerts

def check_widows_alerts(widow_stats: dict) -> List[str]:
    """Check for widow-related alerts"""
    alerts = []
    try:
        if not isinstance(widow_stats, dict):
            return alerts
            
        total_widows = widow_stats.get('total_widows', 0)
        support_1000_count = widow_stats.get('support_1000_count', 0)
        support_2000_count = widow_stats.get('support_2000_count', 0)
        
        if total_widows == 0:
            alerts.append("אין נתוני אלמנות")
        elif support_1000_count == 0 and support_2000_count == 0:
            alerts.append("אין אלמנות עם תמיכה מוגדרת")
        elif support_1000_count > 0 and support_2000_count == 0:
            alerts.append("כל האלמנות מקבלות תמיכה של ₪1,000 בלבד")
        elif support_2000_count > 0 and support_1000_count == 0:
            alerts.append("כל האלמנות מקבלות תמיכה של ₪2,000 בלבד")
            
    except Exception as e:
        logging.error(f"Error checking widows alerts: {str(e)}")
        
    return alerts

def check_donations_alerts(donor_stats: dict) -> List[str]:
    """Check for donation-specific alerts"""
    alerts = []
    try:
        if not isinstance(donor_stats, dict):
            return alerts
            
        total_donations = donor_stats.get('total_donations', 0)
        avg_donation = donor_stats.get('avg_donation', 0)
        
        if total_donations == 0:
            alerts.append("אין נתוני תרומות")
        elif avg_donation < 500:
            alerts.append(f"תרומה ממוצעת נמוכה: ₪{avg_donation:,.0f}")
        elif avg_donation > 100000:
            alerts.append(f"תרומה ממוצעת גבוהה מאוד: ₪{avg_donation:,.0f}")
        elif avg_donation >= 5000:
            alerts.append(f"תרומה ממוצעת טובה: ₪{avg_donation:,.0f}")
            
    except Exception as e:
        logging.error(f"Error checking donations alerts: {str(e)}")
        
    return alerts

def display_alerts(alerts: List[str]) -> None:
    """Display alerts in the sidebar"""
    if not alerts:
        st.sidebar.success("אין התראות")
        return
        
    for alert in alerts:
        if "שגיאה" in alert or "קריטי" in alert:
            st.sidebar.error(alert)
        elif "אזהרה" in alert or "נמוך" in alert or "גבוה" in alert:
            st.sidebar.warning(alert)
        else:
            st.sidebar.info(alert) 