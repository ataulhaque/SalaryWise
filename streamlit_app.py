import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Set page configuration
st.set_page_config(page_title="Salary Wise", layout="centered", page_icon=':moneybag:')

# App Title
st.title("Personal Finance Calculator")
st.subheader("Calculate your In-Hand Salary with Visualizations and Configurable Options")

# Input for CTC
ctc = st.number_input("Enter your Annual CTC (₹):", min_value=0, step=1000)

# Sidebar: User-editable Salary Components
st.sidebar.header("Adjust Salary Component Percentages")
basic_salary_pct = st.sidebar.slider("Basic Salary (%)", min_value=20.0, max_value=50.0, value=40.0, step=0.5)
hra_pct = st.sidebar.slider("HRA (% of Basic)", min_value=30.0, max_value=60.0, value=50.0, step=0.5)
pf_pct = st.sidebar.slider("Provident Fund (PF) (%)", min_value=10.0, max_value=20.0, value=12.0, step=0.5)
gratuity_pct = st.sidebar.slider("Gratuity (%)", min_value=4.0, max_value=5.0, value=4.81, step=0.01)

# Save Configuration Option
if st.sidebar.button("Save Configuration"):
    config = {
        "CTC": ctc,
        "Basic Salary (%)": basic_salary_pct,
        "HRA (%)": hra_pct,
        "Provident Fund (PF) (%)": pf_pct,
        "Gratuity (%)": gratuity_pct,
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
    return {
        "Basic Salary": round(basic_salary, 2),
        "HRA": round(hra, 2),
        "Special Allowance": round(special_allowance, 2),
        "Provident Fund (PF)": round(pf, 2),
        "Gratuity": round(gratuity, 2),
    }

# Calculate salary components
if ctc > 0:
    salary_breakup = calculate_salary_breakup(ctc, basic_salary_pct, hra_pct, pf_pct, gratuity_pct)
    
    # Display salary breakup
    st.subheader("Salary Breakup")
    df = pd.DataFrame(salary_breakup.items(), columns=["Component", "Amount (₹)"])
    st.table(df)

    # Pie Chart for Salary Components
    st.subheader("Salary Components Distribution")
    fig, ax = plt.subplots()
    ax.pie(
        salary_breakup.values(),
        labels=salary_breakup.keys(),
        autopct="%1.1f%%",
        startangle=140,
        colors=["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854"],
    )
    ax.axis("equal")  # Equal aspect ratio ensures the pie is a circle.
    st.pyplot(fig)

    # Tax Calculation and In-Hand Salary
    tax = calculate_taxable_income(ctc)
    in_hand_salary = ctc - tax - salary_breakup["Provident Fund (PF)"] - salary_breakup["Gratuity"]

    st.subheader("Estimated In-Hand Salary")
    st.write(f"**In-Hand Annual Salary (₹):** {round(in_hand_salary, 2)}")
    st.write(f"**In-Hand Monthly Salary (₹):** {round(in_hand_salary / 12, 2)}")

    # Prepare Report CSV for Download
    report_data = {
        "Component": list(salary_breakup.keys()) + ["Tax Deducted", "In-Hand Annual Salary", "In-Hand Monthly Salary"],
        "Amount (₹)": list(salary_breakup.values()) + [tax, round(in_hand_salary, 2), round(in_hand_salary / 12, 2)],
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
