import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Set page configuration
st.set_page_config(page_title="Salary Wise", layout="centered", page_icon=':moneybag:')
st.info("To configure the salary components, expand the sidebar here :point_left:")

# App Title
st.title("Personal Finance Calculator")
st.subheader("Calculate your In-Hand Salary")

# Input for CTC
ctc = st.number_input("Enter your Annual CTC (₹):", min_value=0, step=1000)
raise_pct = st.number_input("Enter Appraisal Raise Percentage (if any)(%):", min_value=0.0, step=0.1)

# Calculate effective CTC based on raise percentage
effective_ctc = ctc + (ctc * (raise_pct / 100)) if raise_pct > 0 else ctc

# Sidebar: User-editable Salary Components
st.sidebar.header("Adjust Salary Component Percentages")
basic_salary_pct = st.sidebar.slider("Basic Salary (%)", min_value=20.0, max_value=50.0, value=40.0, step=0.5)
hra_pct = st.sidebar.slider("HRA (% of Basic)", min_value=30.0, max_value=60.0, value=50.0, step=0.5)
pf_pct = st.sidebar.slider("Provident Fund (PF) (%)", min_value=10.0, max_value=20.0, value=12.0, step=0.5)
gratuity_pct = st.sidebar.slider("Gratuity (%)", min_value=4.0, max_value=5.0, value=4.81, step=0.01)
voluntary_pf_pct = st.sidebar.slider("Voluntary PF (% of Basic)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
nps_pct = st.sidebar.slider("NPS (% of Basic)", min_value=0.0, max_value=10.0, value=0.0, step=0.5)

# Save Configuration Option
if st.sidebar.button("Save Configuration"):
    config = {
        "CTC": ctc,
        "Basic Salary (%)": basic_salary_pct,
        "HRA (%)": hra_pct,
        "Provident Fund (PF) (%)": pf_pct,
        "Gratuity (%)": gratuity_pct,
        "Voluntary PF (%)": voluntary_pf_pct,
        "NPS (%)": nps_pct,
    }
    pd.DataFrame([config]).to_csv("saved_config.csv", index=False)
    st.sidebar.success("Configuration Saved!")

# Load Configuration Option
if st.sidebar.button("Load Configuration"):
    try:
        saved_config = pd.read_csv("saved_config.csv").iloc[0]
        ctc = saved_config["CTC"]
        basic_salary_pct = saved_config["Basic Salary (%)"]
        hra_pct = saved_config["HRA (%)"]
        pf_pct = saved_config["Provident Fund (PF) (%)"]
        gratuity_pct = saved_config["Gratuity (%)"]
        voluntary_pf_pct = saved_config["Voluntary PF (%)"]
        nps_pct = saved_config["NPS (%)"]
        st.sidebar.success("Configuration Loaded!")
    except FileNotFoundError:
        st.sidebar.error("No configuration file found!")

# Function to calculate taxable income based on the New Tax Regime
def calculate_taxable_income(ctc):
    if ctc <= 300000:
        return 0
    elif ctc <= 700000:
        return (ctc - 300000) * 0.05
    elif ctc <= 1000000:
        return 20000 + (ctc - 700000) * 0.10
    elif ctc <= 1200000:
        return 50000 + (ctc - 1000000) * 0.15
    elif ctc <= 1500000:
        return 80000 + (ctc - 1200000) * 0.20
    else:
        return 140000 + (ctc - 1500000) * 0.30

# Function to calculate salary components
def calculate_salary_breakup(ctc, basic_pct, hra_pct, pf_pct, gratuity_pct):
    basic_salary = ctc * (basic_pct / 100)
    hra = basic_salary * (hra_pct / 100)
    pf = basic_salary * (pf_pct / 100)
    gratuity = basic_salary * (gratuity_pct / 100)
    special_allowance = ctc - (basic_salary + hra + pf + gratuity)
    tds = calculate_taxable_income(ctc)
    return {
        "Basic Salary": round(basic_salary, 2),
        "HRA": round(hra, 2),
        "Special Allowance": round(special_allowance, 2),
        "Provident Fund (PF)": round(pf, 2),
        "Gratuity": round(gratuity, 2),
        "Tax Deducted": round(tds, 2),
    }

# Calculate salary components
if effective_ctc > 0:
    salary_breakup = calculate_salary_breakup(effective_ctc, basic_salary_pct, hra_pct, pf_pct, gratuity_pct)
    
    # Display salary breakup
    st.subheader("Salary Breakup")
    monthly_breakup = {key: round(value / 12, 2) for key, value in salary_breakup.items()}  # Calculate monthly amounts
    df = pd.DataFrame({
        "Component": salary_breakup.keys(),
        "Amount Annual (₹)": salary_breakup.values(),
        "Amount Monthly (₹)": monthly_breakup.values(),  # New column for monthly amounts
    })
    st.table(df)

    # Pie Chart for Salary Components
    st.subheader("Salary Components Distribution")
    fig, ax = plt.subplots()
    ax.pie(
        salary_breakup.values(),
        labels=salary_breakup.keys(),
        autopct="%1.1f%%",
        startangle=140,
        colors=["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854", "#264b19"],
    )
    ax.axis("equal")  # Equal aspect ratio ensures the pie is a circle.
    st.pyplot(fig)

    # Tax Calculation and In-Hand Salary
    tax = calculate_taxable_income(effective_ctc)
    in_hand_salary = effective_ctc - tax - salary_breakup["Provident Fund (PF)"] - salary_breakup["Gratuity"]

    st.subheader("Estimated In-Hand Salary")
    st.write(f"**In-Hand Annual Salary (₹):** {round(in_hand_salary, 2)}")
    st.write(f"**In-Hand Monthly Salary (₹):** {round(in_hand_salary / 12, 2)}")

    # Prepare Report CSV for Download
    report_data = {
        "Component": list(salary_breakup.keys()) + ["In-Hand Annual Salary", "In-Hand Monthly Salary"],
        "Amount (₹)": list(salary_breakup.values()) + [round(in_hand_salary, 2), round(in_hand_salary / 12, 2)],
    }
    report_df = pd.DataFrame(report_data)
    csv = report_df.to_csv(index=False)

    # Download Button
    st.download_button(
        label="Download Report as CSV",
        data=csv,
        file_name="salary_breakup_report.csv",
        mime="text/csv",
    )
st.info("This app is designed to help you calculate your in-hand salary based on your annual CTC and various salary components. It also allows you to adjust the percentages of these components to see how they affect your take-home pay. You can also enter your appraisal raise percentage to see how it affects your in-hand salary. if you have any suggestions or feedback, please let me know.")
