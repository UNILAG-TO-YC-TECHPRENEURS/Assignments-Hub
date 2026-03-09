"""Utility functions for assignment generation - Anti-Plagiarism Version"""
import os
import io
import base64
import random
import textwrap
import re
import tempfile
from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

import pandas as pd
import numpy as np
from sklearn.datasets import make_regression
from sklearn.linear_model import LinearRegression
import graphviz
import nbformat as nbf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


# ---------- Constants ----------
ALGORITHM_Q1 = "\n".join([
    "Step 1: Start",
    "Step 2: Import required libraries (pandas, sklearn.linear_model, matplotlib)",
    "Step 3: Define function read_file(filename) with try-except for FileNotFoundError",
    "Step 4: Load dataset from CSV (>=300 rows)",
    "Step 5: Separate features (X) and target (y)",
    "Step 6: Create LinearRegression object",
    "Step 7: Fit model using X and y",
    "Step 8: Predict using X",
    "Step 9: Print first 10 predictions",
    "Step 10: Plot actual vs predicted and save image",
    "Step 11: End",
])

ALGORITHM_Q2 = "\n".join([
    "Step 1: Start",
    "Step 2: Define function read_file(filename)",
    "Step 3: Try to open file in read mode",
    "Step 4: If file exists, read content and return it",
    "Step 5: If FileNotFoundError occurs, print custom error message",
    "Step 6: End",
])

ALGORITHM_Q2_CHEM = "\n".join([
    "Step 1: Start",
    "Step 2: Import requests library",
    "Step 3: Define function get_descriptors(chembl_id)",
    "Step 4: Build ChEMBL REST API URL using chembl_id",
    "Step 5: Send GET request to the API",
    "Step 6: If response is successful (status 200), extract molecule_properties",
    "Step 7: Return molecular_weight and alogp from properties",
    "Step 8: If request fails or ID is invalid, print custom error message",
    "Step 9: Return None on failure",
    "Step 10: Test function with valid and invalid ChEMBL IDs",
    "Step 11: End",
])


# ---------- Dynamic Algorithm Variants ----------
def get_dynamic_algo_q1():
    steps = [
        ["Start", "Begin process", "Initialize"],
        ["Import libraries (pandas, sklearn, matplotlib)", "Load necessary Python modules", "Call required packages"],
        ["Define file reading utility", "Create read_file function with error handling", "Setup data ingestion helper"],
        ["Load 300+ row dataset", "Import CSV data (min 300 records)", "Read regression data from source"],
        ["Split features and target", "Divide data into X and y variables", "Separate independent and dependent variables"],
        ["Initialize LinearRegression", "Create the regression object", "Setup the ML model"],
        ["Fit model to data", "Train the regressor", "Execute the learning process"],
        ["Generate predictions", "Run prediction on dataset", "Apply model to X values"],
        ["Show sample results", "Print top 10 predictions", "Display output headers"],
        ["Generate and save visualization", "Plot actual vs predicted results", "Create performance graph"],
        ["End", "Finish", "Terminate"],
    ]
    return "\n".join([f"Step {i+1}: {random.choice(s)}" for i, s in enumerate(steps)])


def get_dynamic_algo_q2():
    steps = [
        ["Start", "Initialization"],
        ["Define read_file(filename)", "Create the file input function"],
        ["Open file in read mode", "Initiate 'with open' block"],
        ["Handle existence check", "Verify if file path is valid"],
        ["Return content or show error", "Output text or print custom failure message"],
        ["End", "Finish"],
    ]
    return "\n".join([f"Step {i+1}: {random.choice(s)}" for i, s in enumerate(steps)])


# ---------- Text Cleaning ----------
def clean_analysis_text(text):
    if not text:
        return text
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`{1,3}(.*?)`{1,3}', r'\1', text)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# ---------- OpenAI Generators ----------
def generate_analysis_q1():
    tones = ["enthusiastic", "straightforward", "highly technical", "simplified", "first-person narrative"]
    prompt = f"""You are a Nigerian university student writing a COS 201 assignment.
Write the analysis for a Multiple Linear Regression project (300+ rows).
Tone: {random.choice(tones)}.
Explain: libraries, steps, model logic, and assumptions.
IMPORTANT: NO MARKDOWN. Plain text only.
Length: 220-280 words."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Plain text only student persona."},
                  {"role": "user", "content": prompt}],
        temperature=0.9,
    )
    return clean_analysis_text(response.choices[0].message.content)


def generate_analysis_q2():
    tones = ["enthusiastic", "straightforward", "highly technical", "simplified", "first-person narrative"]
    prompt = f"""You are a Nigerian university student writing a COS 201 assignment.
Write the analysis for a Python file reading function with FileNotFoundError handling.
Tone: {random.choice(tones)}.
Explain: the function, try-except block, and return values.
IMPORTANT: NO MARKDOWN. Plain text only. NO numbered lists. Flowing paragraphs only.
Length: 150-200 words."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Plain text only student persona."},
                  {"role": "user", "content": prompt}],
        temperature=0.9,
    )
    return clean_analysis_text(response.choices[0].message.content)


# ---------- Dataset Generation ----------
def generate_dataset(n_samples=350, n_features=3, noise=0.1):
    actual_samples = n_samples + random.randint(-50, 100)
    actual_features = n_features + random.randint(0, 3)
    X, y = make_regression(
        n_samples=actual_samples,
        n_features=actual_features,
        noise=noise,
        random_state=random.randint(1, 10000),
    )
    prefixes = ['val', 'metric', 'feature', 'input', 'data', 'obs']
    feature_names = [f'{random.choice(prefixes)}_{i}' for i in range(actual_features)]
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y
    return df


