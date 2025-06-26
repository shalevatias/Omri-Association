import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import logging
import traceback

def calculate_monthly_averages(df: pd.DataFrame, value_column: str = 'שקלים') -> dict:
    """Calculate monthly averages and statistics"""
    if not isinstance(df, pd.DataFrame) or value_column not in df.columns or df.empty:
        return {
            'monthly_avg': 0,
            'min_monthly': 0,
            'max_monthly': 0,
            'total_months': 0
        }
    try:
        # Group by month and calculate totals
        monthly_totals = df.groupby(df['תאריך'].dt.strftime('%Y-%m'))[value_column].sum()
        
        # Calculate statistics
        monthly_avg = monthly_totals.mean() if len(monthly_totals) > 0 else 0
        min_monthly = monthly_totals.min() if len(monthly_totals) > 0 else 0
        max_monthly = monthly_totals.max() if len(monthly_totals) > 0 else 0
        total_months = len(monthly_totals)
        
        return {
            'monthly_avg': monthly_avg,
            'min_monthly': min_monthly,
            'max_monthly': max_monthly,
            'total_months': total_months
        }
    except Exception as e:
        logging.error(f"Error calculating monthly averages: {str(e)}")
        return {
            'monthly_avg': 0,
            'min_monthly': 0,
            'max_monthly': 0,
            'total_months': 0
        }

def calculate_total_support(df: pd.DataFrame, value_column: str = 'סכום חודשי') -> dict:
    """Calculate total support statistics"""
    if not isinstance(df, pd.DataFrame) or value_column not in df.columns or df.empty:
        return {
            'total_support': 0,
            'avg_support': 0,
            'min_support': 0,
            'max_support': 0,
            'support_count': 0
        }
    try:
        # Calculate statistics
        total_support = df[value_column].sum()
        avg_support = total_support / len(df) if len(df) > 0 else 0
        min_support = float(df[value_column].min())
        max_support = float(df[value_column].max())
        support_count = len(df)
        
        return {
            'total_support': total_support,
            'avg_support': avg_support,
            'min_support': min_support,
            'max_support': max_support,
            'support_count': support_count
        }
    except Exception as e:
        logging.error(f"Error calculating total support: {str(e)}")
        return {
            'total_support': 0,
            'avg_support': 0,
            'min_support': 0,
            'max_support': 0,
            'support_count': 0
        }

