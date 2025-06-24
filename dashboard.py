import pandas as pd
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import string

# --- Config Streamlit ---
st.set_page_config(page_title='דשבורד', layout='wide')
st.title("דשבורד עמותת עמרי למען משפחות השכול")

# --- Google Sheets auth ---
SERVICE_ACCOUNT_FILE = "service_account.json"
SPREADSHEET_ID       = "1zo3Rnmmykvd55owzQyGPSjx6cYfy4SB3SZc-Ku7UcOo"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds  = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
gc     = gspread.authorize(creds)
try:
    sh = gc.open_by_key(SPREADSHEET_ID)
except Exception as e:
    st.error(f"❌ שגיאה בגישה לגיליון: {e}")
    st.stop()

def read_sheet(name: str) -> pd.DataFrame:
    ws   = sh.worksheet(name)
    vals = ws.get_all_values()
    hdr_i = next(i for i,row in enumerate(vals) if any(cell.strip() for cell in row))
    cols  = vals[hdr_i]
    data  = vals[hdr_i+1:]
    return pd.DataFrame(data, columns=cols)

def write_sheet(df: pd.DataFrame, name: str):
    ws       = sh.worksheet(name)
    rows, cols = df.shape
    last_col = chr(ord("A") + cols - 1)
    rng      = f"A2:{last_col}{rows+1}"
    ws.update(rng, df.fillna("").astype(str).values.tolist())

def clean_money(s: pd.Series) -> pd.Series:
    return (
        s.astype(str)
         .str.replace(r"[^\d\.]", "", regex=True)
         .replace("", "0")
         .astype(float)
    )

def fix_empty_headers(df: pd.DataFrame) -> pd.DataFrame:
    """Replace any empty column name with its Excel letter (A, B, C, ...)."""
    new_cols = []
    for idx, col in enumerate(df.columns):
        if not col.strip():
            letter = string.ascii_uppercase[idx] if idx < 26 else f"Col{idx}"
            new_cols.append(letter)
        else:
            new_cols.append(col)
    df.columns = new_cols
    return df

# --- Load raw DataFrames ---
exp_raw   = read_sheet("Expenses")
don_raw   = read_sheet("Donations")
inv_raw   = read_sheet("Investors")
alman_raw = read_sheet("Almanot")

# --- Fix headers so no empty names remain ---
exp_raw   = fix_empty_headers(exp_raw)
don_raw   = fix_empty_headers(don_raw)
inv_raw   = fix_empty_headers(inv_raw)
alman_raw = fix_empty_headers(alman_raw)

# --- Editable full tables ---
st.markdown("## עריכת טבלאות (Google Sheets)")
with st.expander("📋 הוצאות"):
    exp_edit = st.data_editor(exp_raw, num_rows="dynamic")
with st.expander("📋 תרומות עיקריות"):
    don_edit = st.data_editor(don_raw, num_rows="dynamic")
with st.expander("📋 תרומות משקיעים"):
    inv_edit = st.data_editor(inv_raw, num_rows="dynamic")
with st.expander("📋 אלמנות"):
    alman_edit = st.data_editor(alman_raw, num_rows="dynamic")

if st.sidebar.button("שמור שינויים"):
    write_sheet(exp_edit,   "Expenses")
    write_sheet(don_edit,   "Donations")
    write_sheet(inv_edit,   "Investors")
    write_sheet(alman_edit, "Almanot")
    st.sidebar.success("השינויים נשמרו!")

# --- Prepare calculation DataFrames using fixed positions ---
def prepare_calc(df: pd.DataFrame) -> pd.DataFrame:
    calc = df.iloc[:, [0, 2]].copy()  # A=תאריך, C=סכום
    calc.columns   = ["תאריך", "סכום"]
    calc["תאריך"] = pd.to_datetime(calc["תאריך"], dayfirst=True, errors="coerce")
    calc           = calc[calc["תאריך"].notna()]
    calc["סכום"]  = clean_money(calc["סכום"])
    return calc

exp_calc = prepare_calc(exp_edit)
don_calc = prepare_calc(don_edit)
inv_calc = prepare_calc(inv_edit)

# --- Almanot processing ---
alman = alman_edit.copy()
alman["סכום חודשי"] = clean_money(alman.iloc[:, 6])  # G
alman["חודש התחלה"] = pd.to_datetime(alman.iloc[:, 5], dayfirst=True, errors="coerce")  # F

# --- Dashboard calculations ---
sum_exp   = exp_calc["סכום"].sum()
sum_don   = don_calc["סכום"].sum()
sum_inv   = inv_calc["סכום"].sum()
total_don = sum_don + sum_inv
available = total_don - sum_exp

don_calc["month"]  = don_calc["תאריך"].dt.to_period("M").dt.to_timestamp()
monthly_don       = don_calc.groupby("month")["סכום"].sum().reset_index()

total_widows            = len(alman)
count_1000              = int((alman["סכום חודשי"] == 1000).sum())
count_2000              = int((alman["סכום חודשי"] == 2000).sum())
current_monthly_support = count_1000 * 1000 + count_2000 * 2000
support_36_months       = current_monthly_support * 36

# --- Display ---
st.markdown("---")
st.subheader("סיכום אלמנות")
w1,w2,w3,w4,w5 = st.columns(5)
w1.metric("סה״כ אלמנות",            f"{total_widows:,}")
w2.metric("אלמנות ב-1,000 ₪",        f"{count_1000:,}")
w3.metric("אלמנות ב-2,000 ₪",        f"{count_2000:,}")
w4.metric("תמיכה חודשית נוכחית (₪)", f"{current_monthly_support:,.0f}")
w5.metric("תמיכה ל-36 חודשים (₪)",   f"{support_36_months:,.0f}")

st.markdown("---")
st.subheader("עיקרי כספים")
c1,c2,c3 = st.columns(3)
c1.metric("סה״כ תרומות", f"₪{total_don:,.0f}")
c2.metric("סה״כ הוצאות", f"₪{sum_exp:,.0f}")
c3.metric("סכום זמין",   f"₪{available:,.0f}")

st.markdown("---")
st.subheader("גרף תרומות חודשיות")
if not monthly_don.empty:
    st.line_chart(
        monthly_don.rename(columns={"month":"index","סכום":"value"}).set_index("index")
    )
else:
    st.write("אין נתוני תרומות חודשיות")

# ==== Future widows calculator (36 months) ====
st.markdown("---")
st.subheader("הוספת אלמנות נוספות (36 חודשים)")
col1,col2 = st.columns(2)
with col1:
    n1   = st.slider("1,000 ₪/חודש", 0, 100, 0)
    req1 = n1 * 1000 * 36
with col2:
    n2   = st.slider("2,000 ₪/חודש", 0, 100, 0)
    req2 = n2 * 2000 * 36

total_req = req1 + req2
diff      = available - support_36_months - total_req

st.write(f"**דרוש (36ח):** ₪{total_req:,.0f}")
if diff >= 0:
    st.success(f"**תקציב חופשי שנותר:** ₪{diff:,.0f}")
else:
    st.error(f"**חסר לגייס:** ₪{abs(diff):,.0f}")
