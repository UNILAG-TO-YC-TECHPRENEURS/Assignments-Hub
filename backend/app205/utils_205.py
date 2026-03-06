"""Utility functions for COS205 assignment generation"""
import os
import math
import cmath
import time
import random
import textwrap
import re
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from datetime import datetime

# Set matplotlib backend FIRST
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import graphviz
import nbformat as nbf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# ---------- Path to the provided dataset ----------
DATASET_PATH = Path(__file__).parent / 'data' / 'energy_dataset.csv'

# ---------- Configuration ----------
MAX_FFT_POINTS = 1024  # must be a power of two for FFT
NUM_THREADS    = 8     # threads for parallel DFT (ThreadPoolExecutor — safe inside Celery)

# ---------- Text Cleaning ----------
def clean_analysis_text(text):
    """Remove markdown formatting."""
    if not text:
        return text
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    text = re.sub(r'`{1,3}(.*?)`{1,3}', r'\1', text)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s+', ' ', text)
    if text and not text[-1] in '.!?':
        text += '.'
    return text.strip()

# ---------- OpenAI Analysis ----------
def generate_analysis():
    prompt = f"""You are a Nigerian university student writing the analysis section of a COS205 assignment.
The task involves implementing Discrete Fourier Transform (DFT) from scratch, then implementing Fast Fourier Transform (FFT) (also from scratch), and comparing their performance with library implementations (numpy.fft). You are given a dataset of hourly energy demand provided by the lecturer. The dataset has over 267,000 rows, so for practical computation you downsampled it to {MAX_FFT_POINTS} points (the next power of two) before applying DFT/FFT. You also implemented a parallel version of DFT using Python's ThreadPoolExecutor with {NUM_THREADS} threads to speed up the computation and demonstrate parallelization.

Write an analysis explaining:
- The concept of Fourier Transform and why it's useful for analyzing time series data like energy demand.
- The mathematical definition of DFT (formula) and its computational complexity O(N²).
- The FFT algorithm (Cooley-Tukey) and how it reduces complexity to O(N log N).
- Your step-by-step plan: load the provided dataset, downsample to {MAX_FFT_POINTS} points, implement DFT using nested loops (and also a parallel version using ThreadPoolExecutor), implement FFT using recursion (with zero-padding to make the length a power of two), measure execution time, plot magnitude spectra, compare with numpy's FFT.
- Expected observations: peaks corresponding to daily cycles, time difference between DFT and FFT, and speedup from parallelization.
- Constraints: handling of complex numbers in Python, downsampling to keep computation feasible.

The tone should be natural, like a student explaining their understanding. Avoid markdown formatting. Length: 300-400 words."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Nigerian university student. Write in plain text only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=700
    )
    raw = response.choices[0].message.content
    return clean_analysis_text(raw)

# ---------- Load Dataset ----------
def load_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH)
    if 'Balancing Authority' in df.columns:
        top_ba = df['Balancing Authority'].value_counts().idxmax()
        df = df[df['Balancing Authority'] == top_ba].copy()
    required = ['Hour Number', 'Demand (MW)']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Dataset missing required column: {col}")
    df['Demand (MW)'] = pd.to_numeric(df['Demand (MW)'], errors='coerce')
    df = df.dropna(subset=['Demand (MW)'])
    if 'Data Date' in df.columns:
        df['Data Date'] = pd.to_datetime(df['Data Date'], format='%m-%d-%y', errors='coerce')
        df = df.sort_values(['Data Date', 'Hour Number']).reset_index(drop=True)
    hours  = df['Hour Number'].values
    demand = df['Demand (MW)'].values.tolist()
    return hours, demand

def downsample(signal, target_len):
    if len(signal) <= target_len:
        return signal
    indices = np.linspace(0, len(signal) - 1, target_len, dtype=int)
    return [signal[i] for i in indices]

def pad_to_power_of_two(signal):
    n = len(signal)
    next_pow2 = 1 << (n - 1).bit_length()
    padded = signal + [0] * (next_pow2 - n)
    return padded, n

def generate_dataset():
    hours, demand_full = load_dataset()
    full_len = len(demand_full)
    demand_downsampled = downsample(demand_full, MAX_FFT_POINTS)
    # Mean-center so DC component does not dominate the frequency plots
    mean_val = sum(demand_downsampled) / len(demand_downsampled)
    demand_centered = [v - mean_val for v in demand_downsampled]
    signal_padded, original_len = pad_to_power_of_two(demand_centered)
    df = pd.DataFrame({'hour': list(hours[:full_len]), 'demand': demand_full})
    # Also return raw downsampled (for the signal plot to show actual MW values)
    return df, signal_padded, original_len, full_len, demand_downsampled

# ---------- Serial DFT ----------
def dft_serial(x):
    """Discrete Fourier Transform from scratch (serial)."""
    N = len(x)
    X = [0j] * N
    for k in range(N):
        sum_val = 0j
        for n in range(N):
            angle = -2j * math.pi * k * n / N
            sum_val += x[n] * cmath.exp(angle)
        X[k] = sum_val
    return X

# ---------- Parallel DFT (ThreadPoolExecutor — Celery-safe) ----------
def _dft_k(k, x, N):
    """Compute DFT for a single frequency index k."""
    sum_val = 0j
    for n in range(N):
        angle = -2j * math.pi * k * n / N
        sum_val += x[n] * cmath.exp(angle)
    return k, sum_val   # return index so we can reconstruct order

def dft_parallel(x, num_threads=NUM_THREADS):
    """
    Parallel DFT using ThreadPoolExecutor.
    Safe to call inside Celery daemon workers (unlike mp.Pool which requires
    spawning child processes — forbidden in daemon context).
    """
    N = len(x)
    results = [None] * N
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(_dft_k, k, x, N): k for k in range(N)}
        for future in futures:
            k, val = future.result()
            results[k] = val
    return results

# ---------- FFT (Cooley-Tukey, recursive) ----------
def fft(x):
    N = len(x)
    if N <= 1:
        return x
    if N % 2 != 0:
        raise ValueError("Length must be power of two")
    even = fft(x[0::2])
    odd  = fft(x[1::2])
    T = [cmath.exp(-2j * math.pi * k / N) * odd[k] for k in range(N // 2)]
    return [even[k] + T[k] for k in range(N // 2)] + \
           [even[k] - T[k] for k in range(N // 2)]

# ---------- Run Analysis + Plots ----------
def run_analysis(signal_padded, original_len, full_len, output_dir, demand_raw=None):
    """
    signal_padded: mean-centered, power-of-2 length list (for transforms)
    demand_raw:    original MW values for the signal plot (optional)
    """
    N = len(signal_padded)
    x = [complex(val, 0) for val in signal_padded]

    # Serial DFT
    start = time.perf_counter()
    X_dft_serial = dft_serial(x)
    time_dft_serial = time.perf_counter() - start

    # Parallel DFT (threads)
    start = time.perf_counter()
    X_dft_parallel = dft_parallel(x)
    time_dft_parallel = time.perf_counter() - start

    # FFT
    start = time.perf_counter()
    X_fft = fft(x)
    time_fft = time.perf_counter() - start

    # NumPy FFT
    start = time.perf_counter()
    X_np = np.fft.fft(signal_padded)
    time_np = time.perf_counter() - start

    # Magnitudes — skip index 0 (DC component) so the actual frequency
    # content is visible. The DC term is just sum(signal) which is massive
    # for energy demand data (MW scale) and dwarfs everything else.
    mag_dft_serial   = [abs(v) for v in X_dft_serial]
    mag_dft_parallel = [abs(v) for v in X_dft_parallel]
    mag_fft          = [abs(v) for v in X_fft]
    mag_np           = np.abs(X_np)

    half = N // 2
    # Start from index 1 to skip DC; use indices 1..half
    freqs_ac = np.arange(1, half)

    # Plot 1: Original signal — use raw demand values if provided, else centered
    plot_signal = demand_raw[:original_len] if demand_raw else signal_padded[:original_len]
    plt.figure(figsize=(8, 4))
    plt.plot(range(original_len), plot_signal, linestyle='-', color='steelblue', linewidth=0.8)
    plt.title(f'Downsampled Energy Demand ({original_len} points from {full_len} total)')
    plt.xlabel('Sample Index')
    plt.ylabel('Demand (MW)')
    plt.grid(True, alpha=0.3)
    signal_path = os.path.join(output_dir, 'original_signal.png')
    plt.savefig(signal_path, dpi=100, bbox_inches='tight')
    plt.close()

    # Plot 2: Serial DFT magnitude (AC only)
    plt.figure(figsize=(8, 4))
    plt.plot(freqs_ac, mag_dft_serial[1:half], 'b-', linewidth=0.8)
    plt.title(f'Serial DFT Magnitude – AC spectrum (time: {time_dft_serial:.4f} s)')
    plt.xlabel('Frequency Index')
    plt.ylabel('Magnitude')
    plt.grid(True, alpha=0.3)
    dft_serial_path = os.path.join(output_dir, 'dft_serial_magnitude.png')
    plt.savefig(dft_serial_path, dpi=100, bbox_inches='tight')
    plt.close()

    # Plot 3: Parallel DFT magnitude (AC only)
    plt.figure(figsize=(8, 4))
    plt.plot(freqs_ac, mag_dft_parallel[1:half], 'm-', linewidth=0.8)
    plt.title(f'Parallel DFT Magnitude – {NUM_THREADS} threads (time: {time_dft_parallel:.4f} s)')
    plt.xlabel('Frequency Index')
    plt.ylabel('Magnitude')
    plt.grid(True, alpha=0.3)
    dft_parallel_path = os.path.join(output_dir, 'dft_parallel_magnitude.png')
    plt.savefig(dft_parallel_path, dpi=100, bbox_inches='tight')
    plt.close()

    # Plot 4: FFT magnitude (AC only)
    plt.figure(figsize=(8, 4))
    plt.plot(freqs_ac, mag_fft[1:half], 'g-', linewidth=0.8)
    plt.title(f'FFT Magnitude – AC spectrum (time: {time_fft:.4f} s)')
    plt.xlabel('Frequency Index')
    plt.ylabel('Magnitude')
    plt.grid(True, alpha=0.3)
    fft_mag_path = os.path.join(output_dir, 'fft_magnitude.png')
    plt.savefig(fft_mag_path, dpi=100, bbox_inches='tight')
    plt.close()

    # Plot 5: Comparison (AC only)
    plt.figure(figsize=(10, 5))
    plt.plot(freqs_ac, mag_dft_serial[1:half],   'b-',  linewidth=0.8, label=f'Serial DFT {time_dft_serial:.4f}s')
    plt.plot(freqs_ac, mag_dft_parallel[1:half], 'm--', linewidth=0.8, label=f'Parallel DFT {time_dft_parallel:.4f}s')
    plt.plot(freqs_ac, mag_fft[1:half],          'g-',  linewidth=0.8, label=f'FFT {time_fft:.4f}s')
    plt.plot(freqs_ac, mag_np[1:half],           'r:',  linewidth=1.2, label=f'NumPy FFT {time_np:.6f}s')
    plt.title('Magnitude Spectrum Comparison (DC removed)')
    plt.xlabel('Frequency Index')
    plt.ylabel('Magnitude')
    plt.legend()
    plt.grid(True, alpha=0.3)
    comp_path = os.path.join(output_dir, 'comparison.png')
    plt.savefig(comp_path, dpi=100, bbox_inches='tight')
    plt.close()

    # Timing summary
    with open(os.path.join(output_dir, 'timing.txt'), 'w') as f:
        f.write(f"Serial DFT time:          {time_dft_serial:.6f} s\n")
        f.write(f"Parallel DFT time ({NUM_THREADS} threads): {time_dft_parallel:.6f} s\n")
        f.write(f"FFT time:                 {time_fft:.6f} s\n")
        f.write(f"NumPy FFT time:           {time_np:.6f} s\n")
        f.write(f"Speedup (Serial/FFT):     {time_dft_serial / time_fft:.2f}x\n")
        f.write(f"Speedup (Parallel/Serial):{time_dft_serial / time_dft_parallel:.2f}x\n")

    return {
        'signal':           signal_path,
        'dft_serial_mag':   dft_serial_path,
        'dft_parallel_mag': dft_parallel_path,
        'fft_mag':          fft_mag_path,
        'comparison':       comp_path,
    }

# ---------- Flowcharts ----------
def create_flowchart_dft():
    dot = graphviz.Digraph('flowchart_dft', format='png')
    dot.attr(rankdir='TB', size='8,5')
    dot.node('A', 'Start', shape='ellipse')
    dot.node('B', 'Input signal x[n] of length N', shape='parallelogram')
    dot.node('C', 'Initialize array X of size N', shape='rectangle')
    dot.node('D', 'For k = 0 to N-1\n(parallelized via threads)', shape='diamond')
    dot.node('E', 'Set sum = 0', shape='rectangle')
    dot.node('F', 'For n = 0 to N-1', shape='diamond')
    dot.node('G', 'Compute angle = -2π k n / N', shape='rectangle')
    dot.node('H', 'Add x[n] * exp(j*angle) to sum', shape='rectangle')
    dot.node('I', 'Store sum in X[k]', shape='rectangle')
    dot.node('J', 'Output X', shape='parallelogram')
    dot.node('K', 'End', shape='ellipse')
    dot.edges(['AB', 'BC', 'CD', 'DE', 'EF', 'FG', 'GH', 'HI', 'IF', 'HD', 'DJ', 'JK'])
    return dot.pipe(format='png')

def create_flowchart_fft():
    dot = graphviz.Digraph('flowchart_fft', format='png')
    dot.attr(rankdir='TB', size='8,5')
    dot.node('A', 'Start', shape='ellipse')
    dot.node('B', 'Input signal x[n] of length N (power of 2)', shape='parallelogram')
    dot.node('C', 'If N <= 1, return x', shape='diamond')
    dot.node('D', 'Split into even and odd indices', shape='rectangle')
    dot.node('E', 'Compute FFT of even half (recursive)', shape='rectangle')
    dot.node('F', 'Compute FFT of odd half (recursive)', shape='rectangle')
    dot.node('G', 'For k = 0 to N/2-1', shape='diamond')
    dot.node('H', 'Compute twiddle factor T = exp(-2πjk/N) * odd[k]', shape='rectangle')
    dot.node('I', 'X[k] = even[k] + T', shape='rectangle')
    dot.node('J', 'X[k+N/2] = even[k] - T', shape='rectangle')
    dot.node('K', 'Output X', shape='parallelogram')
    dot.node('L', 'End', shape='ellipse')
    dot.edges(['AB', 'BC', 'CD', 'DE', 'DF', 'EG', 'FG', 'GH', 'HI', 'HJ', 'GK', 'KL'])
    return dot.pipe(format='png')

# ---------- Implementation Code ----------
def get_implementation_code():
    return textwrap.dedent(f'''\
    import math
    import cmath
    import time
    from concurrent.futures import ThreadPoolExecutor
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd

    NUM_THREADS = {NUM_THREADS}

    # ---------- Serial DFT ----------
    def dft_serial(x):
        N = len(x)
        X = [0j] * N
        for k in range(N):
            sum_val = 0j
            for n in range(N):
                angle = -2j * math.pi * k * n / N
                sum_val += x[n] * cmath.exp(angle)
            X[k] = sum_val
        return X

    # ---------- Parallel DFT (ThreadPoolExecutor) ----------
    def _dft_k(k, x, N):
        sum_val = 0j
        for n in range(N):
            angle = -2j * math.pi * k * n / N
            sum_val += x[n] * cmath.exp(angle)
        return k, sum_val

    def dft_parallel(x, num_threads=NUM_THREADS):
        N = len(x)
        results = [None] * N
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = {{executor.submit(_dft_k, k, x, N): k for k in range(N)}}
            for future in futures:
                k, val = future.result()
                results[k] = val
        return results

    # ---------- FFT from scratch ----------
    def fft(x):
        N = len(x)
        if N <= 1:
            return x
        if N % 2 != 0:
            raise ValueError("Length must be power of two")
        even = fft(x[0::2])
        odd  = fft(x[1::2])
        T = [cmath.exp(-2j * math.pi * k / N) * odd[k] for k in range(N // 2)]
        return [even[k] + T[k] for k in range(N // 2)] + \\
               [even[k] - T[k] for k in range(N // 2)]

    # ---------- Load and prepare dataset ----------
    df_full = pd.read_csv('energy_demand.csv')
    signal_full = df_full['demand'].values.tolist()
    full_len = len(signal_full)

    # Downsample to {MAX_FFT_POINTS} evenly spaced points
    import numpy as np
    indices = np.linspace(0, full_len - 1, {MAX_FFT_POINTS}, dtype=int)
    signal_downsampled = [signal_full[i] for i in indices]

    # Pad to next power of two (already {MAX_FFT_POINTS} which is a power of two)
    N = len(signal_downsampled)
    next_pow2 = 1 << (N - 1).bit_length()
    signal = signal_downsampled + [0] * (next_pow2 - N)
    x = [complex(val, 0) for val in signal]
    N_padded = len(x)

    # ---------- Run transforms ----------
    start = time.perf_counter()
    X_dft_serial = dft_serial(x)
    time_dft_serial = time.perf_counter() - start

    start = time.perf_counter()
    X_dft_parallel = dft_parallel(x)
    time_dft_parallel = time.perf_counter() - start

    start = time.perf_counter()
    X_fft = fft(x)
    time_fft = time.perf_counter() - start

    start = time.perf_counter()
    X_np = np.fft.fft(signal)
    time_np = time.perf_counter() - start

    mag_dft_serial   = [abs(v) for v in X_dft_serial]
    mag_dft_parallel = [abs(v) for v in X_dft_parallel]
    mag_fft          = [abs(v) for v in X_fft]
    mag_np           = np.abs(X_np)
    freqs = range(N_padded)

    # ---------- Plots ----------
    plt.figure(figsize=(10, 5))
    plt.plot(freqs[:N_padded//2], mag_dft_serial[:N_padded//2],   'b-',  label=f'Serial DFT {{time_dft_serial:.4f}}s')
    plt.plot(freqs[:N_padded//2], mag_dft_parallel[:N_padded//2], 'm--', label=f'Parallel DFT {{time_dft_parallel:.4f}}s')
    plt.plot(freqs[:N_padded//2], mag_fft[:N_padded//2],          'g-',  label=f'FFT {{time_fft:.4f}}s')
    plt.plot(freqs[:N_padded//2], mag_np[:N_padded//2],           'r:',  label=f'NumPy FFT {{time_np:.6f}}s')
    plt.legend()
    plt.title('Magnitude Spectrum Comparison')
    plt.xlabel('Frequency Index')
    plt.ylabel('Magnitude')
    plt.savefig('comparison.png')
    plt.close()

    print(f"Serial DFT:   {{time_dft_serial:.4f}} s")
    print(f"Parallel DFT: {{time_dft_parallel:.4f}} s")
    print(f"FFT:          {{time_fft:.4f}} s")
    print(f"NumPy FFT:    {{time_np:.6f}} s")
    print(f"Speedup (Parallel vs Serial): {{time_dft_serial/time_dft_parallel:.2f}}x")
    print(f"Speedup (FFT vs Serial DFT):  {{time_dft_serial/time_fft:.2f}}x")
    ''')

# ---------- Jupyter Notebook ----------
def create_notebook(impl_code, save_path):
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python', 'version': '3.12'}
    }
    nb['cells'] = [
        nbf.v4.new_markdown_cell("# COS205 Assignment: Fourier Analysis of Energy Demand"),
        nbf.v4.new_code_cell(impl_code),
    ]
    with open(save_path, 'w') as f:
        nbf.write(nb, f)

# ---------- PDF Generation ----------
def generate_pdf(student_name, matric_number, analysis,
                 flowchart_dft_path, flowchart_fft_path,
                 result_paths, algo_dft, algo_fft, impl_code, save_path):

    width, height = A4
    left_margin   = 50
    right_margin  = width - 50
    content_width = right_margin - left_margin

    styles = {
        'normal': ParagraphStyle('Normal', fontName='Helvetica', fontSize=10, leading=14, spaceAfter=8),
        'code':   ParagraphStyle('Code',   fontName='Courier',   fontSize=8,  leading=10, leftIndent=10),
    }

    c = canvas.Canvas(save_path, pagesize=A4)

    def draw_paragraph(text, style, x, y, max_width):
        p = Paragraph(text, style)
        p.wrapOn(c, max_width, height)
        p.drawOn(c, x, y - p.height)
        return p.height

    def section_heading(label, y):
        if y < 100:
            c.showPage()
            y = height - 50
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, y, label)
        return y - 18

    def add_image(path, y, img_h=200, img_w=400):
        if not os.path.exists(path):
            return y
        if y < img_h + 20:
            c.showPage()
            y = height - 50
        img   = ImageReader(path)
        img_x = left_margin + (content_width - img_w) // 2
        c.drawImage(img, img_x, y - img_h, width=img_w, height=img_h, preserveAspectRatio=True)
        return y - (img_h + 20)

    y = height - 50

    # Title block
    c.setFont("Helvetica-Bold", 16)
    c.drawString(left_margin, y, "COS205 ASSIGNMENT")
    y -= 25
    c.setFont("Helvetica", 12)
    c.drawString(left_margin, y, f"Student: {student_name}")
    c.drawString(left_margin + 300, y, f"Matric: {matric_number}")
    y -= 40

    # Problem Statement
    y = section_heading("Problem Statement", y)
    prob = ("For this assignment, you are to write code that visualizes energy demand against the hour. "
            "Write a DFT function (without using libraries) to handle the Fourier Transform and visualize "
            "the outcome. Note your observation on the time it takes and at what hour you notice a spike. "
            "Then write an FFT function for the dataset, execute and visualize it. Compare the time taken. "
            "Which one is faster and by what amount? Use libraries to find DFT and FFT and compare the "
            "output with your own.")
    y -= draw_paragraph(prob, styles['normal'], left_margin, y, content_width) + 15

    # Analysis
    y = section_heading("Analysis", y)
    for para in analysis.split('. '):
        if not para.strip():
            continue
        if not para.endswith('.'):
            para += '.'
        if y - 20 < 50:
            c.showPage()
            y = height - 50
        y -= draw_paragraph(para, styles['normal'], left_margin, y, content_width) + 5
    y -= 10

    # DFT Design
    y = section_heading("Design - DFT", y)
    y -= draw_paragraph("Flowchart and Algorithm for DFT provided below.", styles['normal'], left_margin, y, content_width) + 15
    y = add_image(flowchart_dft_path, y)

    y = section_heading("DFT Algorithm", y)
    c.setFont("Courier", 8)
    for line in algo_dft.split('\n'):
        if line.strip():
            if y < 50:
                c.showPage(); y = height - 50; c.setFont("Courier", 8)
            c.drawString(left_margin + 10, y, line)
            y -= 10
    y -= 5

    # FFT Design
    y = section_heading("Design - FFT", y)
    y -= draw_paragraph("Flowchart and Algorithm for FFT provided below.", styles['normal'], left_margin, y, content_width) + 15
    y = add_image(flowchart_fft_path, y)

    y = section_heading("FFT Algorithm", y)
    c.setFont("Courier", 8)
    for line in algo_fft.split('\n'):
        if line.strip():
            if y < 50:
                c.showPage(); y = height - 50; c.setFont("Courier", 8)
            c.drawString(left_margin + 10, y, line)
            y -= 10
    y -= 5

    # Implementation
    y = section_heading("Implementation", y)
    c.setFont("Courier", 6)
    for line in impl_code.split('\n'):
        if y < 50:
            c.showPage(); y = height - 50; c.setFont("Courier", 6)
        c.drawString(left_margin + 10, y, line[:80] + ("..." if len(line) > 80 else ""))
        y -= 8
    y -= 10

    # Results
    y = section_heading("Results", y)
    for key in ['signal', 'dft_serial_mag', 'dft_parallel_mag', 'fft_mag', 'comparison']:
        path = result_paths.get(key, '')
        y = add_image(path, y, img_h=200 if key != 'comparison' else 225,
                      img_w=400 if key != 'comparison' else 450)

    c.save()

# ---------- Algorithm Texts ----------
ALGORITHM_DFT = """Step 1: Start
Step 2: Input signal x of length N
Step 3: Initialize output array X of size N
Step 4: For each frequency index k from 0 to N-1 (parallelized via ThreadPoolExecutor):
Step 5:    Set sum = 0
Step 6:    For each time sample n from 0 to N-1:
Step 7:        Compute angle = -2pi * k * n / N
Step 8:        Add x[n] * exp(j*angle) to sum
Step 9:    Store sum in X[k]
Step 10: Output X
Step 11: End"""

ALGORITHM_FFT = """Step 1: Start
Step 2: Input signal x of length N (power of two)
Step 3: If N <= 1, return x
Step 4: Split x into even and odd indexed halves
Step 5: Compute FFT of even half recursively -> E
Step 6: Compute FFT of odd half recursively -> O
Step 7: For k = 0 to N/2-1:
Step 8:    Compute twiddle factor T = exp(-2pijk/N) * O[k]
Step 9:    X[k] = E[k] + T
Step 10:   X[k+N/2] = E[k] - T
Step 11: Return X
Step 12: End"""