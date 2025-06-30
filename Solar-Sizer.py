import streamlit as st
import math
from io import BytesIO
from fpdf import FPDF
import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Advanced Solar Sizing Tool", layout="centered")
st.title("☀️ Advanced Solar Panel + Battery Sizing Tool")

# --- User Inputs ---
with st.expander("🔧 Basic Configuration", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        daily_load = st.number_input("🔌 Daily Energy Use (kWh)", min_value=1.0, value=6.0, step=0.5)
        backup_days = st.number_input("🔋 Backup Days", min_value=1, value=2, step=1)
        battery_voltage = st.selectbox("⚡ Battery Voltage (V)", [12, 24, 48, 60, 72, 96], index=2)
        battery_type = st.selectbox("🔋 Battery Type", ["Lead-acid", "Lithium-ion"])
    with col2:
        sun_hours = st.slider("🌞 Sunlight Hours/Day", min_value=1.0, max_value=24.0, value=6.0, step=0.5)
        panel_wattage = st.selectbox("🔆 Panel Wattage (W)", [250, 300, 330, 400], index=2)
        peak_load_kw = st.number_input("⚡ Peak Load (kW)", min_value=0.5, value=2.0, step=0.1)

# --- Battery Type Defaults ---
if battery_type == "Lead-acid":
    dod = 0.8
    cost_per_ah_initial = 15
    dod_note = "Depth of Discharge (DOD) for Lead-acid battery is 80%."
else:
    dod = 0.9
    cost_per_ah_initial = 22
    dod_note = "Depth of Discharge (DOD) for Lithium-ion battery is 90%."

st.caption(dod_note)

# --- Efficiency & Cost Settings ---
with st.expander("⚙️ Advanced Efficiency Settings"):
    panel_eff = st.slider("📉 Panel Efficiency (%)", 50, 100, value=80) / 100
    inverter_eff = st.slider("🔌 Inverter Efficiency (%)", 50, 100, value=90) / 100

with st.expander("💰 Cost Settings"):
    cost_per_panel = st.number_input("🪙 Cost per Panel (Rs.)", min_value=1000, value=13000, step=500)
    cost_per_ah = st.number_input("🔋 Cost per Ah (Rs.)", min_value=1, value=cost_per_ah_initial, step=1)

# --- Calculations ---
panel_kw = daily_load / (sun_hours * panel_eff * inverter_eff)
num_panels = math.ceil(panel_kw * 1000 / panel_wattage)
battery_ah = math.ceil((daily_load * backup_days * 1000) / (battery_voltage * dod))
inverter_kw = peak_load_kw

cost_panel = num_panels * cost_per_panel
cost_battery = battery_ah * cost_per_ah
total_cost = cost_panel + cost_battery

# --- Output Display ---
st.subheader("📊 Sizing Results")
col1, col2 = st.columns(2)
col1.metric("🔆 Panel Capacity (kW)", f"{panel_kw:.2f}")
col1.metric("🔆 Number of Panels", f"{num_panels}")
col2.metric("🔋 Battery Capacity (Ah)", f"{battery_ah} @ {battery_voltage}V")
col2.metric("⚡ Inverter Size (kW)", f"{inverter_kw:.2f}")

# --- Detailed Cost Info ---
st.info(f"🪙 Panel Cost: {num_panels} × Rs. {cost_per_panel:,} = Rs. {cost_panel:,}")
st.info(f"🔋 Battery Cost: {battery_ah} × Rs. {cost_per_ah:,} = Rs. {cost_battery:,}")
st.success(f"💵 Total Estimated Cost: Rs. {total_cost:,}")

# --- PDF Report Generation ---
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Solar Sizing Report", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", align="C")

    def add_report(self, data):
        self.set_font("Arial", "", 12)
        for key, value in data.items():
            self.cell(80, 10, str(key), border=0)
            self.cell(0, 10, str(value), ln=True, border=0)

# --- Prepare PDF Report ---
report_data = {
    "Daily Load (kWh)": daily_load,
    "Sun Hours": sun_hours,
    "Panel Capacity (kW)": f"{panel_kw:.2f}",
    "Number of Panels": num_panels,
    "Panel Wattage (W)": panel_wattage,
    "Battery Capacity (Ah)": battery_ah,
    "Battery Voltage (V)": battery_voltage,
    "Battery Type": battery_type,
    "Inverter Size (kW)": f"{inverter_kw:.2f}",
    "Panel Cost (Rs.)": f"Rs. {cost_panel:,}",
    "Battery Cost (Rs.)": f"Rs. {cost_battery:,}",
    "Total System Cost (Rs.)": f"Rs. {total_cost:,}"
}

pdf = PDF()
pdf.add_page()
pdf.add_report(report_data)

pdf_buffer = BytesIO()
pdf_bytes = pdf.output(dest='S').encode('latin1')
pdf_buffer.write(pdf_bytes)
pdf_buffer.seek(0)

# --- PDF Download Button ---
st.download_button(
    label="📥 Download Results (PDF)",
    data=pdf_buffer,
    file_name="solar_sizing_report.pdf",
    mime="application/pdf"
)

# --- Email Sending Section ---
st.subheader("📧 Email this Report")
email = st.text_input("Enter your email to receive the report (feature requires SMTP setup)", placeholder="example@email.com")
if st.button("Send Email (requires SMTP setup in code)"):
    st.warning("📬 Email feature is not live in this app. Set up SMTP credentials in local environment to use.")
