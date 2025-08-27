#!/usr/bin/env python3
"""
Dashboard Sections Module
Handles different dashboard sections like budget, donors, widows, etc.
"""

import streamlit as st
import pandas as pd
import logging
import re
from typing import Dict, Any
from data_processing import calculate_monthly_budget, calculate_donor_statistics, calculate_widow_statistics
from data_visualization import create_monthly_trends, create_budget_distribution_chart, create_donor_contribution_chart, create_widows_support_chart
from ui.dashboard_layout import create_section_header, create_metric_row, create_three_column_layout, add_spacing

def create_overview_section(expenses_df: pd.DataFrame, donations_df: pd.DataFrame, donor_stats: Dict, widow_stats: Dict):
    """Create the dashboard overview section with key metrics"""
    create_section_header("📊 סקירה כללית")
    
    # 1. FINANCIAL OVERVIEW (Most important - money flow)
    st.markdown("#### 💰 סקירה פיננסית")
    financial_metrics = [
        {
            'label': 'סך תרומות',
            'value': f"₪{pd.to_numeric(donations_df['שקלים'], errors='coerce').fillna(0).sum():,.0f}",
            'help': 'סך כל התרומות שהתקבלו עד כה'
        },
        {
            'label': 'סך הוצאות',
            'value': f"₪{pd.to_numeric(expenses_df['שקלים'], errors='coerce').fillna(0).sum():,.0f}",
            'help': 'סך כל ההוצאות שהוצאו עד כה'
        },
        {
            'label': 'יתרה זמינה',
            'value': f"₪{pd.to_numeric(donations_df['שקלים'], errors='coerce').fillna(0).sum() - pd.to_numeric(expenses_df['שקלים'], errors='coerce').fillna(0).sum():,.0f}",
            'help': 'יתרה זמינה לפעילות עתידית'
        },
        {
            'label': 'אחוז ניצול',
            'value': f"{(pd.to_numeric(expenses_df['שקלים'], errors='coerce').fillna(0).sum() / pd.to_numeric(donations_df['שקלים'], errors='coerce').fillna(0).sum() * 100) if pd.to_numeric(donations_df['שקלים'], errors='coerce').fillna(0).sum() > 0 else 0:.1f}%",
            'help': 'אחוז התרומות שהוצאו (כמה מהתרומות נוצלו)'
        }
    ]
    
    create_metric_row(financial_metrics, 4)
    add_spacing(2)
    
    # 2. ORGANIZATIONAL METRICS (People and impact)
    st.markdown("#### 👥 מדדים ארגוניים")
    org_metrics = [
        {
            'label': 'מספר תורמים',
            'value': f"{donor_stats.get('total_donors', 0):,}",
            'help': 'סך כל התורמים שתרמו לעמותה'
        },
        {
            'label': 'מספר אלמנות',
            'value': f"{widow_stats.get('total_widows', 0):,}",
            'help': 'סך כל האלמנות המטופלות על ידי העמותה'
        }
    ]
    
    create_metric_row(org_metrics, 2)
    add_spacing(2)