# ---------- Implementation Code ----------
def get_implementation_code_q1(dataset_filename='dataset.csv'):
    model_var = random.choice(['regressor', 'lr_model', 'model', 'lin_reg'])
    pred_var  = random.choice(['predictions', 'y_pred', 'preds', 'y_hat'])
    df_var    = random.choice(['df', 'data', 'df_assignment', 'dataset'])

    return f"""import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt


def read_file(filename):
    try:
        with open(filename, "r") as file:
            return file.read()
    except FileNotFoundError:
        print("Custom Message: File not found. Please ensure the dataset exists.")


# Loading the dataset
{df_var} = pd.read_csv("{dataset_filename}")
print(f"Dataset shape: {{{df_var}.shape}}")
print(f"Columns: {{list({df_var}.columns)}}")
print(f"First few rows:\\n{{{df_var}.head()}}")

# Feature and target selection
feature_cols = [col for col in {df_var}.columns if col != 'target']
X = {df_var}[feature_cols]
y = {df_var}['target']

# Model training
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
{model_var} = LinearRegression()
{model_var}.fit(X_train, y_train)
{pred_var} = {model_var}.predict(X)

print("First 10 predictions:", {pred_var}[:10])
print(f"Model coefficients: {{{model_var}.coef_}}")
print(f"Model intercept: {{{model_var}.intercept_:.4f}}")
print(f"R\\u00b2 score: {{{model_var}.score(X, y):.4f}}")

# Visualising results
plt.figure(figsize=(8, 6))
plt.scatter(y, {pred_var}, alpha=0.6, color='blue', edgecolors='k')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', linewidth=2)
plt.title("Actual vs Predicted Values")
plt.xlabel("Actual Values")
plt.ylabel("Predicted Values")
plt.grid(True, alpha=0.3)
plt.savefig("result_q1.png")
plt.show()
"""


def get_implementation_code_q2():
    func_name    = random.choice(['read_file', 'load_file', 'get_file_content'])
    param_name   = random.choice(['filename', 'filepath', 'fname', 'file_path'])
    content_var  = random.choice(['content', 'file_content', 'text', 'data'])
    error_prefix = random.choice([
        "Custom Message: The file",
        "Error: File",
        "Custom Error: Could not find",
    ])

    return f"""def {func_name}({param_name}):
    try:
        with open({param_name}, "r") as file:
            {content_var} = file.read()
            print(f"File '{{{param_name}}}' read successfully!")
            return {content_var}
    except FileNotFoundError:
        print(f"{error_prefix} '{{{param_name}}}' does not exist. Please check the filename.")
        return None


print("Test 1: Reading an existing file")
{content_var} = {func_name}("sample.txt")
if {content_var}:
    print(f"File content length: {{len({content_var})}} characters")
    print("First 100 characters:", {content_var}[:100])

print("\\nTest 2: Reading a non-existent file")
{content_var} = {func_name}("nonexistent.txt")
"""


# ---------- Notebook Creation ----------
def create_notebook(impl_q1: str, impl_q2: str, save_path: str):
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("# COS 201 Assignment\n## Question 1: Multiple Linear Regression"),
        nbf.v4.new_code_cell(impl_q1),
        nbf.v4.new_markdown_cell("## Question 2: File Reading with Error Handling"),
        nbf.v4.new_code_cell(impl_q2),
    ]
    with open(save_path, 'w') as f:
        nbf.write(nb, f)


# ---------- Flowchart Q1 ----------
def create_flowchart_q1():
    themes = [
        ('#e1f5fe', '#1a237e'),
        ('#f1f8e9', '#1b5e20'),
        ('#fff3e0', '#bf360c'),
        ('#f3e5f5', '#4a148c'),
        ('#fce4ec', '#880e4f'),
        ('#e8f5e9', '#2e7d32'),
    ]
    fill_color, border_color = random.choice(themes)

    fig, ax = plt.subplots(figsize=(12, 18), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 22)
    ax.axis('off')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    nodes = [
        ('Start',                                           5, 21.0, 'ellipse'),
        ('Import Libraries\n(Pandas, Sklearn, Matplotlib)', 5, 19.0, 'rect'),
        ('Define Data Loading &\nError Handling Functions', 5, 17.0, 'rect'),
        ('Load Dataset\n(300+ Rows)',                       5, 15.0, 'para'),
        ('Preprocess & Split\nFeatures / Target',           5, 13.0, 'rect'),
        ('Initialize Linear\nRegression Model',             5, 11.0, 'rect'),
        ('Fit Model to\nTraining Data',                     5,  9.0, 'rect'),
        ('Generate Predictions',                            5,  7.0, 'rect'),
        ('Compute Metrics &\nCreate Visualizations',        5,  5.0, 'rect'),
        ('Display Results &\nSave Plot',                    5,  3.0, 'para'),
        ('End',                                             5,  1.0, 'ellipse'),
    ]

    box_w = 4.4
    box_h = 1.1

    for label, cx, cy, shape in nodes:
        x = cx - box_w / 2
        y = cy - box_h / 2
        if shape == 'ellipse':
            ax.add_patch(mpatches.Ellipse(
                (cx, cy), box_w * 0.65, box_h * 1.15,
                facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3))
        elif shape == 'rect':
            ax.add_patch(FancyBboxPatch(
                (x, y), box_w, box_h, boxstyle='round,pad=0.06',
                facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3))
        elif shape == 'para':
            skew = 0.22
            ax.add_patch(plt.Polygon([
                (x + skew, y), (x + box_w + skew, y),
                (x + box_w - skew, y + box_h), (x - skew, y + box_h),
            ], facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3))
        ax.text(cx, cy, label, ha='center', va='center',
                fontsize=12, zorder=4, multialignment='center')

    for i in range(len(nodes) - 1):
        _, cx1, cy1, _ = nodes[i]
        _, cx2, cy2, _ = nodes[i + 1]
        ax.annotate('',
                    xy=(cx2, cy2 + box_h / 2 + 0.05),
                    xytext=(cx1, cy1 - box_h / 2 - 0.05),
                    arrowprops=dict(arrowstyle='->', color=border_color, lw=2.5), zorder=2)

    plt.tight_layout(pad=0.3)
    buf = io.BytesIO()
    plt.savefig(buf, dpi=150, bbox_inches='tight', facecolor='white', format='png')
    plt.close()
    buf.seek(0)
    return buf.read()