def calculate_monthly_budget(expenses_df: pd.DataFrame, donations_df: pd.DataFrame) -> dict:
    """Calculate monthly budget statistics"""
    try:
        if not isinstance(expenses_df, pd.DataFrame) or not isinstance(donations_df, pd.DataFrame):
            raise ValueError("הנתונים חייבים להיות DataFrame")
            
        # Calculate total expenses
        total_expenses = expenses_df['שקלים'].sum() if 'שקלים' in expenses_df.columns else 0
        
        # Calculate total donations
        total_donations = donations_df['שקלים'].sum() if 'שקלים' in donations_df.columns else 0
        
        # Calculate balance
        balance = total_donations - total_expenses
        
        # Calculate monthly averages
        monthly_expenses = expenses_df.groupby(expenses_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum()
        monthly_donations = donations_df.groupby(donations_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum()
        
        # Calculate coverage ratio
        coverage_ratio = (total_donations / total_expenses * 100) if total_expenses > 0 else 0
        
        # Determine status based on balance (surplus/deficit) instead of coverage ratio
        if balance >= 0:
            # Surplus or balanced
            if balance >= total_expenses * 0.2:  # 20% surplus
                status = "מצוין"
            elif balance >= total_expenses * 0.1:  # 10% surplus
                status = "טוב"
            else:
                status = "מספק"
        else:
            # Deficit
            deficit_ratio = abs(balance) / total_expenses if total_expenses > 0 else 0
            if deficit_ratio <= 0.1:  # Deficit up to 10%
                status = "דורש תשומת לב"
            elif deficit_ratio <= 0.25:  # Deficit up to 25%
                status = "קריטי"
            else:  # Deficit over 25%
                status = "מצב חירום"
            
        return {
            'total_expenses': total_expenses,
            'total_donations': total_donations,
            'balance': balance,
            'coverage_ratio': coverage_ratio,
            'status': status,
            'monthly_expenses': monthly_expenses.to_dict(),
            'monthly_donations': monthly_donations.to_dict()
        }
        
    except Exception as e:
        logging.error(f"Error calculating monthly budget: {str(e)}")
        return {
            'total_expenses': 0,
            'total_donations': 0,
            'balance': 0,
            'coverage_ratio': 0,
            'status': "שגיאה",
            'monthly_expenses': {},
            'monthly_donations': {}
        }

def calculate_donor_statistics(df: pd.DataFrame, value_column: str = 'שקלים') -> dict:
    """Calculate donor statistics"""
    if not isinstance(df, pd.DataFrame) or value_column not in df.columns or df.empty:
        return {
            'total_donors': 0,
            'total_donations': 0,
            'avg_donation': 0,
            'min_donation': 0,
            'max_donation': 0,
            'top_donors': []
        }
    try:
        # Basic statistics
        total_donors = df['שם'].nunique() if 'שם' in df.columns else 0
        total_donations = df[value_column].sum()
        avg_donation = total_donations / total_donors if total_donors > 0 else 0
        
        # Top donors
        if 'שם' in df.columns:
            top_donors = df.groupby('שם')[value_column].agg(['sum', 'count']).sort_values('sum', ascending=False).head(10)
            top_donors = top_donors.reset_index()
            top_donors.columns = ['name', 'sum', 'count']
            top_donors = top_donors.to_dict('records')
        else:
            top_donors = []
        
        return {
            'total_donors': total_donors,
            'total_donations': total_donations,
            'avg_donation': avg_donation,
            'min_donation': float(df[value_column].min()),
            'max_donation': float(df[value_column].max()),
            'top_donors': top_donors
        }
    except Exception as e:
        logging.error(f"Error calculating donor statistics: {str(e)}")
        return {
            'total_donors': 0,
            'total_donations': 0,
            'avg_donation': 0,
            'min_donation': 0,
            'max_donation': 0,
            'top_donors': []
        }

def calculate_expense_statistics(df: pd.DataFrame, value_column: str = 'שקלים') -> dict:
    """Calculate expense statistics with detailed analysis"""
    if not isinstance(df, pd.DataFrame) or value_column not in df.columns or df.empty:
        return {
            'total_expenses': 0,
            'avg_expense': 0,
            'min_expense': 0,
            'max_expense': 0,
            'expense_categories': {},
            'monthly_expenses': []
        }
    try:
        # Basic statistics
        total_expenses = df[value_column].sum()
        avg_expense = total_expenses / len(df) if len(df) > 0 else 0
        
        # Expense categories
        if 'שם' in df.columns:
            expense_categories = df.groupby('שם')[value_column].sum().sort_values(ascending=False)
            expense_categories = expense_categories.to_dict()
        else:
            expense_categories = {}
        
        # Monthly expenses
        if 'תאריך' in df.columns:
            df['תאריך'] = pd.to_datetime(df['תאריך'], format='%d.%m.%Y', errors='coerce')
            monthly_expenses = df.groupby(df['תאריך'].dt.strftime('%Y-%m'))[value_column].sum()
            monthly_expenses = monthly_expenses.to_dict()
        else:
            monthly_expenses = {}
        
        return {
            'total_expenses': total_expenses,
            'avg_expense': avg_expense,
            'min_expense': float(df[value_column].min()),
            'max_expense': float(df[value_column].max()),
            'expense_categories': expense_categories,
            'monthly_expenses': monthly_expenses
        }
    except Exception as e:
        logging.error(f"Error calculating expense statistics: {str(e)}")
        return {
            'total_expenses': 0,
            'avg_expense': 0,
            'min_expense': 0,
            'max_expense': 0,
            'expense_categories': {},
            'monthly_expenses': []
        }

def calculate_widow_statistics(df: pd.DataFrame, value_column: str = 'סכום חודשי') -> dict:
    """Calculate widow statistics with detailed analysis"""
    if not isinstance(df, pd.DataFrame) or value_column not in df.columns or df.empty:
        return {
            'total_widows': 0,
            'total_support': 0,
            'support_1000_count': 0,
            'support_2000_count': 0,
            'support_distribution': {},
            'monthly_support': []
        }
    try:
        # Basic statistics
        total_widows = df['שם '].nunique() if 'שם ' in df.columns else 0
        total_support = df[value_column].sum()
        
        # Count widows by support amount (only 1000 or 2000)
        support_1000_count = int((df[value_column] == 1000).sum())
        support_2000_count = int((df[value_column] == 2000).sum())
        
        # Support distribution
        if 'שם ' in df.columns:
            support_distribution = df.groupby('שם ')[value_column].sum().sort_values(ascending=False)
            support_distribution = support_distribution.to_dict()
        else:
            support_distribution = {}
        
        # Monthly support
        if 'חודש התחלה' in df.columns:
            df['חודש התחלה'] = pd.to_datetime(df['חודש התחלה'], format='%d.%m.%Y', errors='coerce')
            monthly_support = df.groupby(df['חודש התחלה'].dt.strftime('%Y-%m'))[value_column].sum()
            monthly_support = monthly_support.to_dict()
        else:
            monthly_support = {}
        
        return {
            'total_widows': total_widows,
            'total_support': total_support,
            'support_1000_count': support_1000_count,
            'support_2000_count': support_2000_count,
            'support_distribution': support_distribution,
            'monthly_support': monthly_support
        }
    except Exception as e:
        logging.error(f"Error calculating widow statistics: {str(e)}")
        return {
            'total_widows': 0,
            'total_support': 0,
            'support_1000_count': 0,
            'support_2000_count': 0,
            'support_distribution': {},
            'monthly_support': []
        }

def calculate_monthly_trends(expenses_df: pd.DataFrame, donations_df: pd.DataFrame) -> dict:
    """Calculate monthly trends for expenses and donations"""
    try:
        if not isinstance(expenses_df, pd.DataFrame) or not isinstance(donations_df, pd.DataFrame):
            raise ValueError("הנתונים חייבים להיות DataFrame")
            
        # Calculate monthly trends for expenses
        if 'תאריך' in expenses_df.columns and 'שקלים' in expenses_df.columns:
            expenses_df['תאריך'] = pd.to_datetime(expenses_df['תאריך'], format='%d.%m.%Y', errors='coerce')
            monthly_expenses = expenses_df.groupby(expenses_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum()
            
            # Calculate trend and change
            if len(monthly_expenses) > 1:
                expenses_trend = "עולה" if monthly_expenses.iloc[-1] > monthly_expenses.iloc[0] else "יורד"
                expenses_change = ((monthly_expenses.iloc[-1] - monthly_expenses.iloc[0]) / monthly_expenses.iloc[0] * 100) if monthly_expenses.iloc[0] != 0 else 0
            else:
                expenses_trend = "יציב"
                expenses_change = 0
        else:
            monthly_expenses = pd.Series()
            expenses_trend = "לא ניתן לחשב"
            expenses_change = 0
            
        # Calculate monthly trends for donations
        if 'תאריך' in donations_df.columns and 'שקלים' in donations_df.columns:
            donations_df['תאריך'] = pd.to_datetime(donations_df['תאריך'], format='%d.%m.%Y', errors='coerce')
            monthly_donations = donations_df.groupby(donations_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum()
            
            # Calculate trend and change
            if len(monthly_donations) > 1:
                donations_trend = "עולה" if monthly_donations.iloc[-1] > monthly_donations.iloc[0] else "יורד"
                donations_change = ((monthly_donations.iloc[-1] - monthly_donations.iloc[0]) / monthly_donations.iloc[0] * 100) if monthly_donations.iloc[0] != 0 else 0
            else:
                donations_trend = "יציב"
                donations_change = 0
        else:
            monthly_donations = pd.Series()
            donations_trend = "לא ניתן לחשב"
            donations_change = 0
            
        # Calculate monthly comparison
        monthly_comparison = {}
        if not monthly_expenses.empty and not monthly_donations.empty:
            common_months = set(monthly_expenses.index).intersection(set(monthly_donations.index))
            for month in common_months:
                monthly_comparison[month] = {
                    'expenses': monthly_expenses[month],
                    'donations': monthly_donations[month],
                    'balance': monthly_donations[month] - monthly_expenses[month]
                }
            
        return {
            'expenses_trend': expenses_trend,
            'donations_trend': donations_trend,
            'expenses_change': expenses_change,
            'donations_change': donations_change,
            'monthly_expenses': monthly_expenses.to_dict(),
            'monthly_donations': monthly_donations.to_dict(),
            'monthly_comparison': monthly_comparison
        }
        
    except Exception as e:
        logging.error(f"Error calculating monthly trends: {str(e)}")
        return {
            'expenses_trend': "שגיאה",
            'donations_trend': "שגיאה",
            'expenses_change': 0,
            'donations_change': 0,
            'monthly_expenses': {},
            'monthly_donations': {},
            'monthly_comparison': {}
        }

def calculate_trend_percentage(monthly_data: pd.Series) -> float:
    """Calculate percentage change for a trend"""
    if len(monthly_data) > 1:
        first_month = monthly_data.iloc[0]
        last_month = monthly_data.iloc[-1]
        return ((last_month - first_month) / first_month * 100) if first_month != 0 else 0
    return 0

def determine_trend(percentage_change: float) -> str:
    """Determine trend based on percentage change"""
    if percentage_change > 5:
        return 'עולה'
    elif percentage_change < -5:
        return 'יורד'
    else:
        return 'יציב'

def calculate_36_month_budget(widows_df: pd.DataFrame, current_support: float) -> dict:
    """Calculate 36-month budget projection with detailed analysis"""
    try:
        # Calculate total required support
        total_required = current_support * 36
        
        # Calculate current support for 36 months
        support_36_months = widows_df['סכום חודשי'].sum() * 36
        
        # Calculate difference and percentage
        diff = support_36_months - total_required
        coverage_percentage = (support_36_months / total_required * 100) if total_required > 0 else 0
        
        # Calculate monthly breakdown
        monthly_breakdown = []
        if 'חודש התחלה' in widows_df.columns:
            widows_df['חודש התחלה'] = pd.to_datetime(widows_df['חודש התחלה'], format='%d.%m.%Y', errors='coerce')
            monthly_support = widows_df.groupby(widows_df['חודש התחלה'].dt.strftime('%Y-%m'))['סכום חודשי'].sum()
            
            for month, amount in monthly_support.items():
                monthly_breakdown.append({
                    'month': month,
                    'amount': amount,
                    'required': current_support,
                    'difference': amount - current_support
                })
        
        return {
            'support_36_months': support_36_months,
            'total_required': total_required,
            'diff': diff,
            'coverage_percentage': coverage_percentage,
            'monthly_breakdown': monthly_breakdown,
            'status': 'מספיק' if coverage_percentage >= 100 else 'חסר'
        }
    except Exception as e:
        logging.error(f"Error calculating 36-month budget: {str(e)}")
        return {
            'support_36_months': 0,
            'total_required': 0,
            'diff': 0,
            'coverage_percentage': 0,
            'monthly_breakdown': [],
            'status': 'שגיאה'
        }

def calculate_monthly_averages_old(df, column_name):
    try:
        monthly_avg = df.groupby(df['תאריך'].dt.strftime('%Y-%m'))[column_name].mean()
        return monthly_avg
    except Exception as e:
        st.error(f"שגיאה בחישוב ממוצעים חודשיים: {str(e)}")
        return pd.Series()

def calculate_total_support_old(widows_df):
    try:
        total_support = widows_df['סכום חודשי'].sum()
        return total_support
    except Exception as e:
        st.error(f"שגיאה בחישוב סכום התמיכה הכולל: {str(e)}")
        return 0

def calculate_monthly_budget_old(expenses_df, donations_df):
    try:
        monthly_expenses = expenses_df.groupby(expenses_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum()
        monthly_donations = donations_df.groupby(donations_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum()
        
        # Align the indices
        common_months = monthly_expenses.index.intersection(monthly_donations.index)
        monthly_expenses = monthly_expenses[common_months]
        monthly_donations = monthly_donations[common_months]
        
        # Calculate budget status
        budget_status = pd.DataFrame({
            'הוצאות': monthly_expenses,
            'תרומות': monthly_donations,
            'יתרה': monthly_donations - monthly_expenses
        })
        
        return budget_status
    except Exception as e:
        st.error(f"שגיאה בחישוב תקציב חודשי: {str(e)}")
        return pd.DataFrame()

def calculate_budget_forecast(budget_status: dict, months: int) -> dict:
    """Calculate budget forecast for specified number of months"""
    try:
        # Get current monthly averages
        total_expenses = budget_status.get('total_expenses', 0)
        total_donations = budget_status.get('total_donations', 0)
        
        # If no data, return empty forecast
        if total_expenses == 0 and total_donations == 0:
            return {
                'total_expenses': 0,
                'total_donations': 0,
                'balance': 0,
                'monthly_forecast': [],
                'forecast_months': months
            }
        
        # Calculate monthly averages (assuming 12 months of data, or use 1 if no data)
        data_months = 12 if total_expenses > 0 or total_donations > 0 else 1
        current_monthly_expenses = total_expenses / data_months
        current_monthly_donations = total_donations / data_months
        
        # Calculate forecast
        total_expenses_forecast = current_monthly_expenses * months
        total_donations_forecast = current_monthly_donations * months
        balance = total_donations_forecast - total_expenses_forecast
        
        # Create monthly forecast breakdown
        monthly_forecast = []
        for i in range(1, months + 1):
            monthly_forecast.append({
                'חודש': f'חודש {i}',
                'הוצאות': current_monthly_expenses,
                'תרומות': current_monthly_donations,
                'יתרה': current_monthly_donations - current_monthly_expenses,
                'יחס כיסוי': (current_monthly_donations / current_monthly_expenses) if current_monthly_expenses > 0 else 0
            })
        
        return {
            'total_expenses': total_expenses_forecast,
            'total_donations': total_donations_forecast,
            'balance': balance,
            'monthly_forecast': monthly_forecast,
            'forecast_months': months
        }
        
    except Exception as e:
        logging.error(f"Error calculating budget forecast: {str(e)}")
        return {
            'total_expenses': 0,
            'total_donations': 0,
            'balance': 0,
            'monthly_forecast': [],
            'forecast_months': months
        } 