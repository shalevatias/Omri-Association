import pandas as pd
import streamlit as st
from datetime import datetime
from fpdf import FPDF
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def clean_text_for_pdf(text):
    """Clean text to be safe for PDF encoding"""
    if pd.isna(text):
        return "N/A"
    
    # Convert to string and clean
    text = str(text)
    
    # Replace Hebrew characters with English equivalents or remove problematic ones
    hebrew_replacements = {
        'א': 'A', 'ב': 'B', 'ג': 'G', 'ד': 'D', 'ה': 'H', 'ו': 'V', 'ז': 'Z', 'ח': 'Ch', 'ט': 'T',
        'י': 'Y', 'כ': 'K', 'ל': 'L', 'מ': 'M', 'נ': 'N', 'ס': 'S', 'ע': 'O', 'פ': 'P', 'צ': 'Ts',
        'ק': 'Q', 'ר': 'R', 'ש': 'Sh', 'ת': 'T', 'ם': 'M', 'ן': 'N', 'ץ': 'Ts', 'ף': 'F', 'ץ': 'Ts',
        'ך': 'K', 'ם': 'M', 'ן': 'N', 'ף': 'F', 'ץ': 'Ts'
    }
    
    # Replace Hebrew characters
    for hebrew, english in hebrew_replacements.items():
        text = text.replace(hebrew, english)
    
    # Remove any remaining non-ASCII characters
    text = ''.join(char for char in text if ord(char) < 128)
    
    # Limit length to avoid PDF issues
    if len(text) > 50:
        text = text[:47] + "..."
    
    return text

