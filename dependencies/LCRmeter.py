import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft,rfftfreq
from scipy.signal import chirp
import time
import math

# basic variables...
sample_rate = 44100
duraton = 3
frequency = 10
w = 2*np.pi*frequency
amplitude = .2
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






class LCR_Meter():
    def __init__(self):
        self.sinWave = 0
        self.sweep_signal = 0
        self.results = 0
        self.streoSignal = 0
        self.AM = 0
    def generate_sin_wave(self, time):
        self.sinWave = amplitude*np.sin(w*time)
    def generate_chirp_signal(self, time):
        self.sweep_signal = amplitude * chirp(time, f0=f_start, f1=f_end, t1=duraton, method='logarithmic')
    def inject_streo_signal(self, type):
        if type == "sin":
            self.streoSignal = np.column_stack((self.sinWave,np.zeros_like(self.sinWave)))
            self.results = sd.playrec(self.streoSignal,samplerate=sample_rate,channels=1,dtype='float32')
            sd.wait()
        if type == "chirp":
            self.streoSignal = np.column_stack((self.sweep_signal,np.zeros_like(self.sweep_signal)))
            self.results = sd.playrec(self.streoSignal,samplerate=sample_rate,channels=1,dtype='float32')
            sd.wait()
    def caculate_resistive_impedance(self,Zc, ampl):
    
        mgni = self.AM/ampl
        a = 100+Zc**2
        b = 2*Zc**2
        c = Zc**2-(Zc/mgni)**2
        delta = np.sqrt(b**2-4*a*c)
        R1_out = 0
        if ((-b+delta)/(2*a) > 0) : 
            R1_out = (-b+delta)/(2*a)
        else :
            R1_out = (-b-delta)/(2*a)
        return R1_out    
    def find_amplitude_accuracy(self, time):
        t_filterd = time[120000::]

        sin_vec = np.sin(w * t_filterd)
        cos_vec = np.cos(w * t_filterd)

        A = np.vstack([cos_vec, sin_vec]).T  
        coeffs, residuals, rank, s = np.linalg.lstsq(A, self.results[120000:, 0].flatten() , rcond=None)
        C, D = coeffs
        amplitude_accuracey = np.sqrt(C**2 + D**2)
        phase_diff = np.arctan2(C, D)  # radians
        self.AM = amplitude_accuracey
        return amplitude_accuracey
    def caculate_complex_impedance(self, R, C, ampl, type="C"):
        mgni = self.AM/ampl
        print((R*w*C)**2)
        a = (mgni**2)*(1+(R*w*C)**2)
        b = -2*mgni**2 *(R*R*w*C)
        c = R**2 *(mgni**2-1)
        delta = np.sqrt(b**2-4*a*c)
        z1 = (-b+delta)/(2*a)
        z2 = (-b-delta)/(2*a)
        Z_out = 0
        LC = 0
        if type == "L": 
            Z_out = max(z1,z2)
            LC = Z_out/w
        
        else :
            Z_out = min(z1, z2)
            LC = abs(1/(Z_out*w))

        return Z_out, LC
    def auto_detect_load(self, recorded_sig, input_sig, R):
        output_signal = recorded_sig.flatten()



# === Sliding window sine fitting ===
        window_size = int(0.05 * sample_rate)  # 50ms window
        step = int(0.02 * sample_rate)         # 20ms hop

        frequencies = []
        gains = []


# window_size = 2048
# step = 1024
        amplitudes = []

        for i in range(0, len(t) - window_size, step):
            segment = output_signal[i:i + window_size]
            amp = np.max(np.abs(segment))  # or np.sqrt(mean(square)) for RMS
            amplitudes.append(amp)
        mean_amplitude = sum(amplitudes) / len(amplitudes)
        print(mean_amplitude,"mean amp")


        for i in range(0, len(t) - window_size, step):
            t_win = t[i:i+window_size]
            x_win = input_sig[i:i+window_size]
            y_win = output_signal[i:i+window_size]
    
    # Instantaneous frequency of log chirp: f(t) = f0*(f1/f0)^(t/T)
            time_center = t_win[window_size // 2]
            inst_freq = f_start * (f_end / f_start) ** (time_center / duraton)
            omega = 2 * np.pi * inst_freq
    
    # Build basis vectors
            sin_basis = np.sin(omega * t_win)
            cos_basis = np.cos(omega * t_win)
            A = np.vstack([cos_basis, sin_basis]).T
    
    # Least squares for input and output
            in_coeffs, _, _, _ = np.linalg.lstsq(A, x_win, rcond=None)
            out_coeffs, _, _, _ = np.linalg.lstsq(A, y_win, rcond=None)

            amp_in = np.sqrt(in_coeffs[0]**2 + in_coeffs[1]**2)
            amp_out = np.sqrt(out_coeffs[0]**2 + out_coeffs[1]**2)

            gain = amp_out / amp_in if amp_in > 1e-5 else 0

            frequencies.append(inst_freq)
            gains.append(gain)

        frequencies = np.array(frequencies)
        gains = np.array(gains)

# === Estimate impedance magnitude ===
        Z_unknown_mag = gains * R / np.sqrt(1 - gains**2)

# === Identify element type ===
        log_f = np.log10(frequencies[5:])
        log_Z = np.log10(Z_unknown_mag[5:])
        slope, _ = np.polyfit(log_f, log_Z, 1)
        if slope < -0.8:
            return "Capacitor"
        elif abs(mean_amplitude)<1e-2 :
            return "Inductor"
        else:
            return "Resistor"
    def auto_detect_load_with_amplitude(self, Zc):
        R_virtual = self.caculate_resistive_impedance(abs(Zc),.199)
        if R_virtual > 2 :
            return "Resistor"
        elif 0.2 < R_virtual < 2 :
            return "Capacitor"
        else :
            return "Inductor"


if __name__ == "__main__" :
    t = np.linspace(0,duraton,int(sample_rate*duraton),endpoint=False)
    lcr_meter = LCR_Meter()
    lcr_meter.generate_sin_wave(t)
    lcr_meter.inject_streo_signal("sin")
    lcr_meter.find_amplitude_accuracy(t)
    Rl = lcr_meter.caculate_resistive_impedance(Z_C1, .199)
    Cl = lcr_meter.caculate_complex_impedance(R1, C1, .199 ,type="C")
    Ll = lcr_meter.caculate_complex_impedance(R1, C1, .199 ,type="L")
    kind = lcr_meter.auto_detect_load_with_amplitude(abs(Z_C1))
    print(f"load is {kind}...")
    print(f"resistance is {Rl}")
    print(f"capacitance is {Cl[1]}")
    print(f"inductance is {Ll[1]}")
    plt.plot(t,lcr_meter.results)
    plt.plot(t,lcr_meter.sinWave)
    plt.show()







# calculating external impedance







    

# print(f"kind is {auto_detect_load(results, sweep_signal, 10_000)}")













# print(f"complex impedance (if C!) is {caculate_complex_impedance(R1,C1,amplitude_accuracey,.199, "C")[0]} and capacitance is {caculate_complex_impedance(R1,C1,amplitude_accuracey,.199, "C")[1]}, complex impedance (if L!) is {caculate_complex_impedance(R1,C1,amplitude_accuracey,.199, "L")[0]} and inductance is {caculate_complex_impedance(R1,C1,amplitude_accuracey,.199, "L")[1]}")
# print(f"real impedance is {caculate_resistive_impedance(abs(Z_C1),amplitude_accuracey,.199)} and Resistance is {caculate_resistive_impedance(abs(Z_C1),amplitude_accuracey,.199)}")