def create_budget_section(expenses_df: pd.DataFrame, donations_df: pd.DataFrame, budget_status: Dict):
    """Create the budget management section"""
    create_section_header("💰 ניהול תקציב")
    
    # Check if budget_status is valid
    if budget_status and isinstance(budget_status, dict) and len(budget_status) > 0:
        try:
            col1, col2, col3 = create_three_column_layout()
            with col1:
                # Calculate total monthly budget from donations
                monthly_donations = budget_status.get('monthly_donations', {})
                total_monthly_budget = sum(monthly_donations.values()) if monthly_donations else 0
                st.metric("תקציב חודשי", f"₪{total_monthly_budget:,.0f}")
            with col2:
                # Calculate total monthly expenses
                monthly_expenses = budget_status.get('monthly_expenses', {})
                total_monthly_expenses = sum(monthly_expenses.values()) if monthly_expenses else 0
                st.metric("הוצאות חודשיות", f"₪{total_monthly_expenses:,.0f}")
            with col3:
                available_budget = total_monthly_budget - total_monthly_expenses
                st.metric("יתרה זמינה", f"₪{available_budget:,.0f}")
        except Exception as e:
            st.error("שגיאה בטעינת סטטוס תקציב")
            logging.error(f"Budget status error: {e}")
    else:
        # Fallback when budget_status is empty or invalid
        st.warning("⚠️ לא ניתן לטעון נתוני תקציב חודשי")
        col1, col2, col3 = create_three_column_layout()
        with col1:
            st.metric("תקציב חודשי", "₪0")
        with col2:
            st.metric("הוצאות חודשיות", "₪0")
        with col3:
            st.metric("יתרה זמינה", "₪0")
    
    add_spacing(2)
    
    # Budget Charts
    try:
        monthly_trends_fig = create_monthly_trends(expenses_df, donations_df)
        if monthly_trends_fig:
            st.plotly_chart(monthly_trends_fig, use_container_width=True)
        else:
            st.warning("⚠️ לא ניתן לטעון גרף מגמות חודשיות")
        
        budget_dist_fig = create_budget_distribution_chart(expenses_df)
        if budget_dist_fig:
            st.plotly_chart(budget_dist_fig, use_container_width=True)
        else:
            st.warning("⚠️ לא ניתן לטעון גרף התפלגות תקציב")
    except Exception as e:
        st.error("שגיאה בטעינת גרפים תקציביים")
        logging.error(f"Budget charts error: {e}")
    
    add_spacing(3)

def create_donors_section(donations_df: pd.DataFrame, donor_stats: Dict):
    """Create the donors management section"""
    create_section_header("👥 ניהול תורמים")
    
    # Donor Charts (no duplicate metrics)
    try:
        donor_fig = create_donor_contribution_chart(donations_df)
        if donor_fig:
            st.plotly_chart(donor_fig, use_container_width=True)
        else:
            st.warning("⚠️ לא ניתן לטעון גרף תרומות תורמים")
    except Exception as e:
        st.error("שגיאה בטעינת גרפי תורמים")
        logging.error(f"Donor charts error: {e}")
    
    add_spacing(3)

def create_widows_section(almanot_df: pd.DataFrame, widow_stats: Dict):
    """Create the widows management section"""
    create_section_header("👩 ניהול אלמנות")
    
    # Widow Charts (no duplicate metrics)
    try:
        widows_fig = create_widows_support_chart(almanot_df)
        if widows_fig:
            st.plotly_chart(widows_fig, use_container_width=True)
        else:
            st.warning("⚠️ לא ניתן לטעון גרף תמיכה אלמנות")
    except Exception as e:
        st.error("שגיאה בטעינת גרפי אלמנות")
        logging.error(f"Widow charts error: {e}")
    
    add_spacing(2)
    
    # Complete Widows Table
    try:
        st.markdown("#### 📋 טבלת כל האלמנות")
        
        # Show all widows with key information
        display_columns = ['שם ', 'מספר ילדים', 'סכום חודשי', 'תורם']
        available_columns = [col for col in display_columns if col in almanot_df.columns]
        
        if len(available_columns) > 0:
            # Sort by monthly amount (descending) to show supported widows first
            sorted_widows = almanot_df.sort_values('סכום חודשי', ascending=False)
            st.dataframe(sorted_widows[available_columns], use_container_width=True)
        else:
            st.warning("⚠️ לא ניתן לטעון טבלת אלמנות")
            
    except Exception as e:
        st.error("שגיאה בטעינת טבלת אלמנות")
        logging.error(f"Widow charts error: {e}")
    
    add_spacing(3)

def create_widows_table_section(almanot_df: pd.DataFrame):
    """Create the complete widows table section"""
    create_section_header("👩 טבלת כל האלמנות")
    
    try:
        # Show all widows with key information
        display_columns = ['שם ', 'מספר ילדים', 'סכום חודשי', 'תורם']
        available_columns = [col for col in display_columns if col in almanot_df.columns]
        
        if len(available_columns) > 0:
            # Sort by monthly amount (descending) to show supported widows first
            sorted_widows = almanot_df.sort_values('סכום חודשי', ascending=False)
            st.dataframe(sorted_widows[available_columns], use_container_width=True)
        else:
            st.warning("⚠️ לא ניתן לטעון טבלת אלמנות")
            
    except Exception as e:
        st.error("שגיאה בטעינת טבלת אלמנות")
        logging.error(f"Widows table error: {e}")
    
    add_spacing(3)

