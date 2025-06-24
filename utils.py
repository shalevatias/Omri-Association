import pandas as pd
import streamlit as st
import logging
import traceback
from typing import Any

def format_currency(value: Any) -> str:
    """Format number as currency"""
    try:
        return f"₪{float(value):,.2f}"
    except Exception:
        return str(value)

def create_statistical_summary(df: pd.DataFrame, value_column: str) -> pd.DataFrame:
    """Create statistical summary for a DataFrame column"""
    if not isinstance(df, pd.DataFrame) or value_column not in df.columns or df.empty:
        return pd.DataFrame({'מדד': [], 'ערך': []})
    try:
        stats = {
            'מדד': [
                'ממוצע',
                'חציון',
                'ערך מינימלי',
                'ערך מקסימלי',
                'סטיית תקן',
                'סכום כולל'
            ],
            'ערך': [
                df[value_column].mean(),
                df[value_column].median(),
                df[value_column].min(),
                df[value_column].max(),
                df[value_column].std(),
                df[value_column].sum()
            ]
        }
        
        # Format values
        stats['ערך'] = [format_currency(x) if isinstance(x, (int, float)) else x for x in stats['ערך']]
        
        return pd.DataFrame(stats)
    except Exception as e:
        logging.error(f"Error creating statistical summary: {str(e)}")
        return pd.DataFrame({'מדד': [], 'ערך': []})

def format_date(date: Any) -> str:
    """Format date to Hebrew format"""
    try:
        return pd.to_datetime(date).strftime('%d/%m/%Y')
    except Exception:
        return str(date)

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    try:
        if old_value == 0:
            return 0.0
        return ((new_value - old_value) / old_value) * 100
    except Exception as e:
        logging.error(f"Error calculating percentage change: {str(e)}")
        return 0.0

def get_month_name(date: Any) -> str:
    """Get Hebrew month name"""
    months = {
        1: "ינואר",
        2: "פברואר",
        3: "מרץ",
        4: "אפריל",
        5: "מאי",
        6: "יוני",
        7: "יולי",
        8: "אוגוסט",
        9: "ספטמבר",
        10: "אוקטובר",
        11: "נובמבר",
        12: "דצמבר"
    }
    try:
        return months[pd.to_datetime(date).month]
    except Exception:
        return ""

def format_month_year(date: Any) -> str:
    """Format date as month and year in Hebrew"""
    try:
        d = pd.to_datetime(date)
        return f"{get_month_name(d)} {d.year}"
    except Exception:
        return str(date)

def calculate_monthly_average(df: pd.DataFrame, value_column: str) -> float:
    """Calculate monthly average for a DataFrame column"""
    if not isinstance(df, pd.DataFrame) or value_column not in df.columns or df.empty:
        return 0.0
    try:
        monthly_avg = df.groupby(df['תאריך'].dt.strftime('%Y-%m'))[value_column].mean()
        return float(monthly_avg.mean())
    except Exception as e:
        logging.error(f"Error calculating monthly average: {str(e)}")
        return 0.0

def calculate_growth_rate(df: pd.DataFrame, value_column: str) -> float:
    """Calculate growth rate for a DataFrame column"""
    if not isinstance(df, pd.DataFrame) or value_column not in df.columns or df.empty:
        return 0.0
    try:
        monthly_totals = df.groupby(df['תאריך'].dt.strftime('%Y-%m'))[value_column].sum()
        if len(monthly_totals) < 2:
            return 0.0
        
        first_month = monthly_totals.iloc[0]
        last_month = monthly_totals.iloc[-1]
        
        return calculate_percentage_change(first_month, last_month)
    except Exception as e:
        logging.error(f"Error calculating growth rate: {str(e)}")
        return 0.0

def validate_date(date_str):
    """Validate date string format"""
    try:
        pd.to_datetime(date_str)
        return True
    except ValueError:
        return False

def validate_amount(amount):
    """Validate amount is a positive number"""
    try:
        amount = float(amount)
        return amount >= 0
    except ValueError:
        return False

def create_trend_graph(df, date_col, value_col, title):
    try:
        df_trend = df.groupby(date_col)[value_col].agg(['mean', 'std', 'count']).reset_index()
        df_trend.columns = [date_col, 'ממוצע', 'סטיית תקן', 'מספר תצפיות']
        st.line_chart(df_trend.set_index(date_col)[['ממוצע']])
        st.write("### סיכום סטטיסטי")
        st.write(df_trend)
    except Exception as e:
        st.error(f"שגיאה ביצירת גרף מגמות: {str(e)}")

def highlight_abnormal(df, value_col):
    try:
        mean = df[value_col].mean()
        std = df[value_col].std()
        threshold = 2
        df_highlighted = df.copy()
        df_highlighted['חריגה'] = abs(df[value_col] - mean) > (threshold * std)
        return df_highlighted
    except Exception as e:
        st.error(f"שגיאה בסימון ערכים חריגים: {str(e)}")
        return df 