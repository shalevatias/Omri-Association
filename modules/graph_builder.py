"""
Graph Builder Module for Omri Association Dashboard
Handles creation of network graph visualization
"""

import pandas as pd
import math
import logging
from streamlit_agraph import agraph, Node, Edge, Config

logger = logging.getLogger(__name__)

def create_network_graph(donations_df, widows_df, widow_to_donor_mapping, donor_connections, real_widows_df):
    """יצירת גרף רשת של קשרים בין תורמים לאלמנות"""
    try:
        # יצירת רשימת צמתים וקשתות
        nodes = []
        edges = []
        
        # צבעים תואמים לעיצוב
        donor_color = "#2563eb"  # כחול עיקרי
        widow_color = "#f43f5e"  # ורוד-אדום
        highlight_color = "#a21caf"  # סגול כהה להדגשה
        edge_color_1000 = "#fbbf24"  # צהוב רך
        edge_color_2000 = "#2563eb"  # כחול
        edge_color_other = "#a3a3a3"  # אפור
        
        # ניקוי נתונים - הסרת שורות עם שמות תורמים ריקים
        donations_df_clean = donations_df.dropna(subset=['שם התורם'])
        donations_df_clean = donations_df_clean[donations_df_clean['שם התורם'] != '']
        donations_df_clean = donations_df_clean[donations_df_clean['שם התורם'].str.strip() != '']
        
        donors = donations_df_clean['שם התורם'].unique()
        
        # בדיקה אילו תורמים יש להם תרומות בפועל
        donors_with_actual_donations = set(donations_df_clean['שם התורם'].unique())
        
        # זיהוי תורמים עם קשרים
        donors_with_connections = set(donor_connections.keys()) - {'nan'}
        donors_with_connections = donors_with_connections.intersection(donors_with_actual_donations)
        donors_without_connections = set(donors) - donors_with_connections
        
        # יצירת מיפוי של מספר חיבורים לגודל צומת
        connection_size_mapping = {}
        max_connections = max(donor_connections.values()) if donor_connections else 0
        
        for connection_count in range(1, max_connections + 1):
            base_size = 20
            connection_bonus = connection_count * 4
            connection_size_mapping[connection_count] = base_size + connection_bonus
        
        donor_nodes = {}
        
        # הוספת תורמים עם קשרים במרכז במעגל
        center_x = 0
        center_y = 0
        donors_with_connections_list = list(donors_with_connections)
        for i, donor in enumerate(donors_with_connections_list):
            node_id = f"donor_{donor}"
            donor_nodes[donor] = node_id
            
            connection_count = donor_connections.get(donor, 1)
            node_size = connection_size_mapping.get(connection_count, 20)
            
            angle = (i / len(donors_with_connections_list)) * 2 * 3.14159
            radius = 200
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            nodes.append(
                Node(
                    id=node_id,
                    label=donor,
                    size=node_size,
                    color=donor_color,
                    shape="circle",
                    x=x,
                    y=y
                )
            )
        
        # הוספת תורמים ללא קשרים משמאל
        left_x = -600
        left_y = 0
        donors_without_connections_list = list(donors_without_connections)
        for i, donor in enumerate(donors_without_connections_list):
            node_id = f"donor_{donor}"
            donor_nodes[donor] = node_id
            nodes.append(
                Node(
                    id=node_id,
                    label=donor,
                    size=20,
                    color="#9ca3af",
                    shape="circle",
                    x=left_x,
                    y=left_y + (i * 40) - (len(donors_without_connections_list) * 20)
                )
            )
        
        # הוספת אלמנות
        widows = widows_df['שם '].unique()
        widow_nodes = {}
        
        widows_with_connections = set(widow_to_donor_mapping.keys())
        widows_without_connections = set(widows) - widows_with_connections
        
        actual_widows_with_connections = set()
        for widow_name, donor_name in widow_to_donor_mapping.items():
            if donor_name in donors_with_actual_donations:
                actual_widows_with_connections.add(widow_name)
        
        widows_with_connections = actual_widows_with_connections
        widows_without_connections = set(widows) - widows_with_connections
        
        # הוספת אלמנות עם קשרים מימין
        right_x = 600
        right_y = 0
        widows_with_connections_list = list(widows_with_connections)
        for i, widow in enumerate(widows_with_connections_list):
            node_id = f"widow_{widow}"
            widow_nodes[widow] = node_id
            nodes.append(
                Node(
                    id=node_id,
                    label=widow,
                    size=25,
                    color=widow_color,
                    shape="square",
                    x=right_x,
                    y=right_y + (i * 40) - (len(widows_with_connections_list) * 20)
                )
            )
        
        # הוספת אלמנות ללא קשרים מימין יותר
        far_right_x = 800
        far_right_y = 0
        widows_without_connections_list = list(widows_without_connections)
        for i, widow in enumerate(widows_without_connections_list):
            node_id = f"widow_{widow}"
            widow_nodes[widow] = node_id
            nodes.append(
                Node(
                    id=node_id,
                    label=widow,
                    size=20,
                    color="#9ca3af",
                    shape="square",
                    x=far_right_x,
                    y=far_right_y + (i * 40) - (len(widows_without_connections_list) * 20)
                )
            )
        
        # יצירת הקשרים
        connections_count = 0
        for i, widow_row in real_widows_df.iterrows():
            widow_name = widow_row['שם ']
            donor_name = widow_row['תורם']
            
            if donor_name in donor_nodes and widow_name in widow_nodes:
                donor_donations = donations_df_clean[donations_df_clean['שם התורם'] == donor_name]
                if not donor_donations.empty:
                    last_row = donor_donations.sort_values('תאריך', ascending=False).iloc[0]
                    last_amount = last_row['סכום']
                    last_date = last_row['תאריך']
                    donation_k = last_amount / 1000
                    edge_width = max(1, min(8, donation_k / 10))
                    
                    if last_amount == 1000:
                        edge_color = edge_color_1000
                    elif last_amount == 2000:
                        edge_color = edge_color_2000
                    else:
                        edge_color = edge_color_other
                    
                    edges.append(
                        Edge(
                            source=donor_nodes[donor_name],
                            target=widow_nodes[widow_name],
                            color=edge_color,
                            width=edge_width,
                            title=f"{donor_name} → {widow_name}: {donation_k:.1f}k ₪ ({last_date.strftime('%d/%m/%Y') if pd.notna(last_date) else 'תאריך לא מוגדר'})"
                        )
                    )
                    connections_count += 1
        
        return nodes, edges, connections_count
        
    except Exception as e:
        logger.error(f"Error creating network graph: {str(e)}")
        return [], [], 0

def create_graph_config():
    """יצירת תצורת הגרף"""
    return Config(
        height=800,
        width=1200,
        directed=True,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightNearest=True,
        collapsible=False,
        node={'labelProperty': 'label'},
        link={'labelProperty': 'label', 'renderLabel': True},
        d3={'gravity': -100, 'linkLength': 100},
        stabilization=True,
        fit=True,
        manipulation={
            'enabled': True,
            'initiallyActive': False,
            'addNode': False,
            'addEdge': True,
            'editNode': False,
            'editEdge': True,
            'deleteNode': False,
            'deleteEdge': True,
            'controlNodeStyle': {
                'shape': 'circle',
                'size': 20,
                'color': {'background': '#4ade80', 'border': '#22c55e'},
                'font': {'color': '#ffffff', 'size': 12}
            }
        }
    )
 