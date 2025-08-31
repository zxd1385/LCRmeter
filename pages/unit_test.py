import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from dependencies.LCRmeter import LCR_Meter
import time
import io

st.header("🔬 LCR Meter Test Page")

# --- Form for Test Inputs ---
with st.form(key="lcr_test_form"):
    st.markdown("<h3>Test Parameters</h3>", unsafe_allow_html=True)
    
    loads = ["Resistance (R)", "Capacitance (C)", "Inductance (L)"]
    load_type = st.selectbox(
        "Select Load Type For Testing:",
        options= loads,
        index=1
    )

    known_value = st.number_input("Enter Known Load Value", min_value=0.000000001, value=0.01, step=0.000000001, format="%.9f")
    test_count = st.number_input("Number of Tests", min_value=1, max_value=50, value=5, step=1)
    
    sample_rate = st.number_input("Sample Rate (Hz)", min_value=10000, max_value=55000, value=44500, step=100)
    duration = st.slider("Duration (s)", min_value=1.0, max_value=5.0, value=3.0, step=0.1)
    frequency = st.slider("Frequency (Hz)", min_value=1, max_value=50, value=10, step=1)
    amplitude = st.slider("Amplitude", min_value=0.01, max_value=1.0, value=0.2, step=0.01)

    submit = st.form_submit_button("Start Test")

# --- Run Test ---
if submit:
    st.info(f"Running {test_count} tests against known load = {known_value:.9f}")
    
    w = 2*np.pi*frequency
    num_harmonics = 1500
    f_start = 5    # Hz
    f_end = 10000


    # internal impedance elements:
    R1 = R2 = 10_000
    C1 = C2 = 0.00001
    L1 = 1e-4
# transform to phasore domain:
    Z_R1 = Z_R2 = R1
    Z_C1 = Z_C2 = -1/(w*C1) * (1j)
    Z_L1 = L1*w*(1j)
    Z_intmd = Z_C1
    Z_t = 1/(1/Z_R1 + 1/Z_intmd )
    results_log = []

    with st.status("Running tests...", expanded=True) as status:
        for i in range(test_count):
            t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
            
            lcr_meter = LCR_Meter()
            lcr_meter.generate_sin_wave(t)
            lcr_meter.inject_streo_signal("sin")
            lcr_meter.find_amplitude_accuracy(t)
            measured_val = lcr_meter.caculate_complex_impedance(R1, C1, .199 ,type="C") if load_type == loads[1] else lcr_meter.caculate_resistive_impedance(Z_C1, .199)  # hypothetical output
            
            # Example: compare to known load
            error = abs(((measured_val[1] if load_type == loads[1] else measured_val) - known_value) / known_value) * 100
            
            results_log.append({
                "Test #": i + 1,
                "Measured": measured_val,
                "Known": known_value,
                "Error %": error
            })
            
            status.write(f"✅ Test {i+1} done. Measured: {(measured_val[1] if load_type == loads[1] else measured_val):.9f}")
            time.sleep(0.5)

        status.update(label="All tests completed!", expanded=False, state="complete")

    # --- Display Results Table ---
    import pandas as pd
    df = pd.DataFrame(results_log)
    st.dataframe(df)

    # --- Summary statistics ---
    st.subheader("📈 Statistical Report")

    measured_vals = df["Measured"].values
    error_vals = df["Error %"].values

    stats = {
        "Measured Mean": np.mean(measured_vals),
        "Measured Median": np.median(measured_vals),
        "Measured Variance": np.var(measured_vals, ddof=1),   # sample variance
        "Measured Std Dev": np.std(measured_vals, ddof=1),    # sample std
        "Error Mean (%)": np.mean(error_vals),
        "Error Median (%)": np.median(error_vals),
        "Error Variance": np.var(error_vals, ddof=1),
        "Error Std Dev": np.std(error_vals, ddof=1),
    }

    stats_df = pd.DataFrame(stats, index=["Value"]).T
    st.table(stats_df)

    # --- Plot Measured vs Known ---
    fig, ax = plt.subplots()
    ax.plot(df["Test #"], df["Measured"], "o-", label="Measured")
    ax.hlines(known_value, 1, test_count, colors="r", linestyles="--", label="Known")
    ax.set_xlabel("Test Number")
    ax.set_ylabel("Value")
    ax.legend()
    st.pyplot(fig)


    # --- Export Options ---
    # Let user enter file name
    default_name = "lcr_test_results"
    file_name = default_name

# --- CSV Export ---
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv,
        file_name=f"{file_name}.csv",
        mime="text/csv",
    )

# --- Excel Export ---
    try:
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, sheet_name="LCR Results")
        st.download_button(
            label="⬇️ Download as Excel",
            data=excel_buffer.getvalue(),
            file_name=f"{file_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except ImportError:
        st.warning("⚠️ Install `openpyxl` to enable Excel export: `pip install openpyxl`")