def generate_monthly_report(expenses_df, donations_df, widows_df):
    """Generate a monthly report"""
    try:
        logger.info("Starting monthly report generation...")
        logger.info(f"Expenses DataFrame shape: {expenses_df.shape}")
        logger.info(f"Donations DataFrame shape: {donations_df.shape}")
        logger.info(f"Widows DataFrame shape: {widows_df.shape}")
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Add title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Monthly Report - Omri Association', 0, 1, 'C')
        
        # Add date
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Date: {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'L')
        
        # Add expenses summary
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Expenses Summary:', 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
        
        # Calculate expenses by category
        logger.info(f"Expenses columns: {list(expenses_df.columns)}")
        if 'שם' in expenses_df.columns and 'שקלים' in expenses_df.columns:
            expenses_by_category = expenses_df.groupby('שם')['שקלים'].sum().sort_values(ascending=False)
            logger.info(f"Expenses by category: {expenses_by_category.to_dict()}")
            for category, amount in expenses_by_category.items():
                clean_category = clean_text_for_pdf(category)
                pdf.cell(0, 10, f'{clean_category}: {amount:,.2f} NIS', 0, 1, 'L')
        else:
            logger.warning("Missing required columns in expenses_df")
            pdf.cell(0, 10, 'No expense data available', 0, 1, 'L')
        
        # Add donations summary
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Donations Summary:', 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
        
        # Calculate donations by donor
        logger.info(f"Donations columns: {list(donations_df.columns)}")
        if 'שם' in donations_df.columns and 'שקלים' in donations_df.columns:
            donations_by_donor = donations_df.groupby('שם')['שקלים'].sum().sort_values(ascending=False)
            logger.info(f"Donations by donor: {donations_by_donor.to_dict()}")
            for donor, amount in donations_by_donor.items():
                clean_donor = clean_text_for_pdf(donor)
                pdf.cell(0, 10, f'{clean_donor}: {amount:,.2f} NIS', 0, 1, 'L')
        else:
            logger.warning("Missing required columns in donations_df")
            pdf.cell(0, 10, 'No donation data available', 0, 1, 'L')
        
        # Add widows summary
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Widows Summary:', 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
        
        # Calculate support by widow
        logger.info(f"Widows columns: {list(widows_df.columns)}")
        if 'שם ' in widows_df.columns and 'סכום חודשי' in widows_df.columns:
            support_by_widow = widows_df.groupby('שם ')['סכום חודשי'].sum().sort_values(ascending=False)
            logger.info(f"Support by widow: {support_by_widow.to_dict()}")
            for widow, amount in support_by_widow.items():
                clean_widow = clean_text_for_pdf(widow)
                pdf.cell(0, 10, f'{clean_widow}: {amount:,.2f} NIS', 0, 1, 'L')
        else:
            logger.warning("Missing required columns in widows_df")
            pdf.cell(0, 10, 'No widows data available', 0, 1, 'L')
        
        # Save PDF
        filename = f'monthly_report_{datetime.now().strftime("%Y%m%d")}.pdf'
        logger.info(f"Saving PDF to: {filename}")
        pdf.output(filename)
        
        logger.info("Monthly report generated successfully")
        return filename
    except Exception as e:
        logger.error(f"Error generating monthly report: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        st.error(f"Error generating monthly report: {str(e)}")
        return None

def generate_widows_report(widows_df):
    """Generate a widows report"""
    try:
        logger.info("Starting widows report generation...")
        logger.info(f"Widows DataFrame shape: {widows_df.shape}")
        logger.info(f"Widows columns: {list(widows_df.columns)}")
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Add title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Widows Report - Omri Association', 0, 1, 'C')
        
        # Add date
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Date: {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'L')
        
        # Add widows list
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Widows List:', 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
        
        # Sort widows by support amount
        if 'שם ' in widows_df.columns and 'סכום חודשי' in widows_df.columns:
            widows_sorted = widows_df.sort_values('סכום חודשי', ascending=False)
            logger.info(f"Processing {len(widows_sorted)} widows")
            
            for _, row in widows_sorted.iterrows():
                try:
                    clean_name = clean_text_for_pdf(row["שם "])
                    amount = row["סכום חודשי"]
                    pdf.cell(0, 10, f'{clean_name}: {amount:,.2f} NIS', 0, 1, 'L')
                except Exception as row_error:
                    logger.error(f"Error processing row: {row_error}")
                    pdf.cell(0, 10, f'Error processing widow data', 0, 1, 'L')
            
            # Add total support
            pdf.set_font('Arial', 'B', 14)
            total_support = widows_df['סכום חודשי'].sum()
            logger.info(f"Total support: {total_support}")
            pdf.cell(0, 10, f'Total Support: {total_support:,.2f} NIS', 0, 1, 'L')
        else:
            logger.warning("Missing required columns in widows_df")
            pdf.cell(0, 10, 'No widows data available', 0, 1, 'L')
        
        # Save PDF
        filename = f'widows_report_{datetime.now().strftime("%Y%m%d")}.pdf'
        logger.info(f"Saving PDF to: {filename}")
        pdf.output(filename)
        
        logger.info("Widows report generated successfully")
        return filename
    except Exception as e:
        logger.error(f"Error generating widows report: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        st.error(f"Error generating widows report: {str(e)}")
        return None

def generate_donor_report(donations_df):
    """Generate a donor report"""
    try:
        logger.info("Starting donor report generation...")
        logger.info(f"Donations DataFrame shape: {donations_df.shape}")
        logger.info(f"Donations columns: {list(donations_df.columns)}")
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Add title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Donors Report - Omri Association', 0, 1, 'C')
        
        # Add date
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Date: {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'L')
        
        # Calculate donor statistics
        if 'שם' in donations_df.columns and 'שקלים' in donations_df.columns:
            donor_totals = donations_df.groupby('שם')['שקלים'].sum().sort_values(ascending=False)
            total_donations = donations_df['שקלים'].sum()
            logger.info(f"Total donations: {total_donations}")
            logger.info(f"Number of donors: {len(donor_totals)}")
            
            # Add summary
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Summary:', 0, 1, 'L')
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Number of donors: {len(donor_totals)}', 0, 1, 'L')
            pdf.cell(0, 10, f'Total donations: {total_donations:,.2f} NIS', 0, 1, 'L')
            
            # Add donor details
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Donor Details:', 0, 1, 'L')
            pdf.set_font('Arial', '', 12)
            
            for donor, amount in donor_totals.items():
                try:
                    clean_donor = clean_text_for_pdf(donor)
                    pdf.cell(0, 10, f'{clean_donor}: {amount:,.2f} NIS', 0, 1, 'L')
                except Exception as donor_error:
                    logger.error(f"Error processing donor {donor}: {donor_error}")
                    pdf.cell(0, 10, f'Error processing donor data', 0, 1, 'L')
        else:
            logger.warning("Missing required columns in donations_df")
            pdf.cell(0, 10, 'No donation data available', 0, 1, 'L')
        
        # Save PDF
        filename = f'donor_report_{datetime.now().strftime("%Y%m%d")}.pdf'
        logger.info(f"Saving PDF to: {filename}")
        pdf.output(filename)
        
        logger.info("Donor report generated successfully")
        return filename
    except Exception as e:
        logger.error(f"Error generating donor report: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        st.error(f"Error generating donor report: {str(e)}")
        return None

def generate_budget_report(expenses_df, donations_df):
    """Generate a budget report"""
    try:
        logger.info("Starting budget report generation...")
        logger.info(f"Expenses DataFrame shape: {expenses_df.shape}")
        logger.info(f"Donations DataFrame shape: {donations_df.shape}")
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Add title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Budget Report - Omri Association', 0, 1, 'C')
        
        # Add date
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Date: {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'L')
        
        # Add monthly comparison
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Monthly Comparison:', 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
        
        # Calculate monthly totals
        if 'תאריך' in expenses_df.columns and 'שקלים' in expenses_df.columns:
            monthly_expenses = expenses_df.groupby(expenses_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum()
            logger.info(f"Monthly expenses: {monthly_expenses.to_dict()}")
        else:
            monthly_expenses = pd.Series()
            logger.warning("Missing required columns in expenses_df")
            
        if 'תאריך' in donations_df.columns and 'שקלים' in donations_df.columns:
            monthly_donations = donations_df.groupby(donations_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum()
            logger.info(f"Monthly donations: {monthly_donations.to_dict()}")
        else:
            monthly_donations = pd.Series()
            logger.warning("Missing required columns in donations_df")
        
        for month in sorted(set(monthly_expenses.index) | set(monthly_donations.index)):
            expenses = monthly_expenses.get(month, 0)
            donations = monthly_donations.get(month, 0)
            balance = donations - expenses
            
            pdf.cell(0, 10, f'Month: {month}', 0, 1, 'L')
            pdf.cell(0, 10, f'Expenses: {expenses:,.2f} NIS', 0, 1, 'L')
            pdf.cell(0, 10, f'Donations: {donations:,.2f} NIS', 0, 1, 'L')
            pdf.cell(0, 10, f'Balance: {balance:,.2f} NIS', 0, 1, 'L')
            pdf.cell(0, 10, '', 0, 1, 'L')  # Add space between months
        
        # Add totals
        pdf.set_font('Arial', 'B', 14)
        total_expenses = expenses_df['שקלים'].sum() if 'שקלים' in expenses_df.columns else 0
        total_donations = donations_df['שקלים'].sum() if 'שקלים' in donations_df.columns else 0
        total_balance = total_donations - total_expenses
        
        logger.info(f"Total expenses: {total_expenses}")
        logger.info(f"Total donations: {total_donations}")
        logger.info(f"Total balance: {total_balance}")
        
        pdf.cell(0, 10, 'Summary:', 0, 1, 'L')
        pdf.cell(0, 10, f'Total expenses: {total_expenses:,.2f} NIS', 0, 1, 'L')
        pdf.cell(0, 10, f'Total donations: {total_donations:,.2f} NIS', 0, 1, 'L')
        pdf.cell(0, 10, f'Total balance: {total_balance:,.2f} NIS', 0, 1, 'L')
        
        # Save PDF
        filename = f'budget_report_{datetime.now().strftime("%Y%m%d")}.pdf'
        logger.info(f"Saving PDF to: {filename}")
        pdf.output(filename)
        
        logger.info("Budget report generated successfully")
        return filename
    except Exception as e:
        logger.error(f"Error generating budget report: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        st.error(f"Error generating budget report: {str(e)}")
        return None
