"""Utility functions for assignment generation - Anti-Plagiarism Version"""
import os
import io
import base64
import random
import textwrap
import re
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


# ---------- Constants (used by tasks.py as utils.ALGORITHM_Q1 / Q2) ----------
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


# ---------- Dynamic Algorithm Variants (randomised per student) ----------
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
    """Returns randomised but correct Q1 implementation code as a string."""
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
    """Returns randomised but correct Q2 implementation code as a string."""
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
    """Creates a Jupyter notebook with Q1 and Q2 implementation cells."""
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("# COS 201 Assignment\n## Question 1: Multiple Linear Regression"),
        nbf.v4.new_code_cell(impl_q1),
        nbf.v4.new_markdown_cell("## Question 2: File Reading with Error Handling"),
        nbf.v4.new_code_cell(impl_q2),
    ]
    with open(save_path, 'w') as f:
        nbf.write(nb, f)


# ---------- Flowchart Q1 — Matplotlib (BIG, full page) ----------
def create_flowchart_q1():
    """
    Returns raw PNG bytes of the Q1 flowchart.
    Uses matplotlib for full size control — fills ~85% of A4 page, never squashed.
    Visual variety from randomised colour themes per student.
    """
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
                facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3,
            ))
        elif shape == 'rect':
            ax.add_patch(FancyBboxPatch(
                (x, y), box_w, box_h,
                boxstyle='round,pad=0.06',
                facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3,
            ))
        elif shape == 'para':
            skew = 0.22
            ax.add_patch(plt.Polygon([
                (x + skew,         y),
                (x + box_w + skew, y),
                (x + box_w - skew, y + box_h),
                (x - skew,         y + box_h),
            ], facecolor=fill_color, edgecolor=border_color, linewidth=2.5, zorder=3))

        ax.text(cx, cy, label, ha='center', va='center',
                fontsize=12, zorder=4, multialignment='center')

    for i in range(len(nodes) - 1):
        _, cx1, cy1, _ = nodes[i]
        _, cx2, cy2, _ = nodes[i + 1]
        ax.annotate('',
                    xy=(cx2, cy2 + box_h / 2 + 0.05),
                    xytext=(cx1, cy1 - box_h / 2 - 0.05),
                    arrowprops=dict(arrowstyle='->', color=border_color, lw=2.5),
                    zorder=2)

    plt.tight_layout(pad=0.3)
    buf = io.BytesIO()
    plt.savefig(buf, dpi=150, bbox_inches='tight', facecolor='white', format='png')
    plt.close()
    buf.seek(0)
    return buf.read()


# ---------- Flowchart Q2 — graphviz ----------
def create_flowchart_q2():
    """Returns raw PNG bytes for Q2 flowchart."""
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

    dot.node('A', 'Start',                               shape='ellipse')
    dot.node('B', 'Define function\nread_file(filename)', shape='rectangle')
    dot.node('C', 'Try to open file\nin read mode',      shape='rectangle')
    dot.node('D', 'File exists?',                        shape='diamond', width='2.2', height='1.0')
    dot.node('E', 'Read and\nreturn content',             shape='parallelogram')
    dot.node('F', 'Catch\nFileNotFoundError',             shape='rectangle')
    dot.node('G', 'Print custom\nerror message',          shape='parallelogram')
    dot.node('H', 'End',                                 shape='ellipse')

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
    # Only use filled markers to avoid matplotlib edgecolor warning
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


# Alias so tasks.py call of utils.generate_result_q2(...) works
def generate_result_q2(save_path):
    """Alias for generate_result_plot_q2 — matches tasks.py call."""
    generate_result_plot_q2(save_path)


def generate_result_plot_q2(save_path):
    """Terminal-style output image demonstrating Q2 file handling."""
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
    """One image per page, scaled to fill as much of the page as possible."""
    c.showPage()
    if not os.path.exists(img_path):
        c.setFont("Helvetica", 12)
        c.drawCentredString(page_width / 2, page_height / 2,
                            f"[Image not found: {img_path}]")
        return

    img      = ImageReader(img_path)
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


# ---------- Main PDF Generator ----------
def generate_pdf(student_name, matric_number,
                 analysis_q1, analysis_q2,
                 flowchart_q1_path, flowchart_q2_path,
                 result_q1_path, result_q2_path,
                 algo_q1, algo_q2,
                 impl_q1, impl_q2,
                 save_path):

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
                     "Figure 1: Flowchart – Question 1 (Multiple Linear Regression)", W, H)
    _draw_image_page(c, result_q1_path,
                     "Figure 3: Actual vs Predicted – Question 1", W, H)

    # ── QUESTION 2 — always a brand new page ──────────────────────────────
    c.showPage()
    y = H - 55

    y = _draw_heading(c, "QUESTION 2", LEFT, y, H, font_size=15)
    y = _draw_heading(c, "Problem Statement", LEFT, y, H)
    y = _draw_paragraph(c,
        "Write a Python function that takes a file name and returns its content. "
        "The program should handle file not found errors and print a custom message "
        "when the file does not exist.",
        LEFT, y, W, H)
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
                     "Figure 2: Flowchart – Question 2 (File Reading)", W, H)
    _draw_image_page(c, result_q2_path,
                     "Figure 4: File Handling Demo – Question 2", W, H)

    c.save()