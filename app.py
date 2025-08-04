from dependencies.LCRmeter import LCR_Meter
import streamlit as st
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft,rfftfreq
from scipy.signal import chirp
import time
import math

st.header("***Hellow there!!***")


# basic variables...
with st.form(key="signal_form"):
    st.markdown("<h3>Signal_Variables</h3>", unsafe_allow_html=True)
    sample_rate = st.number_input(label="sample-rate_frequency",min_value=10000, max_value= 55000, step=100, value=44500)
    duraton = st.slider(label="duration",min_value=1.0, max_value=5.0, value=3.0, step=0.1, format="%.1f")
    frequency = st.slider(label="frequency",min_value=1, max_value=50, value=10, step=1, format="%.1f")
    amplitude = st.slider(label="Amplitude",min_value=0.01, max_value=1.0, value=.2, step=.01)
    submit = st.form_submit_button("Submit")


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


if submit:
    with st.status("Process started...", expanded=True) as status:
        
        t = np.linspace(0,duraton,int(sample_rate*duraton),endpoint=False)
        st.write("generating time steps...")
        lcr_meter = LCR_Meter()
        
        lcr_meter.generate_sin_wave(t)
        status.write("generating sin wave...")
        
        lcr_meter.inject_streo_signal("sin")
        st.write("injecting signal to the circuit...")
        
        lcr_meter.find_amplitude_accuracy(t)
        Rl = lcr_meter.caculate_resistive_impedance(Z_C1, .199)
        Cl = lcr_meter.caculate_complex_impedance(R1, C1, .199 ,type="C")
        Ll = lcr_meter.caculate_complex_impedance(R1, C1, .199 ,type="L")
        kind = lcr_meter.auto_detect_load_with_amplitude(abs(Z_C1))
        st.write("finding && detecting load impedance...")
        status.update(label="done succesfuly...", expanded=False, state="complete" )
    st.info(f"kind is {kind} and resistance is {Rl} and capacitance is {Cl[1]} and inductance is {Ll[1]}")
    fig, ax = plt.subplots()
    ax.plot(t,lcr_meter.results)
    ax.plot(t,lcr_meter.sinWave)
    st.pyplot(fig)
    