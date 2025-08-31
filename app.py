from dependencies.LCRmeter import LCR_Meter
import streamlit as st
import streamlit.components.v1 as components
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft,rfftfreq
from scipy.signal import chirp
import time
import math

animation_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  :root {
    --wire-stroke: 2.5;
    --elem-stroke: 2.5;
    --label-size: 13px;
  }
  body { margin: 0; }
  .wrap { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto; padding: 8px 10px 4px; }
  .toolbar {
    display: flex; gap: 10px; align-items: center; margin-bottom: 8px; flex-wrap: wrap;
  }
  .toolbar button {
    border: 0; padding: 8px 12px; border-radius: 10px; cursor: pointer; background: #111; color: #fff;
    box-shadow: 0 2px 8px rgba(0,0,0,.12);
  }
  .toolbar input[type="range"] { width: 180px; }
  .toolbar .speed { font-size: 13px; opacity:.8; }

  svg { width: 100%; height: 380px; border-radius: 12px; background: #fff; box-shadow: inset 0 0 0 1px #eee; }

  .wire, .resistor, .capacitor { fill: none; stroke: #111; stroke-linecap: round; stroke-linejoin: round; }
  .wire       { stroke-width: var(--wire-stroke); }
  .resistor   { stroke-width: var(--elem-stroke); }
  .capacitor  { stroke-width: var(--elem-stroke); }
  .node { fill: #111; }
    .wave {
  stroke: red;
  stroke-width: 2;
  fill: none;
}

  

  .label { font-size: var(--label-size); font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; fill: #111; opacity: 0; transition: opacity .25s ease; }

  /* dash-draw is handled via JS by setting stroke-dasharray/offset and transitions */
</style>
</head>
<body>
<div class="wrap">
  

  <svg viewBox="0 0 520 300" id="stage" aria-label="Animated circuit">
    <!-- Sine wave injection at IN node -->
    <path id="in_wave" class="wave" d="" stroke="red" stroke-width="2" fill="none" opacity="0.8"/>
    <!-- IN/OUT/MIC nodes -->
    <circle id="node_in"  class="node" cx="40"  cy="150" r="3.5"/>
    <circle id="node_out" class="node" cx="480" cy="150" r="3.5"/>
    <circle id="node_out" class="node" cx="236" cy="150" r="3.5"/>
    <!-- Step 1: input wire -->
    <path id="wire_in" class="wire" d="M 40 150 L 120 150"/>

    <!-- Step 2: split up/down -->
    <path id="split_up"   class="wire" d="M 120 150 L 120 85"/>
    <path id="split_down" class="wire" d="M 120 150 L 120 215"/>

    <!-- Step 3: R1 (zigzag on top branch) and top branch return -->
    <!-- R1 zigzag from (120,85) to (210,85) -->
    <path id="r1" class="resistor" d="
      M 120 85
      l 15 0 l 10 -10 l 10 10 l 10 -10 l 10 10 l 10 -10 l 10 10 l 10 -10 l 10 10 l 20 0
    "/>
    <!-- drop back to the join at y=150 -->
    <path id="top_drop" class="wire" d="M 236 85 L 236 150"/>

    <!-- Step 4: C1 (bottom branch) and bottom branch return -->
    <!-- small wire right from split to plates -->
    <path id="c1_lead_l" class="wire" d="M 120 215 L 165 215"/>
    <!-- capacitor plates -->
    <line id="c1_plate1" class="capacitor" x1="165" y1="198" x2="165" y2="232"/>
    <line id="c1_plate2" class="capacitor" x1="178" y1="198" x2="178" y2="232"/>
    <!-- wire from plates to right vertical join -->
    <path id="c1_lead_r" class="wire" d="M 178 215 L 235 215"/>
    <path id="bot_rise"  class="wire" d="M 236 215 L 236 150"/>

    <!-- Step 5: short horizontal from join to R2 -->
    <path id="to_r2" class="wire" d="M 236 150 L 290 150"/>

    <!-- Step 6: R2 (zigzag in series) -->
    <!--R2_PLACEHOLDER-->

    <!-- Step 7: output wire -->
    <path id="wire_out" class="wire" d="M 370 150 L 480 150"/>

    <!-- Labels (fade in at the end) -->
    <text id="label_in"  class="label" x="28"  y="138">GND</text>
    <text id="v_in"  class="label" x="380"  y="100">VIN=ampspecsin(2pifreqspect)</text>
    <text id="label_out" class="label" x="486" y="138">IN</text>
    <text id="label_mic" class="label" x="240" y="138">MIC</text>
    <text id="label_r1"  class="label" x="150" y="68">R1=10K</text>
    <text id="label_c1"  class="label" x="158" y="248">C1=10uF</text>
    <text id="label_r2"  class="label" x="318" y="126">unknown</text>
    <!-- === Energy pulse overlay === -->
    
  </svg>
</div>

<script>
// === Sine Wave Animation ===
function animateWave() {
  const wave = document.getElementById("in_wave");
  let t = 0;
  function frame() {
    const points = [];
    const amp = 12;   // amplitude (height of wave)
    const wl  = 25;   // wavelength (px per cycle)
    const len = 70;  // how far to draw wave (px)
    for (let x = 0; x <= len; x += 2) {
      const y = 150 - Math.sin((x/ wl) * 2 * Math.PI + t) * amp;
      points.push(`${165 + x},${y}`);
    }
    wave.setAttribute("d", "M " + points.join(" L "));
    t += 0.15;  // speed
    requestAnimationFrame(frame);
  }
  frame();
}



(function() {
  const stage = document.getElementById('stage');

  // Elements to animate, grouped into steps (movie frames)
  const steps = [
    { ids: ['wire_in'],                     dur: 600 },
    { ids: ['split_up','split_down'],       dur: 500 },
    { ids: ['r1','top_drop'],               dur: 900 },
    { ids: ['c1_lead_l','c1_plate1','c1_plate2','c1_lead_r','bot_rise'], dur: 900 },
    { ids: ['to_r2'],                       dur: 400 },
    { ids: ['r2'],                           dur: 900 },
    { ids: ['wire_out'],                    dur: 600 },
    { ids: ['label_in','v_in','label_out','label_mic','label_r1','label_c1','label_r2'], dur: 250, labels: true },
  ];

  const toAnimate = steps.flatMap(s => s.ids.map(id => document.getElementById(id)));

  // Prepare line-like SVGs for stroke-draw animation
  function prepStroke(el) {
    if (!el) return;
    if (el.tagName === 'text') {
      el.style.opacity = 0;
      return;
    }
    const total = (typeof el.getTotalLength === 'function') ? el.getTotalLength() : 0;
    el.style.strokeDasharray  = total;
    el.style.strokeDashoffset = total;
    el.style.transition = 'none';
  }

  function resetScene() {
    toAnimate.forEach(prepStroke);
    // force reflow so subsequent transitions apply
    stage.getBoundingClientRect();
  }

  function drawStroke(el, ms) {
    return new Promise(resolve => {
      if (el.tagName === 'text') {
        el.style.transition = `opacity ${ms}ms ease`;
        el.style.opacity = 1;
        setTimeout(resolve, ms);
        return;
      }
      const total = (typeof el.getTotalLength === 'function') ? el.getTotalLength() : 0;
      el.style.transition = `stroke-dashoffset ${ms}ms cubic-bezier(.4,.0,.2,1)`;
      requestAnimationFrame(() => {
        el.style.strokeDashoffset = 0;
      });
      setTimeout(resolve, ms);
    });
  }

  function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
  }

  async function playAll(speed=1) {
    for (const step of steps) {
      const ms = Math.max(60, step.dur / speed);
      await Promise.all(step.ids.map(id => drawStroke(document.getElementById(id), ms)));
      await sleep(90 / speed);
    }
  }

  // Initial setup and automatic play
  resetScene();
  window.addEventListener('load', () => {
  playAll(1);
  animateWave();
  });
})();
</script>

</body>
</html>
"""

st.header("***LCRmeter Dashboard***")


# basic variables...
with st.form(key="signal_form"):
    st.markdown("<h3>Signal_Variables</h3>", unsafe_allow_html=True)
    loads = ["Resistance (R)", "Capacitance (C)", "Inductance (L)", "Auto-Detect Load"]
    load_type = st.selectbox(
        "Select Load Type:",
        options= loads,
        index=3
    )
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
        
        amc = lcr_meter.find_amplitude_accuracy(t)
        Rl = lcr_meter.caculate_resistive_impedance(Z_C1, .199)
        Cl = lcr_meter.caculate_complex_impedance(R1, C1, .199 ,type="C")
        Ll = lcr_meter.caculate_complex_impedance(R1, C1, .199 ,type="L")
        kind = lcr_meter.auto_detect_load_with_amplitude(abs(Z_C1))
        st.write("finding && detecting load impedance...")
        status.update(label="done succesfuly...", expanded=False, state="complete" )
    s = ""
    if load_type == loads[3]:
        
        if kind == "Capacitor":
            s = f"Capacitance is {Cl[1]*1.1}F"
            animation_html = (animation_html
                        .replace("unknown", f"C={Cl[1]*1.1:.2e}F")
                        .replace("ampspec", f"{amplitude}")
                        .replace("freqspec", f"{frequency}")
                        .replace("<!--R2_PLACEHOLDER-->", """
    <path id="r2" class="capacitor" d="
  M 236 150
  L 320 150
  M 320 135 L 320 165
  M 330 135 L 330 165
  M 330 150 L 480 150
"/>
    """)
                         )
            components.html(animation_html, height=430)
        elif kind == "Resistor":
            s = f"Resistance is {Rl.real*1.08}K"
            animation_html = (animation_html
                        .replace("unknown", f"R={Rl.real*1.08:.2f}K")
                        .replace("ampspec", f"{amplitude}")
                        .replace("freqspec", f"{frequency}")
                        .replace("<!--R2_PLACEHOLDER-->", """
    <path id="r2" class="resistor" d="
      M 290 150
      l 10 -10 l 10 10 l 10 -10 l 10 10 l 10 -10 l 10 10 l 10 -10 l 10 10
    "/>
    """)
                         )
            components.html(animation_html, height=430)
        else :
            s = f"inductance is {Ll[1]}H"
            animation_html = (animation_html
                        .replace("unknown", f"L={Ll[1]*1.1:.2e}H")
                        .replace("ampspec", f"{amplitude}")
                        .replace("freqspec", f"{frequency}")
                        .replace("<!--R2_PLACEHOLDER-->", """
    <path id="r2" class="inductor" fill="none" stroke="#111" stroke-width="2.5" d="
  M 236 150
  L 290 150
  A 10 10 0 0 1 310 150
  A 10 10 0 0 1 330 150
  A 10 10 0 0 1 350 150
  A 10 10 0 0 1 370 150
  L 480 150
"/>


    """)
                         )
            components.html(animation_html, height=430)
        st.info(f"Load is {kind} and {s}")
    
    if load_type == loads[0]:
        animation_html = (animation_html
                        .replace("unknown", f"R={Rl.real*1.08:.2f}K")
                        .replace("ampspec", f"{amplitude}")
                        .replace("freqspec", f"{frequency}")
                        .replace("<!--R2_PLACEHOLDER-->", """
    <path id="r2" class="resistor" d="
      M 290 150
      l 10 -10 l 10 10 l 10 -10 l 10 10 l 10 -10 l 10 10 l 10 -10 l 10 10
    "/>
    """)
                         )
        components.html(animation_html, height=430)
        s = f"Resistance is {Rl.real*1.08}Kohms"
        st.info(f"{s}")
        
    if load_type == loads[1]:
        s = f"Capacitance is {Cl[1]*1.1}F"
        animation_html = (animation_html
                        .replace("unknown", f"C={Cl[1]*1.1:.2e}F")
                        .replace("ampspec", f"{amplitude}")
                        .replace("freqspec", f"{frequency}")
                        .replace("<!--R2_PLACEHOLDER-->", """
    <path id="r2" class="capacitor" d="
  M 236 150
  L 320 150
  M 320 135 L 320 165
  M 330 135 L 330 165
  M 330 150 L 480 150
"/>
    """)
                         )
        components.html(animation_html, height=430)
        st.info(f"{s}")
        
    if load_type == loads[2]:
        s = f"Inductance is {Ll[1]}H"
        animation_html = (animation_html
                        .replace("unknown", f"L={Ll[1]*1.1:.2e}H")
                        .replace("ampspec", f"{amplitude}")
                        .replace("freqspec", f"{frequency}")
                        .replace("<!--R2_PLACEHOLDER-->", """
    <path id="r2" class="inductor" fill="none" stroke="#111" stroke-width="2.5" d="
  M 236 150
  L 290 150
  A 10 10 0 0 1 310 150
  A 10 10 0 0 1 330 150
  A 10 10 0 0 1 350 150
  A 10 10 0 0 1 370 150
  L 480 150
"/>


    """)
                         )
        components.html(animation_html, height=430)
        st.info(f"{s}")
        

    fig, ax = plt.subplots()
    ax.plot(t,lcr_meter.results)
    ax.plot(t,lcr_meter.sinWave)
    st.pyplot(fig)
    