def create_network_section(expenses_df: pd.DataFrame, donations_df: pd.DataFrame, almanot_df: pd.DataFrame, investors_df: pd.DataFrame):
    """Create the network visualization section"""
    create_section_header("🕸️ מפת קשרים")
    

    
    # Add network editor toggle
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        show_editor = st.button("🔧 ערוך רשת קשרים", use_container_width=True, type="secondary")
    
    # Show network editor only if user chooses to edit
    if show_editor:
        try:
            from ui.network_editor import create_network_editor
            create_network_editor(almanot_df, donations_df, investors_df)
            add_spacing(2)
        except ImportError as e:
            st.warning("⚠️ לא ניתן לטעון עורך הרשת")
            logging.error(f"Network editor import error: {e}")
    
    try:
        # Clean monthly support data - ensure all values are numeric and NaN is treated as 0
        if 'סכום חודשי' in almanot_df.columns:
            almanot_df['סכום חודשי'] = pd.to_numeric(almanot_df['סכום חודשי'], errors='coerce').fillna(0)
            st.info(f"✅ נוקו נתוני תמיכה חודשית - {len(almanot_df)} אלמנות עם ערכים תקינים")
        
        # Create nodes and edges for the network
        nodes = []
        edges = []
        

        
        # Get all valid donors with normalized names
        all_donors = set()
        donor_name_mapping = {}  # Map normalized names to original names
        
        if 'שם' in donations_df.columns:
            donors_from_donations = donations_df['שם'].dropna().unique()
            for donor in donors_from_donations:
                normalized = str(donor).strip()  # Remove extra spaces
                all_donors.add(normalized)
                donor_name_mapping[normalized] = str(donor)
        
        if 'שם' in investors_df.columns:
            investors_names = investors_df['שם'].dropna().unique()
            for investor in investors_names:
                normalized = str(investor).strip()  # Remove extra spaces
                all_donors.add(normalized)
                donor_name_mapping[normalized] = str(investor)
        
        # Categorize nodes for layout
        connected_donors = set()
        connected_widows = set()
        unconnected_donors = set()
        unconnected_widows = set()
        
        # First pass: identify connected pairs with fuzzy matching
        if 'שם ' in almanot_df.columns:
            for _, widow in almanot_df.iterrows():
                widow_name = widow['שם ']
                if pd.notna(widow_name):
                    donor = widow.get('תורם')
                    monthly_support = widow.get('סכום חודשי')
                    
                    # Handle missing monthly support values - treat NaN/non-numbers as 0
                    if pd.isna(monthly_support) or monthly_support == '' or monthly_support == 0:
                        monthly_support = 0
                    else:
                        try:
                            monthly_support = float(monthly_support)
                            # If conversion results in NaN, treat as 0
                            if pd.isna(monthly_support):
                                monthly_support = 0
                        except (ValueError, TypeError):
                            monthly_support = 0
                    
                    # Try to find matching donor with fuzzy matching
                    matched_donor = None
                    if pd.notna(donor):
                        donor_str = str(donor).strip()
                        # Exact match first
                        if donor_str in all_donors:
                            matched_donor = donor_str
                        else:
                            # Try partial matching
                            for potential_donor in all_donors:
                                if (donor_str in potential_donor or 
                                    potential_donor in donor_str or
                                    donor_str.lower() == potential_donor.lower()):
                                    matched_donor = potential_donor
                                    break
                            
                            # If still no match, try more aggressive matching
                            if not matched_donor:
                                for potential_donor in all_donors:
                                    # Remove common prefixes/suffixes and try again
                                    clean_donor = donor_str.replace('בע"מ', '').replace('עמותת', '').replace('חברה', '').strip()
                                    clean_potential = potential_donor.replace('בע"מ', '').replace('עמותת', '').replace('חברה', '').strip()
                                    
                                    if (clean_donor in clean_potential or 
                                        clean_potential in clean_donor or
                                        clean_donor.lower() == clean_potential.lower()):
                                        matched_donor = potential_donor
                                        break
                                
                                # If still no match, try handling abbreviations and initials
                                if not matched_donor:
                                    for potential_donor in all_donors:
                                        # Handle abbreviations like "א.ל." -> "אל"
                                        clean_donor = donor_str
                                        clean_potential = potential_donor
                                        
                                        # Remove dots and spaces from abbreviations
                                        clean_donor = re.sub(r'\.\s*', '', clean_donor)
                                        clean_potential = re.sub(r'\.\s*', '', clean_potential)
                                        
                                        # Try matching cleaned names
                                        if (clean_donor in clean_potential or 
                                            clean_potential in clean_donor or
                                            clean_donor.lower() == clean_potential.lower()):
                                            matched_donor = potential_donor
                                            break
                    
                    if matched_donor and monthly_support > 0:
                        # Connected pair
                        connected_donors.add(matched_donor)
                        connected_widows.add(widow_name)
                        
                        # Add edge
                        edges.append({
                            'from': matched_donor,
                            'to': widow_name,
                            'arrows': 'to',
                            'label': f"₪{monthly_support:,.0f}"
                        })
                    else:
                        # Unconnected widow
                        unconnected_widows.add(widow_name)

        
        # Identify unconnected donors
        unconnected_donors = all_donors - connected_donors
        
        # Debug: Show monthly support values and data quality
        st.info(f"🔍 ערכים בעמודת סכום חודשי: {almanot_df['סכום חודשי'].value_counts(dropna=False).to_dict()}")
        st.info(f"🔍 סה״כ שורות: {len(almanot_df)}, ערכים לא ריקים: {almanot_df['סכום חודשי'].notna().sum()}")
        
        # Show sample of problematic rows
        problematic_rows = almanot_df[almanot_df['סכום חודשי'].isna() | (almanot_df['סכום חודשי'] == '') | (almanot_df['סכום חודשי'] == 0)]
        if not problematic_rows.empty:
            st.warning(f"⚠️ נמצאו {len(problematic_rows)} שורות עם ערכים חסרים או שגויים בעמודת סכום חודשי")
            st.dataframe(problematic_rows[['שם ', 'סכום חודשי', 'תורם']].head(5))
        
        # Add nodes with area constraints for natural floating
        
        # Left area: Unconnected widows (will float naturally in left area)
        for widow_name in sorted(unconnected_widows):
            nodes.append({
                'id': widow_name,
                'label': widow_name,
                'group': 'widow_unconnected',
                'title': 'אלמנה ללא קשר'
            })
        
        # Middle area: Connected pairs (will float naturally in middle area)
        for donor in sorted(connected_donors):
            nodes.append({
                'id': donor,
                'label': donor,
                'group': 'donor_connected',
                'title': 'תורם מחובר'
            })
        
        for widow in sorted(connected_widows):
            nodes.append({
                'id': widow,
                'label': widow,
                'group': 'widow_connected',
                'title': 'אלמנה מחוברת'
            })
        
        # Right area: Unconnected donors (will float naturally in right area)
        for donor_name in sorted(unconnected_donors):
            nodes.append({
                'id': donor_name,
                'label': donor_name,
                'group': 'donor_unconnected',
                'title': 'תורם ללא קשר'
            })
        
        # Create network visualization
        if nodes and edges:
            # Show network info for debugging
            st.info(f"🌐 רשת עם {len(nodes)} צמתים ו-{len(edges)} קשרים")
            
            # Add custom CSS and JavaScript for area constraints
            st.markdown("""
            <style>
            /* Force all text in network view to be black */
            .stPlotlyChart, .stPlotlyChart * {
                color: #000000 !important;
            }
            /* Network specific text colors */
            .vis-network, .vis-network * {
                color: #000000 !important;
            }
            /* Edge labels */
            .vis-edge-label {
                color: #000000 !important;
                background-color: #ffffff !important;
            }
            /* Make network use full available width */
            .stPlotlyChart {
                width: 100% !important;
                max-width: none !important;
            }
            /* Ensure the agraph container uses full width */
            .stPlotlyChart > div {
                width: 100% !important;
                max-width: none !important;
            }
            </style>
            
            <script>
            // Add area constraints after network loads
            setTimeout(function() {
                const network = document.querySelector('.vis-network');
                if (network && network.__vis_network) {
                    const visNetwork = network.__vis_network;
                    
                    // Add physics constraints for area separation with extremely tight areas
                    visNetwork.on('stabilizationProgress', function(params) {
                        // Constrain nodes to their designated areas
                        const nodes = visNetwork.body.data.nodes;
                        nodes.forEach(function(node) {
                            if (node.group === 'widow_unconnected') {
                                // Keep unconnected widows on left side - extremely tight area
                                if (node.x > -10) node.x = -10;
                            } else if (node.group === 'donor_unconnected') {
                                // Keep unconnected donors on right side - extremely tight area
                                if (node.x < 10) node.x = 10;
                            } else if (node.group === 'donor_connected' || node.group === 'widow_connected') {
                                // Keep connected pairs in middle area - extremely tight area
                                if (node.x < -10 || node.x > 10) node.x = 0;
                            }
                        });
                    });
                }
            }, 1000);
            </script>
            """, unsafe_allow_html=True)
            
            try:
                from streamlit_agraph import agraph, Node, Edge, Config
                
                # Convert to agraph format with natural floating
                agraph_nodes = []
                for node in nodes:
                    if node['group'] == 'donor_connected':
                        # Connected donor (middle, blue)
                        agraph_nodes.append(Node(
                            id=node['id'], 
                            label=node['label'], 
                            size=25,
                            color="#1f77b4",  # Blue
                            font={"size": 8, "color": "#000000", "face": "Arial", "bold": True},
                            title=node['title']
                        ))
                    elif node['group'] == 'widow_connected':
                        # Connected widow (middle, orange)
                        agraph_nodes.append(Node(
                            id=node['id'], 
                            label=node['label'], 
                            size=22,
                            color="#ff7f0e",  # Orange
                            font={"size": 7, "color": "#000000", "face": "Arial", "bold": True},
                            title=node['title']
                        ))
                    elif node['group'] == 'donor_unconnected':
                        # Unconnected donor (right side, light blue)
                        agraph_nodes.append(Node(
                            id=node['id'], 
                            label=node['label'], 
                            size=20,
                            color="#87ceeb",  # Light blue
                            font={"size": 7, "color": "#000000", "face": "Arial", "bold": True},
                            title=node['title']
                        ))
                    elif node['group'] == 'widow_unconnected':
                        # Unconnected widow (left side, light orange)
                        agraph_nodes.append(Node(
                            id=node['id'], 
                            label=node['label'], 
                            size=18,
                            color="#ffb347",  # Light orange
                            font={"size": 7, "color": "#000000", "face": "Arial", "bold": True},
                            title=node['title']
                        ))
                
                agraph_edges = [Edge(
                    source=edge['from'], 
                    target=edge['to'], 
                    arrows="to",
                    label=edge['label'],
                    color="#333333",  # Darker color for better visibility
                    width=1.5,       # Thinner lines for cleaner look
                    font={"size": 8, "color": "#000000"}  # Small, black text for edge labels
                ) for edge in edges]
                
                config = Config(
                    height=800,       # Increased height to use more vertical space
                    width="100%",     # Use full available width
                    directed=True,
                    physics=True,     # Enable physics for natural floating
                    hierarchical=False,
                    nodeHighlightBehavior=True,
                    highlightColor="#F7A7A6",
                    collapsible=True,
                    nodeSpacing=20,   # Extremely tight spacing between nodes for maximum compactness
                    nodeSize=25,      # Match the largest node size
                    fontSize=8,       # Match the font size
                    fontColor="#000000",  # Black text for all labels
                    backgroundColor="#ffffff",
                    linkHighlightBehavior=True,
                    linkHighlightColor="#F7A7A6",
                    labelHighlightBold=True,
                    showEdgeLabels=True
                )
                
                # Use full width for the network graph
                agraph(nodes=agraph_nodes, edges=agraph_edges, config=config)
                
            except ImportError:
                st.warning("⚠️ streamlit-agraph לא מותקן. התקן עם: pip install streamlit-agraph")
                st.info("מפת קשרים תציג כאן לאחר התקנת streamlit-agraph")
        else:
            st.info("אין נתונים להצגת מפת קשרים")
            
    except Exception as e:
        st.error("שגיאה ביצירת מפת קשרים")
        logging.error(f"Network error: {e}")
