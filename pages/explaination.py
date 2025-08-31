import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="LCR Meter Project - Intro", layout="wide")

st.title("📘 Introduction to My Homemade LCR Meter")

st.markdown("""
Welcome to my homemade **LCR Meter Project**!  

This project demonstrates how to build and test an LCR meter using Python, Streamlit, and a simple audio interface for signal generation.  
It is aimed at **beginners** who want to learn about electronics, impedance measurement, and Python-based data visualization.
""")

# --- What is an LCR Meter ---
st.header("🔎 What is an LCR Meter?")
st.markdown("""
An **LCR Meter** measures the following properties of an electronic component:

- **L**: Inductance (Henry, H)  
- **C**: Capacitance (Farad, F)  
- **R**: Resistance (Ohm, Ω)  

It works by applying a known AC signal to a component and measuring the voltage and current response.
""")

# --- How this project works ---
st.header("⚙️ How My LCR Meter Works")
st.markdown("""
1. **Generate a signal**: We use a sine wave with a user-defined frequency, amplitude, and duration.  
2. **Inject the signal**: Send the signal through the unknown load.  
3. **Measure response**: Capture the resulting voltage/current waveform.  
4. **Calculate impedance**: Use phasor relationships to compute R, L, or C.  
5. **Display results**: Show measured values, errors, and statistics.
""")

# --- Example Sine Wave Code ---
st.header("💻 Key Code Snippet: Signal Generation")
st.code("""
import numpy as np

sample_rate = 44100  # Hz
duration = 3.0       # seconds
frequency = 10       # Hz

t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)
sin_wave = 0.2 * np.sin(2 * np.pi * frequency * t)
""", language="python")

# --- Plot example sine wave ---
st.subheader("Example Sine Wave Used")
t = np.linspace(0, 1, 1000, endpoint=False)
sin_wave = 0.5 * np.sin(2 * np.pi * 5 * t)
fig, ax = plt.subplots()
ax.plot(t, sin_wave)
ax.set_title("Example Sine Wave")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Amplitude")
st.pyplot(fig)

# --- Example Impedance Calculation ---
st.header("🔧 Key Code Snippet: Impedance Calculation")
st.markdown("The impedance of a capacitor is $Z_C = \\frac{1}{j \\omega C}$")
st.markdown("The impedance of an inductor is $Z_L = j \\omega L$")
st.code("""
# For a capacitor C1
w = 2 * np.pi * frequency
Z_C1 = -1j / (w * C1)

# For a resistor R1
Z_R1 = R1

# Total impedance for series or parallel combinations
Z_total = 1 / (1/Z_R1 + 1/Z_C1)
""", language="python")

# --- Tips for Starters ---
st.header("💡 Tips for Beginners")
st.markdown("""
- Start by understanding **AC signals and phasors**.  
- Use **small test components** when measuring, like 1kΩ resistors or 10µF capacitors.  
- Adjust **frequency and amplitude** carefully to avoid saturating your ADC/sound card.  
- Print **plots of your waveform** to understand the signal behavior.
""")

st.info("This page is meant as a beginner-friendly introduction to the project. Use the Home and Test pages to experiment with real measurements!")