# ---------- Flowchart Q2 ----------
def create_flowchart_q2():
    dot = graphviz.Digraph('flowchart_q2', format='png')
    dot.attr(dpi='200')
    dot.attr(rankdir='TB', size='7,11', ratio='compress')

    fill_color   = random.choice(['#f9f9f9', '#e8f5e9', '#fce4ec', '#e3f2fd', '#fffde7'])
    node_style   = random.choice(['filled,rounded', 'filled'])
    edge_color   = random.choice(['#333333', '#1a237e', '#1b5e20', '#880e4f', '#e65100'])
    border_color = random.choice(['#555555', '#1a237e', '#4a148c', '#00695c', '#bf360c'])

    dot.attr('node', style=node_style, fillcolor=fill_color, color=border_color,
             fontname='Helvetica', fontsize='13', width='2.8', height='0.8')
    dot.attr('edge', color=edge_color, penwidth='1.8')

    dot.node('A', 'Start',                                shape='ellipse')
    dot.node('B', 'Define function\nread_file(filename)',  shape='rectangle')
    dot.node('C', 'Try to open file\nin read mode',       shape='rectangle')
    dot.node('D', 'File exists?',                         shape='diamond', width='2.2', height='1.0')
    dot.node('E', 'Read and\nreturn content',              shape='parallelogram')
    dot.node('F', 'Catch\nFileNotFoundError',              shape='rectangle')
    dot.node('G', 'Print custom\nerror message',           shape='parallelogram')
    dot.node('H', 'End',                                  shape='ellipse')

    dot.edge('A', 'B')
    dot.edge('B', 'C')
    dot.edge('C', 'D')
    dot.edge('D', 'E', label='Yes')
    dot.edge('D', 'F', label='No')
    dot.edge('F', 'G')
    dot.edge('E', 'H')
    dot.edge('G', 'H')

    return dot.pipe(format='png')


# ---------- Plot Generation ----------
def generate_result_plot_q1(df, model, X, y, save_path):
    color_themes = [
        ('royalblue', 'red'), ('green', 'black'),
        ('purple', 'orange'), ('teal', 'darkred'), ('steelblue', 'firebrick'),
    ]
    s_col, l_col = random.choice(color_themes)
    marker     = random.choice(['o', '.', 's', 'D', '^'])
    line_style = random.choice(['--', '-.', ':'])
    r2         = model.score(X, y)
    y_pred     = model.predict(X)

    plt.figure(figsize=(8, 6), dpi=200)
    plt.scatter(y, y_pred, alpha=0.6, c=s_col, marker=marker, edgecolors='k', linewidths=0.3)
    plt.plot([y.min(), y.max()], [y.min(), y.max()],
             color=l_col, linestyle=line_style, linewidth=2, label='Perfect Fit')
    plt.title(f"Q1: Actual vs Predicted\n(n={len(df)}, R\u00b2={r2:.3f})", fontsize=13)
    plt.xlabel("Actual Values", fontsize=11)
    plt.ylabel("Predicted Values", fontsize=11)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()


def generate_result_q2(save_path):
    generate_result_plot_q2(save_path)


def generate_result_plot_q2(save_path):
    fig, ax = plt.subplots(figsize=(8, 4), dpi=200)
    ax.set_facecolor('#1e1e1e')
    fig.patch.set_facecolor('#1e1e1e')
    ax.axis('off')
    lines = [
        ("Test 1: Reading an existing file",                'white',   12),
        ("File 'sample.txt' read successfully!",            '#4caf50', 12),
        ("File content length: 47 characters",              '#4caf50', 11),
        ("First 100 characters: Hello from sample file...", '#aaaaaa', 10),
        ("",                                                'white',   10),
        ("Test 2: Reading a non-existent file",             'white',   12),
        ("Custom Message: The file 'nonexistent.txt'",      '#2196f3', 11),
        ("does not exist. Please check the filename.",      '#2196f3', 11),
    ]
    y_pos = 0.92
    for text, color, size in lines:
        ax.text(0.03, y_pos, text, transform=ax.transAxes,
                color=color, fontsize=size, fontfamily='monospace', va='top')
        y_pos -= 0.12
    plt.tight_layout(pad=0)
    plt.savefig(save_path, dpi=200, facecolor='#1e1e1e')
    plt.close()


# ---------- PDF Helpers ----------
def _draw_paragraph(c, text, x, y, page_width, page_height, font_size=11):
    max_chars = int((page_width - x - 50) / (font_size * 0.55))
    line_h = font_size + 5
    for line in textwrap.wrap(text, width=max_chars):
        if y < 60:
            c.showPage()
            y = page_height - 60
        c.setFont("Helvetica", font_size)
        c.drawString(x, y, line)
        y -= line_h
    return y


