import pandas as pd
import numpy as np

print("=== ניתוח מפורט של חוסר התאמה בין תורמים ===")

# Load data
donations_df = pd.read_excel("omri.xlsx", sheet_name="Donations")
investors_df = pd.read_excel("omri.xlsx", sheet_name="Investors")
almanot_df = pd.read_excel("almanot.xlsx")

# Combine donations and investors
donations_df.columns = ["תאריך", "שם", "שקלים"]
investors_df.columns = ["תאריך", "שם", "שקלים"]
all_donations = pd.concat([donations_df, investors_df], ignore_index=True)

# Clean data - remove rows with NaN names
all_donations = all_donations.dropna(subset=['שם'])
all_donations = all_donations[all_donations['שם'] != 'שם התורם']
all_donations = all_donations[all_donations['שם'].str.strip() != '']

print(f"\n=== סטטיסטיקות כלליות ===")
print(f"מספר תרומות: {len(all_donations)}")
print(f"מספר אלמנות: {len(almanot_df)}")

print(f"\n=== תורמים בקובץ התרומות ===")
donors_in_donations = all_donations['שם'].unique()
print(f"מספר תורמים בקובץ תרומות: {len(donors_in_donations)}")
print("תורמים בקובץ תרומות:")
for i, donor in enumerate(sorted(donors_in_donations)):
    print(f"{i+1}. {donor}")

print(f"\n=== תורמים בקובץ אלמנות ===")
donors_in_widows = almanot_df['תורם'].dropna().unique()
print(f"מספר תורמים בקובץ אלמנות: {len(donors_in_widows)}")
print("תורמים בקובץ אלמנות:")
for i, donor in enumerate(sorted(donors_in_widows)):
    print(f"{i+1}. {donor}")

print(f"\n=== אלמנות ללא תורם ===")
widows_without_donor = almanot_df[almanot_df['תורם'].isna()]
print(f"מספר אלמנות ללא תורם: {len(widows_without_donor)}")
for i, (_, row) in enumerate(widows_without_donor.iterrows()):
    print(f"{i+1}. {row['שם ']}")

print(f"\n=== השוואת שמות תורמים ===")
donors_donations_set = set(donors_in_donations)
donors_widows_set = set(donors_in_widows)

print("תורמים רק בקובץ תרומות:")
for donor in sorted(donors_donations_set - donors_widows_set):
    print(f"- {donor}")

print("\nתורמים רק בקובץ אלמנות:")
for donor in sorted(donors_widows_set - donors_donations_set):
    print(f"- {donor}")

print("\nתורמים בשני הקבצים:")
for donor in sorted(donors_donations_set & donors_widows_set):
    print(f"- {donor}")

print(f"\n=== דוגמאות אלמנות עם תורמים ===")
widows_with_donor = almanot_df[almanot_df['תורם'].notna()]
for i, (_, row) in enumerate(widows_with_donor.head(10).iterrows()):
    print(f"{i+1}. {row['שם ']} -> {row['תורם']}")

print(f"\n=== ספירת חיבורים לכל תורם ===")
donor_connections = almanot_df['תורם'].value_counts()
print(donor_connections)

print(f"\n=== ניתוח תרומות לפי תורם ===")
donations_by_donor = all_donations.groupby('שם')['שקלים'].sum().sort_values(ascending=False)
print("תרומות לפי תורם:")
for donor, amount in donations_by_donor.items():
    print(f"- {donor}: ₪{amount:,.0f}")

print(f"\n=== תורמים עם תרומות אבל ללא אלמנות ===")
donors_with_donations_no_widows = donors_donations_set - donors_widows_set
for donor in sorted(donors_with_donations_no_widows):
    donor_amount = donations_by_donor.get(donor, 0)
    print(f"- {donor}: ₪{donor_amount:,.0f}")

print(f"\n=== תורמים עם אלמנות אבל ללא תרומות ===")
donors_with_widows_no_donations = donors_widows_set - donors_donations_set
for donor in sorted(donors_with_widows_no_donations):
    print(f"- {donor}")

print(f"\n=== סיכום הבעיות ===")
print(f"1. תורמים עם תרומות אבל ללא אלמנות: {len(donors_with_donations_no_widows)}")
print(f"2. תורמים עם אלמנות אבל ללא תרומות: {len(donors_with_widows_no_donations)}")
print(f"3. אלמנות ללא תורם: {len(widows_without_donor)}")
print(f"4. תורמים בשני הקבצים: {len(donors_donations_set & donors_widows_set)}") 