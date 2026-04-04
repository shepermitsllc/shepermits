import os
import streamlit as st
import pandas as pd
from datetime import date
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
client = OpenAI()

st.set_page_config(page_title="shePERMITS", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@1&family=DM+Sans:wght@600;700&family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #1f4fd8; color: #fafaf7; }
    .stApp { background-color: #1f4fd8; }
    [data-testid="stAppViewContainer"] { background-color: #1f4fd8; }
    [data-testid="stHeader"] { background-color: #1f4fd8; }
    .block-container { padding-top: 2.5rem; padding-bottom: 2rem; }
    h1, h2, h3 { font-family: 'DM Sans', sans-serif; color: #fafaf7; font-weight: 700; }
    .stSelectbox label { font-weight: 600; color: #fafaf7; }
    .stButton > button { background-color: #F6EB9A; color: #1f2933; font-family: 'Inter', sans-serif; font-weight: 700; border: none; border-radius: 8px; padding: 0.6rem 2rem; font-size: 0.95rem; width: 100%; }
    .stButton > button:hover { background-color: #ffe566; color: #1f2933; }
    hr { border-color: rgba(255,255,255,0.15); }
    table { width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 0.88rem; }
    thead tr { background-color: rgba(255,255,255,0.08); color: #a8c4ff; text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.08em; }
    thead th { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
    tbody tr { border-bottom: 1px solid rgba(255,255,255,0.07); }
    tbody tr:hover { background-color: rgba(255,255,255,0.05); }
    tbody td { padding: 0.7rem 1rem; color: #fafaf7 !important; background-color: rgba(255,255,255,0.06) !important; }
    tbody td * { color: #fafaf7 !important; }
    tbody tr:nth-child(even) td { background-color: rgba(255,255,255,0.03) !important; }
    table, th, td { color: #fafaf7 !important; border-color: rgba(255,255,255,0.1) !important; }
  
    div[data-testid="stTextInput"] {
        margin-top: -1.5rem !important;
    }
    section[data-testid="stMain"] div[data-baseweb="select"] {
        margin-top: -0.75rem !important;
    }
    footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)
# Header
with open(os.path.join(os.path.dirname(__file__), "logo.svg"), "r") as f:
    svg_content = f.read()

st.markdown(
    f'<div style="text-align:center; max-width:700px; margin:0 auto;">{svg_content}</div>',
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# Load data
df = pd.read_excel(
    os.path.join(os.path.dirname(__file__), "data", "shePERMITS - License Tracker.xlsx")
)

df = df[[c for c in df.columns if c is not None]]
df.columns = df.columns.str.strip()
df["Expires"] = pd.to_datetime(df["Expires"], errors="coerce")
df["Company Name"] = df["Company Name"].str.strip()
df["State"] = df["State"].str.strip()

today = pd.Timestamp(date.today())
df["Days Remaining"] = (df["Expires"] - today).dt.days

def get_status(days):
    if pd.isna(days):
        return "⚪ Unknown"
    elif days < 0:
        return "🔴 Expired"
    elif days <= 30:
        return "🟠 Critical"
    elif days <= 90:
        return "🟡 Warning"
    else:
        return "🟢 Active"

df["Risk Status"] = df["Days Remaining"].apply(get_status)
st.markdown("<h4 style='color:#F6EB9A; font-family:Georgia,serif; font-weight:700; margin-top:0rem; margin-bottom:-1.5rem;'>License Dashboard</h4>", unsafe_allow_html=True)
st.markdown("<div style='display:flex; gap:48%;'><p style='color:#fafaf7; font-size:0.85rem; font-weight:600; margin-bottom:-1rem;'>Filter by State</p><p style='color:#fafaf7; font-size:0.85rem; font-weight:600; margin-bottom:-1rem;'>Filter by Status</p></div>", unsafe_allow_html=True)
col_a, col_b = st.columns(2)

with col_a:
    state = st.selectbox(
        "",
        ["All"] + sorted(df["State"].dropna().unique().tolist())
    )
    

with col_b:
    status_filter = st.selectbox(
        "",
        ["All", "🔴 Expired", "🟠 Critical", "🟡 Warning", "🟢 Active"]
    )

filtered = df.copy()
if state != "All":
    filtered = filtered[filtered["State"] == state]
if status_filter != "All":
    filtered = filtered[filtered["Risk Status"] == status_filter]

display = filtered[[
    "Company Name", "State", "License Type",
    "License Number", "Expires", "Days Remaining", "Risk Status"
]].copy()

display = display.sort_values("Days Remaining")
display["Expires"] = display["Expires"].dt.strftime("%m/%d/%Y")
display["Days Remaining"] = display["Days Remaining"].fillna("—").astype(str).str.replace(".0", "", regex=False)

st.write(display.to_html(index=False), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

total = len(df)
expired = len(df[df["Risk Status"] == "🔴 Expired"])
critical = len(df[df["Risk Status"] == "🟠 Critical"])
active = len(df[df["Risk Status"] == "🟢 Active"])

st.markdown(f"""
    <div style="display:flex; gap:1rem; margin:1.5rem 0;">
        <div style="flex:1; background:#2d5be3; border-radius:12px; padding:1.25rem 1.5rem; border-top:4px solid #4fa3ff;">
            <div style="font-family:Inter,sans-serif; font-size:0.72rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:#a8c4ff; margin-bottom:0.5rem;">Total Licenses</div>
            <div style="font-family:DM Sans,sans-serif; font-size:2.5rem; font-weight:700; color:#fafaf7; line-height:1;">{total}</div>
        </div>
        <div style="flex:1; background:#2d5be3; border-radius:12px; padding:1.25rem 1.5rem; border-top:4px solid #ff4d4d;">
            <div style="font-family:Inter,sans-serif; font-size:0.72rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:#a8c4ff; margin-bottom:0.5rem;">Expired</div>
            <div style="font-family:DM Sans,sans-serif; font-size:2.5rem; font-weight:700; color:#ff4d4d; line-height:1;">{expired}</div>
        </div>
        <div style="flex:1; background:#2d5be3; border-radius:12px; padding:1.25rem 1.5rem; border-top:4px solid #ffaa33;">
            <div style="font-family:Inter,sans-serif; font-size:0.72rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:#a8c4ff; margin-bottom:0.5rem;">Critical (≤30 days)</div>
            <div style="font-family:DM Sans,sans-serif; font-size:2.5rem; font-weight:700; color:#ffaa33; line-height:1;">{critical}</div>
        </div>
        <div style="flex:1; background:#2d5be3; border-radius:12px; padding:1.25rem 1.5rem; border-top:4px solid #3ddc84;">
            <div style="font-family:Inter,sans-serif; font-size:0.72rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:#a8c4ff; margin-bottom:0.5rem;">Active</div>
            <div style="font-family:DM Sans,sans-serif; font-size:2.5rem; font-weight:700; color:#3ddc84; line-height:1;">{active}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.divider()
# AI Risk Check
st.divider()
st.markdown("<h4 style='color:#F6EB9A; font-family:Georgia,serif; font-weight:700; margin-top:-1rem; margin-bottom:-2.75rem;'>Compliance Risk Assessment</h4>", unsafe_allow_html=True)
selected_state = st.selectbox(
    "",
    sorted(df["State"].dropna().unique().tolist()),
    key="ai_state"
)



if st.button("Run Risk Check"):
    state_data = df[df["State"] == selected_state]
    license_summary = []
    for _, row in state_data.iterrows():
        license_summary.append(
            f"- {row['License Type']} ({row['State']}): expires {row['Expires'].strftime('%m/%d/%Y') if pd.notna(row['Expires']) else 'unknown'}, {int(row['Days Remaining']) if pd.notna(row['Days Remaining']) else 'unknown'} days remaining, status: {row['Risk Status']}"
        )
    license_text = "\n".join(license_summary)

    prompt = f"""You are a compliance operator reviewing a contractor's license portfolio...
Here is the current license data for licenses in {selected_state}:

{license_text}

Write a concise, plain-English compliance risk summary for this contractor. 
Flag any expired or critical licenses by name and state. 
Note what needs immediate attention and what looks healthy. 
Sound like an experienced operator, not a chatbot. Keep it under 150 words."""

    with st.spinner("Running risk check..."):
        try:
            
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            result = response.choices[0].message.content
            st.markdown(f"""
                <div style="background:#2d5be3; border-left:4px solid #4fa3ff; border-radius:8px; padding:1.25rem 1.5rem; margin-top:1rem;">
                    <div style="font-family:Inter,sans-serif; font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.1em; color:#F6EB9A; margin-bottom:0.5rem;">Risk Assessment — {selected_state}</div>
                    <div style="font-family:Inter,sans-serif; font-size:0.95rem; color:#fafaf7; line-height:1.7;">{result}</div>
                </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")
            # Jurisdiction Q&A
st.divider()
st.markdown("<h4 style='color:#F6EB9A; font-family:Georgia,serif; font-weight:700; margin-bottom:-2rem; margin-top:-1rem; margin-bottom:-1rem;'>Jurisdiction Intelligence</h4>", unsafe_allow_html=True)
question = st.text_input("", placeholder="e.g. How do I renew a general contractor license in North Carolina?")



if st.button("Get Answer", key="qa_button"):
    if question:
        qa_prompt = f"""You are a construction licensing and permitting compliance advisor with deep knowledge of contractor licensing requirements across U.S. states.

Answer this question clearly and specifically: {question}

You have worked inside high-liability environments where mistakes are expensive. Be direct and specific. If you know the answer, give it. If requirements vary by jurisdiction or change frequently, say so plainly and tell them what to verify. Do not hedge everything. Do not use the words streamline, optimize, or ensure. No bullet points. No headers. Write in plain prose like someone who actually knows this industry. Keep it under 200 words."""

        with st.spinner("Looking that up..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": qa_prompt}],
                    max_tokens=400
                )
                answer = response.choices[0].message.content
                st.markdown(f"""
                    <div style="background:#2d5be3; border-left:4px solid #4fa3ff; border-radius:8px; padding:1.25rem 1.5rem; margin-top:1rem;">
                        <div style="font-family:Inter,sans-serif; font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.1em; color:#4fa3ff; margin-bottom:0.5rem;">Compliance Guidance</div>
                        <div style="font-family:Inter,sans-serif; font-size:0.95rem; color:#fafaf7; line-height:1.7;">{answer}</div>
                        <div style="font-family:Inter,sans-serif; font-size:0.72rem; color:#a8c4ff; margin-top:0.75rem;">⚠️ AI-generated guidance. Verify all requirements directly with your state licensing board.</div>
                    </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a question first.")
# Renewal Timeline Engine
st.divider()
st.markdown("<h4 style='color:#F6EB9A; font-family:Georgia,serif; font-weight:700; margin-bottom:-1.75rem;'>Renewal Timeline Engine <span style='color:#a8c4ff; font-size:0.85rem; font-family:Inter,sans-serif; font-weight:400;'>— "" to generate a backwards renewal timeline with financial review milestones and a CPA checklist.</span></h4>", unsafe_allow_html=True)

license_options = df.apply(lambda row: f"{row['License Type']} — {row['State']} (expires {row['Expires'].strftime('%m/%d/%Y') if pd.notna(row['Expires']) else 'unknown'})", axis=1).tolist()
selected_license_idx = st.selectbox("", range(len(license_options)), format_func=lambda x: license_options[x], key="timeline_license")

if st.button("Generate Renewal Timeline", key="timeline_button"):
    selected_row = df.iloc[selected_license_idx]
    license_type = selected_row["License Type"]
    state = selected_row["State"]
    expires = selected_row["Expires"].strftime("%m/%d/%Y") if pd.notna(selected_row["Expires"]) else "unknown"
    days_remaining = int(selected_row["Days Remaining"]) if pd.notna(selected_row["Days Remaining"]) else "unknown"

    timeline_prompt = f"""You are a construction licensing compliance advisor who has managed multi-state contractor renewals. You know that missing a renewal deadline can shut down a project and trigger real liability.

The contractor needs to renew the following license:
- License Type: {license_type}
- State: {state}
- Expiration Date: {expires}
- Days Remaining: {days_remaining}

Do the following:
1. State whether this license requires a financial review or audit for renewal in {state}. Be specific.
2. If a financial review IS required, work backwards from the expiration date and provide a realistic timeline with specific target dates for: starting document collection, engaging a CPA, completing the financial review, submitting the renewal application, and the final deadline.
3. Provide a preparation checklist of what the contractor should gather before engaging a CPA — typical items include financial statements, P&L, balance sheet, bonding information, insurance certificates, and any state-specific documents.
4. Note anything specific to {state} that could slow the process down.

Write in plain prose. Be direct and specific. No hedging everything. Sound like someone who has actually done this before. Under 250 words."""

    with st.spinner("Building renewal timeline..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": timeline_prompt}],
                max_tokens=500
            )
            timeline_result = response.choices[0].message.content
            st.markdown(f"""
                <div style="background:#2d5be3; border-left:4px solid #F6EB9A; border-radius:8px; padding:1.25rem 1.5rem; margin-top:1rem;">
                    <div style="font-family:Inter,sans-serif; font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.1em; color:#F6EB9A; margin-bottom:0.75rem;">Renewal Timeline — {license_type} ({state})</div>
                    <div style="font-family:Inter,sans-serif; font-size:0.95rem; color:#fafaf7; line-height:1.7;">{timeline_result}</div>
                    <div style="font-family:Inter,sans-serif; font-size:0.72rem; color:#a8c4ff; margin-top:0.75rem;">⚠️ AI-generated guidance. Verify all requirements directly with your state licensing board and CPA.</div>
                </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")
st.markdown("<p style='font-family:Inter; color:#a8c4ff; font-size:0.8rem; text-align:center;'>shePERMITS &nbsp;|&nbsp; Automation isn't efficiency — it's insurance.</p>", unsafe_allow_html=True)
   