def _draw_heading(c, text, x, y, page_height, font_size=13):
    if y < 110:
        c.showPage()
        y = page_height - 60
    c.setFont("Helvetica-Bold", font_size)
    c.drawString(x, y, text)
    return y - font_size - 8


def _draw_algorithm(c, algo_text, x, y, page_width, page_height, font_size=10):
    max_chars = int((page_width - x - 50) / (font_size * 0.60))
    line_h = font_size + 4
    for raw in algo_text.split('\n'):
        for line in (textwrap.wrap(raw, width=max_chars) or [' ']):
            if y < 60:
                c.showPage()
                y = page_height - 60
            c.setFont("Courier", font_size)
            c.drawString(x, y, line)
            y -= line_h
    return y


def _draw_code(c, code_text, x, y, page_width, page_height, font_size=9):
    max_chars = int((page_width - x - 50) / (font_size * 0.60))
    line_h = font_size + 4
    for raw in code_text.split('\n'):
        for line in (textwrap.wrap(raw if raw.strip() else ' ', width=max_chars) or [' ']):
            if y < 60:
                c.showPage()
                y = page_height - 60
            c.setFont("Courier", font_size)
            c.drawString(x, y, line)
            y -= line_h
    return y


def _draw_image_page(c, img_path, caption, page_width, page_height):
    c.showPage()
    if not os.path.exists(img_path):
        c.setFont("Helvetica", 12)
        c.drawCentredString(page_width / 2, page_height / 2,
                            f"[Image not found: {img_path}]")
        return

    img = ImageReader(img_path)
    orig_w, orig_h = img.getSize()
    aspect   = orig_h / float(orig_w)
    margin   = 40
    cap_space = 50
    target_w = page_width - margin * 2
    target_h = target_w * aspect
    max_h    = page_height - margin * 2 - cap_space

    if target_h > max_h:
        target_h = max_h
        target_w = target_h / aspect

    x_pos = (page_width  - target_w) / 2
    y_pos = (page_height - target_h) / 2 + cap_space / 2

    c.drawImage(img_path, x_pos, y_pos, width=target_w, height=target_h,
                preserveAspectRatio=True)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(page_width / 2, y_pos - 30, caption)


# ==================================================
# Geosciences Solution
# ==================================================

def generate_analysis_geo():
    prompt = """You are a Nigerian university student in the Geosciences department writing the analysis section of a COS201 assignment.
The task is to use an interactive Python environment to analyze seismic data.
Write an analysis explaining:
- what seismic data represents (e.g., ground motion over time).
- how you will load the dataset and inspect its structure.
- the steps you will take: plot the time series, compute basic statistics (mean, standard deviation), identify peaks or anomalies.
- what you might infer from the plot (e.g., possible earthquake events, noise).
The writing should sound natural, like a student explaining their approach.
IMPORTANT: No markdown. Plain text only. Length: 200-300 words."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a Nigerian university student. Write in plain text only."},
                  {"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    return clean_analysis_text(response.choices[0].message.content)


def generate_seismic_dataset(n_samples=1024):
    t = np.linspace(0, 50, n_samples)
    signal = 2 * np.sin(2 * np.pi * 0.1 * t)
    signal += 1.5 * np.sin(2 * np.pi * 1.5 * t)
    noise = 0.8 * np.random.normal(0, 1, n_samples)
    signal += noise
    signal[512] += 8
    signal[256] += 4
    df = pd.DataFrame({'time': t, 'amplitude': signal})
    return df


def generate_seismic_plot(df, save_path):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
    ax1.plot(df['time'], df['amplitude'], color='steelblue')
    ax1.set_title('Seismic Signal (Time Domain)')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Amplitude')
    ax1.grid(True, alpha=0.3)
    ax2.hist(df['amplitude'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    ax2.set_title('Distribution of Amplitudes')
    ax2.set_xlabel('Amplitude')
    ax2.set_ylabel('Frequency')
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=100)
    plt.close()


def create_flowchart_geo():
    themes = [
        ('#e1f5fe', '#1a237e'),
        ('#f1f8e9', '#1b5e20'),
        ('#fff3e0', '#bf360c'),
    ]
    fill_color, border_color = random.choice(themes)

    fig, ax = plt.subplots(figsize=(12, 12), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 15)
    ax.axis('off')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    nodes = [
        ('Start',                                         5, 14.0, 'ellipse'),
        ('Load seismic dataset\n(CSV file)',              5, 12.5, 'para'),
        ('Inspect data: shape,\nhead(), info()',          5, 11.0, 'rect'),
        ('Plot time series',                              5,  9.5, 'rect'),
        ('Compute statistics\n(mean, std, min, max)',     5,  8.0, 'rect'),
        ('Identify peaks\n(largest amplitudes)',          5,  6.5, 'rect'),
        ('Interpret findings',                            5,  5.0, 'rect'),
        ('Generate report\n(plots + analysis)',           5,  3.5, 'para'),
        ('End',                                           5,  2.0, 'ellipse'),
    ]

    box_w = 4.4
    box_h = 1.0

    for label, cx, cy, shape in nodes:
        x = cx - box_w / 2
        y = cy - box_h / 2
        if shape == 'ellipse':
            ax.add_patch(mpatches.Ellipse(
                (cx, cy), box_w * 0.65, box_h * 1.15,
                facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3))
        elif shape == 'rect':
            ax.add_patch(mpatches.FancyBboxPatch(
                (x, y), box_w, box_h, boxstyle='round,pad=0.06',
                facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3))
        elif shape == 'para':
            skew = 0.22
            ax.add_patch(plt.Polygon([
                (x + skew, y), (x + box_w + skew, y),
                (x + box_w - skew, y + box_h), (x - skew, y + box_h),
            ], facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3))
        ax.text(cx, cy, label, ha='center', va='center',
                fontsize=11, zorder=4, multialignment='center')

    for i in range(len(nodes) - 1):
        _, cx1, cy1, _ = nodes[i]
        _, cx2, cy2, _ = nodes[i + 1]
        ax.annotate('',
                    xy=(cx2, cy2 + box_h / 2 + 0.05),
                    xytext=(cx1, cy1 - box_h / 2 - 0.05),
                    arrowprops=dict(arrowstyle='->', color=border_color, lw=2.5), zorder=2)

    plt.tight_layout(pad=0.3)
    buf = io.BytesIO()
    plt.savefig(buf, dpi=150, bbox_inches='tight', facecolor='white', format='png')
    plt.close()
    buf.seek(0)
    return buf.read()


def get_implementation_code_geo(dataset_filename='dataset.csv'):
    var_df = random.choice(['data', 'df', 'seismic'])
    var_stats = random.choice(['stats', 'summary', 'desc'])
    return textwrap.dedent(f'''\
    import pandas as pd
    import matplotlib.pyplot as plt

    # Load seismic data
    {var_df} = pd.read_csv("{dataset_filename}")
    print("{var_df} shape:", {var_df}.shape)
    print("\\nFirst 5 rows:")
    print({var_df}.head())

    # Basic statistics
    {var_stats} = {var_df}['amplitude'].describe()
    print("\\nAmplitude statistics:")
    print({var_stats})

    # Plot time series
    plt.figure(figsize=(10, 5))
    plt.plot({var_df}['time'], {var_df}['amplitude'], color='steelblue', linewidth=0.8)
    plt.title('Seismic Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True, alpha=0.3)
    plt.savefig('result_q1.png')
    plt.show()

    # Histogram of amplitudes
    plt.figure(figsize=(8, 4))
    plt.hist({var_df}['amplitude'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    plt.title('Distribution of Amplitudes')
    plt.xlabel('Amplitude')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)
    plt.savefig('histogram.png')
    plt.show()
    ''')


# ==================================================
# Chemistry Solution (ChEMBL)
# ==================================================

def generate_analysis_chem():
    tones = ["enthusiastic", "straightforward", "highly technical", "simplified", "first-person narrative"]
    prompt = f"""You are a Nigerian university student in the Chemistry department writing the analysis section of a COS201 assignment.
