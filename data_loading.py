import pandas as pd
import streamlit as st
import os

def load_data():
    """Load data from Excel files"""
    try:
        # Load expenses data
        exp = pd.read_excel("omri.xlsx", sheet_name="Expenses")
        exp.columns = ["תאריך", "שם", "שקלים"]
        exp = clean_dataframe(exp)
        
        # Load donations data
        don = pd.read_excel("omri.xlsx", sheet_name="Donations")
        don.columns = ["תאריך", "שם התורם", "סכום חודשי"]
        don = clean_dataframe(don)
        
        # Load investors data
        inv = pd.read_excel("omri.xlsx", sheet_name="Investors")
        inv.columns = ["תאריך", "שם התורם", "סכום חודשי"]
        inv = clean_dataframe(inv)
        
        # Combine donations and investors
        donations_df = pd.concat([don, inv], ignore_index=True)
        
        # Load widows data
        alman = pd.read_excel("almanot.xlsx")
        # Print column names for debugging
        st.write("עמודות קובץ האלמנות:", alman.columns.tolist())
        if "סכום חודשי" not in alman.columns:
            st.warning("לא נמצאה עמודת 'סכום חודשי' בקובץ האלמנות. נוצרת עמודה עם ערך ברירת מחדל 0.")
            alman["סכום חודשי"] = 0
        alman = clean_widows_data(alman)
        
        return exp, donations_df, alman
        
    except FileNotFoundError as e:
        st.error(f"שגיאה: לא נמצא קובץ {str(e)}")
        return None, None, None
    except Exception as e:
        st.error(f"שגיאה בטעינת הנתונים: {str(e)}")
        return None, None, None

def clean_dataframe(df):
    """Clean dataframe data"""
    # Convert date format
    df['תאריך'] = pd.to_datetime(df['תאריך'])
    
    # Remove currency symbols and convert to float
    if 'שקלים' in df.columns:
        df['שקלים'] = df['שקלים'].astype(str).str.replace('₪', '').str.replace(',', '').astype(float)
    if 'סכום חודשי' in df.columns:
        df['סכום חודשי'] = df['סכום חודשי'].astype(str).str.replace('₪', '').str.replace(',', '').astype(float)
    
    return df

def clean_widows_data(alman):
    """Clean widows data"""
    # Remove currency symbols and convert to float
    if 'סכום חודשי' in alman.columns:
        alman['סכום חודשי'] = alman['סכום חודשי'].astype(str).str.replace('₪', '').str.replace(',', '').astype(float)
    
    return alman 