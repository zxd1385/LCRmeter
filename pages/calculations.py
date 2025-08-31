import streamlit as st

st.title("📐 LCR Meter Calculations")

st.markdown("""
This page explains the main **calculations** behind the homemade LCR meter, using LaTeX formulas.
""")

# --- Angular frequency ---
st.header("Angular Frequency")
st.latex(r"\omega = 2 \pi f")

st.markdown("Where:")
st.markdown("- $f$: Signal frequency (Hz)")

st.header("Evaluating Network Function")
st.markdown("""As shown in the application page, the circuit consists of a 
10kΩ resistor (
R1) in parallel with a 
10μF capacitor (
C1), both connected in series with an unknown load to be identified. Suppose the load is resistive (
R2). The network function is then calculated as follows:""")
st.latex(r"""
H(j\omega) = \frac{V_{\mathrm{MIC}}}{V_{\mathrm{IN}}}
= \frac{R_1 \parallel Z_C}{(R_1 \parallel Z_C) + R_2}, 
\qquad Z_C = \frac{1}{j\omega C}
""")

st.latex(r"""
\Longrightarrow \;
H(j\omega) = \frac{R_1}{(R_1 + R_2) + j \omega C R_1 R_2}
= \frac{\tfrac{R_1}{R_1 + R_2}}{1 + j \omega \tfrac{C R_1 R_2}{R_1 + R_2}}
""")

st.latex(r"""
\text{where } 
\quad G_0 = \frac{R_1}{R_1 + R_2}, 
\quad \tau = \frac{C R_1 R_2}{R_1 + R_2}.
""")

st.latex(r"""
|H(j\omega)| = \frac{R_1}
{\sqrt{(R_1 + R_2)^2 + (\omega C R_1 R_2)^2}},
\qquad
\angle H(j\omega) = -\arctan\!\left(\frac{\omega C R_1 R_2}{R_1 + R_2}\right)
""")

st.markdown("Now, we use the magnitude response ∣H(jω)∣ to derive a quadratic equation in the unknown resistor and solve for its value. A similar procedure is applied for the other load types")
# --- Resistor ---
st.header("Resistive Impedance")
st.latex(r"Z_R = R")

st.markdown("Resistive impedance is purely real. The measured value is calculated using the amplitude ratio:")
st.latex(r"""
R_\text{measured} = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}, \quad
a = 100 + |Z_C|^2, \; b = 2|Z_C|^2, \; c = |Z_C|^2 - \left(\frac{|Z_C|}{\text{amplitude ratio}}\right)^2
""")

# --- Capacitor ---
st.header("Capacitive Impedance")
st.latex(r"Z_C = -\frac{j}{\omega C}")

st.markdown("Complex impedance calculation for a capacitor:")
st.latex(r"""
Z_\text{C,measured} = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}, \quad
C_\text{measured} = \frac{1}{|Z_\text{C,measured}| \, \omega}
""")

st.markdown("Where for capacitor:")
st.latex(r"""
a = (M^2)(1 + (R \omega C)^2), \quad
b = -2 M^2 R^2 \omega C, \quad
c = R^2 (M^2 - 1), \quad
M = \frac{A_\text{measured}}{A_\text{input}}
""")

# --- Inductor ---
st.header("Inductive Impedance")
st.latex(r"Z_L = j \omega L")

st.markdown("Complex impedance calculation for an inductor:")
st.latex(r"""
Z_\text{L,measured} = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}, \quad
L_\text{measured} = \frac{Z_\text{L,measured}}{\omega}
""")

# --- Parallel combination example ---
st.header("Parallel Combination (Resistor + Capacitor)")
st.latex(r"Z_\text{total} = \frac{1}{\frac{1}{R} + \frac{1}{Z_C}}")

# --- Auto-detection of load type ---
st.header("Load Detection Criteria")
st.markdown("""
The LCR meter detects the type of load based on amplitude or slope of impedance vs frequency:
- Capacitor: slope < -0.8 or apparent resistance between 0.5 and 2 Kohms
- Inductor: mean amplitude very small (apparent resistance is very small)
- Resistor: otherwise
""")
st.latex(r"""
\text{if } slope < -0.8 \quad \text{or } 0.5K < AP < 2K\rightarrow \text{Capacitor} \\
\text{if } |A_\text{mean}| < 10^{-2} \rightarrow \text{Inductor} \\
\text{else} \rightarrow \text{Resistor}
""")

# --- Summary ---
st.subheader("Summary")
st.markdown("""
- $Z_R$, $Z_C$, $Z_L$ are calculated from amplitude measurements and phasor relationships.
- Parallel and series combinations are calculated using standard formulas.
- Load type is auto-detected using amplitude and frequency response.
""")
