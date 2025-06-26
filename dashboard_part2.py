                all_names = list(donors) + list(widows)
                selected_name = st.selectbox("חפש תורם/אלמנה להדגשה בגרף", options=["בחר שם להדגשה..."] + sorted(all_names), index=0)
                
                # הדגשת הצומת שנבחרה
                if selected_name != "בחר שם להדגשה...":
                    for node in nodes:
                        if node.label == selected_name:
                            node.color = highlight_color
                            node.size = node.size + 5
                            break
                    st.info(f"🔎 בחרת להדגיש את: {selected_name}. הצומת מודגשת בצבע סגול.")
                
                # הגדרת תצורת הגרף
                config = Config(
                    height=1000,
                    width=1800,
                    directed=True,
                    physics=True,
                    hierarchical=False,
                    nodeHighlightBehavior=True,
                    highlightColor=highlight_color,
                    collapsible=True,
                    node={
                        'labelProperty': 'label',
                        'fontSize': 12,
                        'fontFace': 'Arial',
                        'fontColor': '#ffffff'
                    },
                    link={'labelProperty': 'title', 'renderLabel': True},
                    zoom=1.0,
                    minZoom=0.1,
                    maxZoom=3.0,
                    search=True,
                    searchOptions={
                        'caseSensitive': False,
                        'highlightFirst': True,
                        'highlightAll': True
                    }
                )
                
                # CSS למרכוז הגרף ולצמצום רווחים
                st.markdown("""
                <style>
                .stAgraph {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 0 auto !important;
                    padding: 0 !important;
                }
                .block-container {
                    padding-top: 1rem !important;
                    padding-bottom: 0.5rem !important;
                }
                .stSelectbox, .stInfo, .stMarkdown {
                    margin-bottom: 0.5rem !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # הצגת הגרף
                agraph(nodes=nodes, edges=edges, config=config)
                
                # הסבר על הדגשה
                if selected_name != "בחר שם להדגשה...":
                    st.info(f"💡 **טיפ**: כדי לראות את הצומת בצורה ברורה יותר, השתמש גם בחיפוש המובנה של הגרף למעלה או לחץ על הצומת.")
                
                # מידע על הגרף
                st.info(f"📊 **מידע על הגרף**: מוצגים {connections_count} קשרים מתוך {len(donors)} תורמים ({donor_color}) ו-{len(widows)} אלמנות ({widow_color})")
                
                # הסבר על הצבעים
                st.markdown("### הסבר על הצבעים:")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"🟡 <span style='color:{edge_color_1000}'>**צהוב**</span>: תרומות של 1,000 ₪", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"🔵 <span style='color:{edge_color_2000}'>**כחול**</span>: תרומות של 2,000 ₪", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"⚪ <span style='color:{edge_color_other}'>**אפור**</span>: תרומות אחרות", unsafe_allow_html=True)
            
            except Exception as e:
                logging.error(f"Error creating network graph: {str(e)}")
                logging.error(traceback.format_exc())
                st.error("שגיאה ביצירת מפת הקשרים. אנא נסה שוב.")
        
    except Exception as e:
        logging.error(f"Error in main function: {str(e)}")
        logging.error(traceback.format_exc())
        st.error("שגיאה בהצגת הדשבורד. אנא נסה לרענן את הדף.")

if __name__ == "__main__":
    main()