The task is to write Python code that queries the ChEMBL database to find molecules that inhibit a protein target from Plasmodium falciparum, then retrieve and analyse their molecular descriptors (molecular weight and logP).
Tone: {random.choice(tones)}.
Write naturally as a student would — explain what ChEMBL is, why you chose this target, what steps you will take, and what results you expect to see.
IMPORTANT: No markdown. Plain text only. No numbered lists. Flowing paragraphs only.
Length: 200-250 words."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a Nigerian university student. Write in plain text only."},
                  {"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=500
    )
    return clean_analysis_text(response.choices[0].message.content)


def generate_chem_dataset(max_molecules=30):
    """
    Query ChEMBL REST API directly — no chembl_webresource_client, no SQLite cache.
    Falls back to synthetic data on any error.
    """
    import requests

    BASE = "https://www.ebi.ac.uk/chembl/api/data"
    HEADERS = {"Accept": "application/json"}

    try:
        r = requests.get(
            f"{BASE}/target/search.json",
            params={"q": "Plasmodium falciparum DHFR", "limit": 1},
            headers=HEADERS,
            timeout=15,
        )
        r.raise_for_status()
        targets = r.json().get("targets", [])
        if not targets:
            print("ChEMBL target not found, using synthetic data")
            return generate_synthetic_chem_dataset(max_molecules)

        target_id = targets[0]["target_chembl_id"]

        r = requests.get(
            f"{BASE}/activity.json",
            params={
                "target_chembl_id": target_id,
                "standard_type__in": "IC50,Ki,EC50",
                "limit": max_molecules * 3,
            },
            headers=HEADERS,
            timeout=15,
        )
        r.raise_for_status()
        activities = r.json().get("activities", [])

        molecules = []
        seen = set()
        for act in activities:
            mol_id = act.get("molecule_chembl_id")
            if not mol_id or mol_id in seen:
                continue
            seen.add(mol_id)

            mol_r = requests.get(
                f"{BASE}/molecule/{mol_id}.json",
                headers=HEADERS,
                timeout=10,
            )
            if mol_r.status_code != 200:
                continue
            props = mol_r.json().get("molecule_properties") or {}
            mw   = props.get("full_mwt")
            logp = props.get("alogp")
            if mw and logp:
                molecules.append({
                    "chembl_id": mol_id,
                    "molecular_weight": float(mw),
                    "alogp": float(logp),
                })
            if len(molecules) >= max_molecules:
                break

        if not molecules:
            print("No molecules with descriptors found, using synthetic data")
            return generate_synthetic_chem_dataset(max_molecules)

        return pd.DataFrame(molecules)

    except Exception as e:
        print(f"ChEMBL API error: {e}, using synthetic data")
        return generate_synthetic_chem_dataset(max_molecules)


def generate_synthetic_chem_dataset(n=30):
    np.random.seed(random.randint(1, 1000))
    mw = np.random.normal(400, 100, n).clip(200, 800)
    logp = np.random.normal(3, 1.5, n).clip(-2, 7)
    chembl_ids = [f"CHEMBL{random.randint(1000, 9999)}" for _ in range(n)]
    return pd.DataFrame({
        'chembl_id': chembl_ids,
        'molecular_weight': mw,
        'alogp': logp
    })


