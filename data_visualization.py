import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
import traceback
import time
import uuid

def create_comparison_chart(expenses_df: pd.DataFrame, donations_df: pd.DataFrame) -> None:
    """Create a comparison chart between expenses and donations"""
    try:
        if not isinstance(expenses_df, pd.DataFrame) or not isinstance(donations_df, pd.DataFrame):
            st.error("הנתונים חייבים להיות DataFrame")
            return
            
        if 'תאריך' not in expenses_df.columns or 'שקלים' not in expenses_df.columns or 'תאריך' not in donations_df.columns or 'שקלים' not in donations_df.columns:
            st.error("חסרות עמודות נדרשות")
            return
            
        # Calculate monthly totals
        monthly_expenses = expenses_df.groupby(expenses_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum().reset_index()
        monthly_donations = donations_df.groupby(donations_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum().reset_index()
        
        # Create the chart
        fig = go.Figure()
        
        # Add expenses bars
        fig.add_trace(go.Bar(
            x=monthly_expenses['תאריך'],
            y=monthly_expenses['שקלים'],
            name='הוצאות',
            marker_color='red',
            hovertemplate='חודש: %{x}<br>סכום: %{y:,.0f} ₪<extra></extra>'
        ))
        
        # Add donations bars
        fig.add_trace(go.Bar(
            x=monthly_donations['תאריך'],
            y=monthly_donations['שקלים'],
            name='תרומות',
            marker_color='green',
            hovertemplate='חודש: %{x}<br>סכום: %{y:,.0f} ₪<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title='השוואת הוצאות ותרומות חודשיות',
            xaxis_title='חודש',
            yaxis_title='סכום (₪)',
            barmode='group',
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f'comparison_chart_{uuid.uuid4().hex[:8]}')
        
    except Exception as e:
        st.error(f"שגיאה ביצירת גרף השוואה: {str(e)}")
        logging.error(f"Error creating comparison chart: {str(e)}")

def create_monthly_trends(expenses_df: pd.DataFrame, donations_df: pd.DataFrame) -> None:
    """Create monthly trends chart"""
    try:
        if not isinstance(expenses_df, pd.DataFrame) or not isinstance(donations_df, pd.DataFrame):
            st.error("הנתונים חייבים להיות DataFrame")
            return
            
        if 'תאריך' not in expenses_df.columns or 'שקלים' not in expenses_df.columns or 'תאריך' not in donations_df.columns or 'שקלים' not in donations_df.columns:
            st.error("חסרות עמודות נדרשות")
            return
            
        # Calculate monthly totals
        monthly_expenses = expenses_df.groupby(expenses_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum().reset_index()
        monthly_donations = donations_df.groupby(donations_df['תאריך'].dt.strftime('%Y-%m'))['שקלים'].sum().reset_index()
        
        # Create the chart
        fig = go.Figure()
        
        # Add expenses line
        fig.add_trace(go.Scatter(
            x=monthly_expenses['תאריך'],
            y=monthly_expenses['שקלים'],
            name='הוצאות',
            line=dict(color='red', width=2),
            hovertemplate='חודש: %{x}<br>סכום: %{y:,.0f} ₪<extra></extra>'
        ))
        
        # Add donations line
        fig.add_trace(go.Scatter(
            x=monthly_donations['תאריך'],
            y=monthly_donations['שקלים'],
            name='תרומות',
            line=dict(color='green', width=2),
            hovertemplate='חודש: %{x}<br>סכום: %{y:,.0f} ₪<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title='מגמות חודשיות בהוצאות ותרומות',
            xaxis_title='חודש',
            yaxis_title='סכום (₪)',
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f'monthly_trends_{uuid.uuid4().hex[:8]}')
        
    except Exception as e:
        st.error(f"שגיאה ביצירת גרף מגמות: {str(e)}")
        logging.error(f"Error creating monthly trends chart: {str(e)}")

def create_budget_distribution_chart(df: pd.DataFrame) -> None:
    if not isinstance(df, pd.DataFrame) or 'שם' not in df.columns or 'שקלים' not in df.columns or df.empty:
        st.error("נתונים לא תקינים או חסרים")
        return
    try:
        # Group by name and calculate totals
        budget_data = df.groupby('שם')['שקלים'].sum().reset_index()
        
        # Sort by amount
        budget_data = budget_data.sort_values('שקלים', ascending=False)
        
        # Create figure
        fig = px.pie(
            budget_data,
            values='שקלים',
            names='שם',
            title='התפלגות תקציב',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'התפלגות תקציב',
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Update traces
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='קטגוריה: %{label}<br>סכום: ₪%{value:,.0f}<br>אחוז: %{percent:.1%}<extra></extra>'
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f'budget_distribution_{uuid.uuid4().hex[:8]}')
        
    except Exception as e:
        logging.error(f"Error creating budget distribution chart: {str(e)}")
        st.error("שגיאה ביצירת גרף התפלגות תקציב")

def create_widows_support_chart(df: pd.DataFrame) -> None:
    if not isinstance(df, pd.DataFrame) or 'שם ' not in df.columns or 'סכום חודשי' not in df.columns or df.empty:
        st.error("נתונים לא תקינים או חסרים")
        return
    try:
        # Group by name and calculate totals
        support_data = df.groupby('שם ')['סכום חודשי'].sum().reset_index()
        
        # Sort by amount
        support_data = support_data.sort_values('סכום חודשי', ascending=False)
        
        # Create figure
        fig = px.bar(
            support_data,
            x='שם ',
            y='סכום חודשי',
            title='תמיכה באלמנות',
            color='סכום חודשי',
            color_continuous_scale='Viridis'
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'תמיכה באלמנות',
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title='שם',
            yaxis_title='סכום חודשי (₪)',
            showlegend=False,
            template='plotly_white',
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Update traces
        fig.update_traces(
            hovertemplate='שם: %{x}<br>סכום חודשי: ₪%{y:,.0f}<extra></extra>'
        )
        
        # Format y-axis ticks
        fig.update_yaxes(tickformat=",.0f")
        
        st.plotly_chart(fig, use_container_width=True, key=f'widows_support_chart_{uuid.uuid4().hex[:8]}')
        
    except Exception as e:
        logging.error(f"Error creating widows support chart: {str(e)}")
        st.error("שגיאה ביצירת גרף תמיכה באלמנות")

def create_donor_contribution_chart(donations_df: pd.DataFrame) -> None:
    """Create a chart showing donor contributions"""
    try:
        if not isinstance(donations_df, pd.DataFrame):
            st.error("הנתונים חייבים להיות DataFrame")
            return
            
        if 'שם' not in donations_df.columns or 'שקלים' not in donations_df.columns:
            st.error("חסרות עמודות נדרשות")
            return
            
        # Calculate total donations by donor
        donor_totals = donations_df.groupby('שם')['שקלים'].sum().sort_values(ascending=False)
        
        # Create the chart
        fig = go.Figure()
        
        # Add bars
        fig.add_trace(go.Bar(
            x=donor_totals.index,
            y=donor_totals.values,
            marker_color='green',
            hovertemplate='תורם: %{x}<br>סכום: %{y:,.0f} ₪<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title='סכום תרומות לפי תורם',
            xaxis_title='תורם',
            yaxis_title='סכום (₪)',
            hovermode='x unified',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f'donor_contribution_{uuid.uuid4().hex[:8]}')
        
    except Exception as e:
        st.error(f"שגיאה ביצירת גרף תרומות: {str(e)}")
        logging.error(f"Error creating donor contribution chart: {str(e)}")

def create_forecast_chart(forecast: dict) -> None:
    """Create a forecast chart"""
    try:
        if not isinstance(forecast, dict) or 'monthly_forecast' not in forecast:
            st.error("נתוני תחזית לא תקינים")
            return
            
        monthly_data = forecast['monthly_forecast']
        if not monthly_data:
            st.warning("אין נתוני תחזית להצגה")
            return
            
        # Create DataFrame
        df = pd.DataFrame(monthly_data)
        
        # Create the chart
        fig = go.Figure()
        
        # Add expenses line
        fig.add_trace(go.Scatter(
            x=df['חודש'],
            y=df['הוצאות'],
            name='הוצאות צפויות',
            line=dict(color='red', width=2, dash='dash'),
            hovertemplate='חודש: %{x}<br>הוצאות: %{y:,.0f} ₪<extra></extra>'
        ))
        
        # Add donations line
        fig.add_trace(go.Scatter(
            x=df['חודש'],
            y=df['תרומות'],
            name='תרומות צפויות',
            line=dict(color='green', width=2, dash='dash'),
            hovertemplate='חודש: %{x}<br>תרומות: %{y:,.0f} ₪<extra></extra>'
        ))
        
        # Add balance line
        fig.add_trace(go.Scatter(
            x=df['חודש'],
            y=df['יתרה'],
            name='יתרה צפויה',
            line=dict(color='blue', width=2),
            hovertemplate='חודש: %{x}<br>יתרה: %{y:,.0f} ₪<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title='תחזית תקציב',
            xaxis_title='חודש',
            yaxis_title='סכום (₪)',
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f'forecast_chart_{uuid.uuid4().hex[:8]}')
        
    except Exception as e:
        st.error(f"שגיאה ביצירת גרף תחזית: {str(e)}")
        logging.error(f"Error creating forecast chart: {str(e)}")

def create_monthly_budget_chart(budget_status: dict) -> None:
    """Create a monthly budget chart"""
    try:
        if not isinstance(budget_status, dict) or 'monthly_budget' not in budget_status:
            st.error("נתוני תקציב לא תקינים")
            return
            
        monthly_data = budget_status['monthly_budget']
        if not monthly_data:
            st.warning("אין נתוני תקציב חודשי להצגה")
            return
            
        # Create DataFrame
        df = pd.DataFrame(monthly_data)
        
        # Create the chart
        fig = go.Figure()
        
        # Add expenses bars
        fig.add_trace(go.Bar(
            x=df['חודש'],
            y=df['הוצאות'],
            name='הוצאות',
            marker_color='red',
            hovertemplate='חודש: %{x}<br>הוצאות: %{y:,.0f} ₪<extra></extra>'
        ))
        
        # Add donations bars
        fig.add_trace(go.Bar(
            x=df['חודש'],
            y=df['תרומות'],
            name='תרומות',
            marker_color='green',
            hovertemplate='חודש: %{x}<br>תרומות: %{y:,.0f} ₪<extra></extra>'
        ))
        
        # Add balance line
        fig.add_trace(go.Scatter(
            x=df['חודש'],
            y=df['יתרה'],
            name='יתרה',
            line=dict(color='blue', width=3),
            yaxis='y2',
            hovertemplate='חודש: %{x}<br>יתרה: %{y:,.0f} ₪<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title='תקציב חודשי',
            xaxis_title='חודש',
            yaxis_title='סכום (₪)',
            yaxis2=dict(
                title='יתרה (₪)',
                overlaying='y',
                side='right'
            ),
            barmode='group',
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f'monthly_budget_{uuid.uuid4().hex[:8]}')
        
    except Exception as e:
        st.error(f"שגיאה ביצירת גרף תקציב חודשי: {str(e)}")
        logging.error(f"Error creating monthly budget chart: {str(e)}") 