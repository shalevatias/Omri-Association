import streamlit as st
from utils import format_currency
import pandas as pd

def validate_data(df, name):
    """Validate data in a DataFrame"""
    errors = []
    
    # Check for missing values
    if df['שקלים'].isnull().any():
        errors.append(f"חסרים ערכים בעמודת סכומים ב{name}")
    
    if df['תאריך'].isnull().any():
        errors.append(f"חסרים ערכים בעמודת תאריכים ב{name}")
    
    # Check for negative values
    if (df['שקלים'] < 0).any():
        errors.append(f"נמצאו ערכים שליליים בעמודת סכומים ב{name}")
    
    return errors

def validate_widows_data(df):
    """Validate widows data"""
    errors = []
    
    # Check for missing values
    if df['סכום חודשי'].isnull().any():
        errors.append("חסרים ערכים בעמודת סכום חודשי באלמנות")
    
    # Check for negative values
    if (df['סכום חודשי'] < 0).any():
        errors.append("נמצאו ערכים שליליים בעמודת סכום חודשי באלמנות")
    
    return errors

def validate_donations_data(donations_df):
    errors = []
    try:
        if donations_df['שקלים'].isnull().any():
            errors.append("חסרים ערכים בעמודת שקלים בתרומות")
        if (donations_df['שקלים'] < 0).any():
            errors.append("נמצאו ערכים שליליים בעמודת שקלים בתרומות")
    except Exception as e:
        errors.append(f"שגיאה בבדיקת נתוני תרומות: {str(e)}")
    return errors

def validate_expenses_data(expenses_df):
    errors = []
    try:
        if expenses_df['שקלים'].isnull().any():
            errors.append("חסרים ערכים בעמודת שקלים בהוצאות")
        if (expenses_df['שקלים'] < 0).any():
            errors.append("נמצאו ערכים שליליים בעמודת שקלים בהוצאות")
    except Exception as e:
        errors.append(f"שגיאה בבדיקת נתוני הוצאות: {str(e)}")
    return errors

def check_budget_alerts(expenses_df, donations_df):
    alerts = []
    try:
        monthly_expenses = expenses_df.groupby(expenses_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum()
        monthly_donations = donations_df.groupby(donations_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum()
        
        # Check for monthly drops in donations
        prev_month_donation = None
        for month in sorted(monthly_donations.index):
            if prev_month_donation is not None:
                drop_percentage = (prev_month_donation - monthly_donations[month]) / prev_month_donation * 100
                if drop_percentage > 30:
                    alerts.append({
                        'type': 'donation_drop',
                        'month': month,
                        'message': f"⚠️ ירידה של {drop_percentage:.1f}% בתרומות בחודש {month}"
                    })
            prev_month_donation = monthly_donations[month]
        
        # Check for budget overruns
        for month in monthly_expenses.index:
            if month in monthly_donations.index:
                if monthly_expenses[month] > monthly_donations[month]:
                    alerts.append({
                        'type': 'budget_overrun',
                        'month': month,
                        'message': f"⚠️ חריגת תקציב בחודש {month}: הוצאות {format_currency(monthly_expenses[month])} לעומת תרומות {format_currency(monthly_donations[month])}"
                    })
    except Exception as e:
        st.error(f"שגיאה בבדיקת התראות תקציב: {str(e)}")
    return alerts 