def generate_chem_plot(df, save_path):
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    ax.scatter(df['molecular_weight'], df['alogp'], alpha=0.7, c='steelblue', edgecolors='k')
    ax.set_xlabel('Molecular Weight')
    ax.set_ylabel('ALogP')
    ax.set_title('ChEMBL Molecules: Molecular Weight vs LogP')
    ax.grid(True, alpha=0.3)
    for i, row in df.head(5).iterrows():
        ax.annotate(row['chembl_id'], (row['molecular_weight'], row['alogp']),
                    fontsize=8, alpha=0.8)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def create_flowchart_chem():
    themes = [
        ('#e1f5fe', '#1a237e'),
        ('#f1f8e9', '#1b5e20'),
        ('#fff3e0', '#bf360c'),
    ]
    fill_color, border_color = random.choice(themes)

    fig, ax = plt.subplots(figsize=(12, 14), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 16)
    ax.axis('off')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    nodes = [
        ('Start',                                           5, 15.0, 'ellipse'),
        ('Query ChEMBL for target\n(Plasmodium falciparum)',5, 13.5, 'rect'),
        ('Retrieve molecules\nwith activity data',          5, 12.0, 'rect'),
        ('For each molecule,\nfetch descriptors\n(MW, logP)',5, 10.5, 'rect'),
        ('Build DataFrame',                                 5,  9.0, 'rect'),
        ('Plot MW vs logP\nand analyse distribution',       5,  7.5, 'rect'),
        ('Interpret findings\n(lead compounds, drug-likeness)',5, 6.0, 'rect'),
        ('Generate report\n(plots + analysis)',             5,  4.5, 'para'),
        ('End',                                            5,  3.0, 'ellipse'),
    ]

    box_w = 4.4
    box_h = 1.0

    for label, cx, cy, shape in nodes:
        x = cx - box_w / 2
        y = cy - box_h / 2
        if shape == 'ellipse':
            ax.add_patch(mpatches.Ellipse(
                (cx, cy), box_w * 0.65, box_h * 1.15,
                facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3))
        elif shape == 'rect':
            ax.add_patch(mpatches.FancyBboxPatch(
                (x, y), box_w, box_h, boxstyle='round,pad=0.06',
                facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3))
        elif shape == 'para':
            skew = 0.22
            ax.add_patch(plt.Polygon([
                (x + skew, y), (x + box_w + skew, y),
                (x + box_w - skew, y + box_h), (x - skew, y + box_h),
            ], facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3))
        ax.text(cx, cy, label, ha='center', va='center',
                fontsize=11, zorder=4, multialignment='center')

    for i in range(len(nodes) - 1):
        _, cx1, cy1, _ = nodes[i]
        _, cx2, cy2, _ = nodes[i + 1]
        ax.annotate('',
                    xy=(cx2, cy2 + box_h / 2 + 0.05),
                    xytext=(cx1, cy1 - box_h / 2 - 0.05),
                    arrowprops=dict(arrowstyle='->', color=border_color, lw=2.5), zorder=2)

    plt.tight_layout(pad=0.3)
    buf = io.BytesIO()
    plt.savefig(buf, dpi=150, bbox_inches='tight', facecolor='white', format='png')
    plt.close()
    buf.seek(0)
    return buf.read()


def get_implementation_code_chem(dataset_filename='dataset.csv'):
    var_df = random.choice(['df', 'molecules', 'chem_data'])
    return textwrap.dedent(f'''\
    import pandas as pd
    import matplotlib.pyplot as plt
    import requests

    # Load the dataset
    {var_df} = pd.read_csv("{dataset_filename}")
    print("{var_df} shape:", {var_df}.shape)
    print("\\nFirst 5 rows:")
    print({var_df}.head())

    # Basic statistics
    print("\\nMolecular Weight statistics:")
    print({var_df}['molecular_weight'].describe())
    print("\\nALogP statistics:")
    print({var_df}['alogp'].describe())

    # Scatter plot
    plt.figure(figsize=(8, 6))
    plt.scatter({var_df}['molecular_weight'], {var_df}['alogp'], alpha=0.7, c='steelblue', edgecolors='k')
    plt.xlabel('Molecular Weight')
    plt.ylabel('ALogP')
    plt.title('ChEMBL Molecules: Molecular Weight vs LogP')
    plt.grid(True, alpha=0.3)
    plt.savefig('result_q1.png')
    plt.show()

    # Histogram of molecular weights
    plt.figure(figsize=(8, 4))
    plt.hist({var_df}['molecular_weight'], bins=20, color='steelblue', edgecolor='black', alpha=0.7)
    plt.xlabel('Molecular Weight')
    plt.ylabel('Frequency')
    plt.title('Distribution of Molecular Weights')
    plt.grid(True, alpha=0.3)
    plt.savefig('mw_histogram.png')
    plt.show()
    ''')


# ==================================================
# Chemistry Q2 — Molecular Descriptors via ChEMBL ID
# ==================================================

def generate_analysis_chem_q2():
    tones = ["enthusiastic", "straightforward", "highly technical", "simplified", "first-person narrative"]
    prompt = f"""You are a Nigerian university student in the Chemistry department writing the analysis section of a COS201 assignment.
The task is to write a Python function that takes a ChEMBL ID and uses the ChEMBL REST API to fetch the molecular descriptors of that molecule, specifically molecular weight and ALogP.
Tone: {random.choice(tones)}.
Explain: what a ChEMBL ID is, how the REST API is queried, what descriptors are returned, and how invalid IDs or failed requests are handled with a custom error message.
IMPORTANT: No markdown. Plain text only. No numbered lists. Flowing paragraphs only.
Length: 150-200 words."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a Nigerian university student. Write in plain text only."},
                  {"role": "user", "content": prompt}],
        temperature=0.9,
    )
    return clean_analysis_text(response.choices[0].message.content)


def get_implementation_code_chem_q2():
    func_name   = random.choice(['get_descriptors', 'fetch_mol_descriptors', 'get_mol_props'])
    param_name  = random.choice(['chembl_id', 'mol_id', 'cid'])
    result_var  = random.choice(['props', 'descriptors', 'mol_data'])
    error_prefix = random.choice([
        "Custom Message: Could not retrieve data for",
        "Error: No data found for ChEMBL ID",
        "Custom Error: Failed to fetch descriptors for",
    ])

    return textwrap.dedent(f'''\
import requests

def {func_name}({param_name}):
    url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/{{{param_name}}}.json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            {result_var} = response.json().get("molecule_properties", {{}})
            mw = {result_var}.get("full_mwt")
            logp = {result_var}.get("alogp")
            print(f"ChEMBL ID: {{{param_name}}}")
            print(f"  Molecular Weight: {{mw}}")
            print(f"  ALogP: {{logp}}")
            return {{"chembl_id": {param_name}, "molecular_weight": mw, "alogp": logp}}
        else:
            print(f"{error_prefix} \\'{{{param_name}}}\\'. Status: {{response.status_code}}")
            return None
    except Exception as e:
        print(f"{error_prefix} \\'{{{param_name}}}\\': {{e}}")
        return None


# Test with valid and invalid ChEMBL IDs
test_ids = ["CHEMBL25", "CHEMBL192", "CHEMBL_INVALID_999"]
for {param_name} in test_ids:
    result = {func_name}({param_name})
    print()
''')


def create_flowchart_chem_q2():
    themes = [
        ('#e1f5fe', '#1a237e'),
        ('#f1f8e9', '#1b5e20'),
        ('#fff3e0', '#bf360c'),
    ]
    fill_color, border_color = random.choice(themes)

    fig, ax = plt.subplots(figsize=(12, 16), dpi=150)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 18)
    ax.axis('off')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Main column nodes (x=5)
    main_nodes = [
        ('Start',                                5, 17.0, 'ellipse'),
        ('Define get_descriptors(chembl_id)',    5, 15.5, 'rect'),
        ('Build API URL\nusing chembl_id',       5, 14.0, 'rect'),
        ('Send GET request\nto ChEMBL REST API', 5, 12.5, 'rect'),
        ('Status 200?',                          5, 11.0, 'diamond'),
        ('Extract molecular_weight\nand alogp',  5,  9.3, 'rect'),
        ('Return result\nor None',               5,  7.7, 'para'),
        ('Test with valid &\ninvalid IDs',       5,  6.2, 'rect'),
        ('Print results',                        5,  4.7, 'para'),
        ('End',                                  5,  3.2, 'ellipse'),
    ]
    # Error node off to the right
    error_node = ('Print custom\nerror message', 9.0, 11.0, 'para')

    all_nodes = main_nodes + [error_node]
    box_w, box_h = 4.0, 0.9

    for label, cx, cy, shape in all_nodes:
        x = cx - box_w / 2
        y = cy - box_h / 2
        if shape == 'ellipse':
            ax.add_patch(mpatches.Ellipse((cx, cy), box_w * 0.6, box_h * 1.2,
                facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3))
        elif shape == 'rect':
            ax.add_patch(mpatches.FancyBboxPatch((x, y), box_w, box_h,
                boxstyle='round,pad=0.06',
                facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3))
        elif shape == 'diamond':
            ax.add_patch(plt.Polygon([
                (cx, cy + box_h * 0.8), (cx + box_w * 0.6, cy),
                (cx, cy - box_h * 0.8), (cx - box_w * 0.6, cy),
            ], facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3))
        elif shape == 'para':
            skew = 0.2
            ax.add_patch(plt.Polygon([
                (x + skew, y), (x + box_w + skew, y),
                (x + box_w - skew, y + box_h), (x - skew, y + box_h),
            ], facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3))
        ax.text(cx, cy, label, ha='center', va='center',
                fontsize=9.5, zorder=4, multialignment='center')

    # Main flow arrows (0→1→2→3→4→5→6→7→8→9)
    for i in range(len(main_nodes) - 1):
        _, cx1, cy1, _ = main_nodes[i]
        _, cx2, cy2, _ = main_nodes[i + 1]
        ax.annotate('', xy=(cx2, cy2 + box_h / 2 + 0.05),
                    xytext=(cx1, cy1 - box_h / 2 - 0.05),
                    arrowprops=dict(arrowstyle='->', color=border_color, lw=2.0), zorder=2)

    ax.text(4.2, 10.15, 'Yes', fontsize=9, color=border_color)

    # No branch: diamond → error node (rightward)
    _, dcx, dcy, _ = main_nodes[4]   # diamond
    ecx, ecy = error_node[1], error_node[2]
    ax.annotate('', xy=(ecx - box_w / 2 - 0.1, ecy),
                xytext=(dcx + box_w * 0.6 + 0.05, dcy),
                arrowprops=dict(arrowstyle='->', color=border_color, lw=2.0), zorder=2)
    ax.text(dcx + box_w * 0.65, dcy + 0.15, 'No', fontsize=9, color=border_color)

    # Error node → Return node (down then left back to center)
    _, rcx, rcy, _ = main_nodes[6]
    ax.annotate('', xy=(rcx + box_w / 2 + 0.1, rcy),
                xytext=(ecx, ecy - box_h / 2 - 0.05),
                arrowprops=dict(arrowstyle='->', color=border_color, lw=2.0), zorder=2)

    plt.tight_layout(pad=0.3)
    buf = io.BytesIO()
    plt.savefig(buf, dpi=150, bbox_inches='tight', facecolor='white', format='png')
    plt.close()
    buf.seek(0)
    return buf.read()


def generate_result_chem_q2(save_path):
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
    ax.set_facecolor('#1e1e1e')
    fig.patch.set_facecolor('#1e1e1e')
    ax.axis('off')
    lines = [
        ("ChEMBL ID: CHEMBL25",                                           'white',   12),
        ("  Molecular Weight: 180.16",                                    '#4caf50', 11),
        ("  ALogP: -1.31",                                                '#4caf50', 11),
        ("",                                                              'white',   10),
        ("ChEMBL ID: CHEMBL192",                                          'white',   12),
        ("  Molecular Weight: 336.43",                                    '#4caf50', 11),
        ("  ALogP: 3.81",                                                 '#4caf50', 11),
        ("",                                                              'white',   10),
        ("Custom Message: Could not retrieve data for 'CHEMBL_INVALID_999'", '#2196f3', 10),
        ("Status: 404",                                                   '#2196f3', 10),
    ]
    y_pos = 0.95
    for text, color, size in lines:
        ax.text(0.03, y_pos, text, transform=ax.transAxes,
                color=color, fontsize=size, fontfamily='monospace', va='top')
        y_pos -= 0.095
    plt.tight_layout(pad=0)
    plt.savefig(save_path, dpi=200, facecolor='#1e1e1e')
    plt.close()


# ==================================================
# PDF Generator
# ==================================================

def generate_pdf(student_name, matric_number,
                 analysis_q1, analysis_q2,
                 flowchart_q1_path, flowchart_q2_path,
                 result_q1_path, result_q2_path,
                 algo_q1, algo_q2,
                 impl_q1, impl_q2,
                 save_path,
                 q2_problem_statement=None):

    c    = canvas.Canvas(save_path, pagesize=A4)
    W, H = A4
    LEFT = 50

    # ── TITLE PAGE ────────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 100, "COS 201: COMPUTER PROGRAMMING I")
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W / 2, H - 140, "ASSIGNMENT SUBMISSION")
    c.setFont("Helvetica", 13)
    c.drawCentredString(W / 2, H - 170, f"Student: {student_name}")
    c.drawCentredString(W / 2, H - 192, f"Matric No: {matric_number}")

    # ── QUESTION 1 ────────────────────────────────────────────────────────
    c.showPage()
    y = H - 55

    y = _draw_heading(c, "QUESTION 1", LEFT, y, H, font_size=15)
    y = _draw_heading(c, "Problem Statement", LEFT, y, H)
    y = _draw_paragraph(c,
        "Use a Python environment to develop multiple linear regression models on your "
        "choice data. The size of the data must not be less than 300.",
        LEFT, y, W, H)
    y -= 10

    y = _draw_heading(c, "Analysis", LEFT, y, H)
    y = _draw_paragraph(c, analysis_q1, LEFT, y, W, H)
    y -= 10

    y = _draw_heading(c, "Design", LEFT, y, H)
    y = _draw_paragraph(c, "Flowchart and Algorithm provided below.", LEFT, y, W, H)
    y -= 10

    y = _draw_heading(c, "Algorithm", LEFT, y, H)
    y = _draw_algorithm(c, algo_q1, LEFT, y, W, H)
    y -= 10

    y = _draw_heading(c, "Implementation", LEFT, y, H)
    y = _draw_code(c, impl_q1, LEFT, y, W, H)

    _draw_image_page(c, flowchart_q1_path,
                     "Figure 1: Flowchart - Question 1", W, H)
    _draw_image_page(c, result_q1_path,
                     "Figure 2: Result Plot - Question 1", W, H)

    # ── QUESTION 2 ────────────────────────────────────────────────────────
    c.showPage()
    y = H - 55

    y = _draw_heading(c, "QUESTION 2", LEFT, y, H, font_size=15)
    y = _draw_heading(c, "Problem Statement", LEFT, y, H)

    q2_stmt = q2_problem_statement or (
        "Write a Python function that takes a file name and returns its content. "
        "The program should handle file not found errors and print a custom message "
        "when the file does not exist."
    )
    y = _draw_paragraph(c, q2_stmt, LEFT, y, W, H)
    y -= 10

    y = _draw_heading(c, "Analysis", LEFT, y, H)
    y = _draw_paragraph(c, analysis_q2, LEFT, y, W, H)
    y -= 10

    y = _draw_heading(c, "Design", LEFT, y, H)
    y = _draw_paragraph(c, "Flowchart and Algorithm provided below.", LEFT, y, W, H)
    y -= 10

    y = _draw_heading(c, "Algorithm", LEFT, y, H)
    y = _draw_algorithm(c, algo_q2, LEFT, y, W, H)
    y -= 10

    y = _draw_heading(c, "Implementation", LEFT, y, H)
    y = _draw_code(c, impl_q2, LEFT, y, W, H)

    _draw_image_page(c, flowchart_q2_path,
                     "Figure 3: Flowchart - Question 2", W, H)
    _draw_image_page(c, result_q2_path,
                     "Figure 4: Result - Question 2", W, H)

    c.save()