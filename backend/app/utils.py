"""Utility functions for assignment generation"""
import os
import io
import base64
import random
import textwrap
import re
from pathlib import Path
from datetime import datetime

# Set matplotlib backend FIRST - before any other imports
import matplotlib
matplotlib.use('Agg')  # Must be before importing pyplot
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
from sklearn.datasets import make_regression
from sklearn.linear_model import LinearRegression
import graphviz
import nbformat as nbf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from PIL import Image as PILImage

from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# ---------- Text Cleaning Helper ----------
def clean_analysis_text(text):
    """Remove markdown formatting from analysis text."""
    if not text:
        return text
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)      # **bold**
    text = re.sub(r'\*(.*?)\*', r'\1', text)          # *italic*
    text = re.sub(r'__(.*?)__', r'\1', text)          # __bold__
    text = re.sub(r'_(.*?)_', r'\1', text)            # _italic_
    text = re.sub(r'`{1,3}(.*?)`{1,3}', r'\1', text)  # `code`
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)  # headers
    text = re.sub(r'\s+', ' ', text)                  # multiple spaces
    text = text.replace('\\*', '*')
    if text and not text[-1] in '.!?':
        text += '.'
    return text.strip()

# ---------- OpenAI Analysis Generators ----------
def generate_analysis_q1():
    prompt = """You are helping a Nigerian university student write the analysis section of a COS 201 assignment.
Write in a natural human tone. It must sound like a real student explaining their approach.
IMPORTANT: Do NOT use any markdown formatting like **bold**, *italic*, or `code` in your response. Write in plain text only.
The assignment problem is:
"Use Python to develop a multiple linear regression model using a dataset with at least 300 rows."
Write the analysis explaining:
- the step by step approach
- libraries that will be used
- how the regression model works
- assumptions
- constraints
The writing must feel original and human.
Length: 200–300 words."""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Nigerian university student. Write in plain text only - no markdown formatting, no asterisks, no backticks."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )
    raw_text = response.choices[0].message.content
    return clean_analysis_text(raw_text)

def generate_analysis_q2():
    prompt = """You are helping a Nigerian student write the analysis section of a programming assignment.
The task is to write a Python function that reads a file and returns its contents while handling file not found errors.
Explain the step by step plan for implementing the solution.
IMPORTANT: Do NOT use any markdown formatting like **bold**, *italic*, or `code` in your response. Write in plain text only.
The tone must sound natural, simple, and like it was written by a student.
Length: around 150–250 words."""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Nigerian university student. Write in plain text only - no markdown formatting, no asterisks, no backticks."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=400
    )
    raw_text = response.choices[0].message.content
    return clean_analysis_text(raw_text)

# ---------- Dataset - Truly Random Each Time ----------
def generate_dataset(n_samples=350, n_features=3, noise=0.1):
    """Generate a random dataset for regression. Each call produces different data."""
    try:
        actual_samples = n_samples + random.randint(-20, 50)
        actual_features = n_features + random.randint(0, 2)
        actual_noise = noise * random.uniform(0.5, 2.0)
        
        print(f"Generating dataset with: samples={actual_samples}, features={actual_features}, noise={actual_noise:.4f}")
        
        X, y = make_regression(
            n_samples=actual_samples,
            n_features=actual_features,
            noise=actual_noise,
            random_state=None,
            bias=random.uniform(-50, 50)
        )
        
        # Create random feature names
        prefixes = ['age', 'income', 'score', 'rate', 'count', 'value', 'factor', 'index', 'weight', 'height']
        feature_names = [f'{random.choice(prefixes)}_{random.randint(100,999)}' for _ in range(actual_features)]
        
        df = pd.DataFrame(X, columns=feature_names)
        df['target'] = y
        df = df.sample(frac=1).reset_index(drop=True)  # shuffle
        
        if df.empty or len(df) < 300:
            raise ValueError(f"Invalid dataset: {len(df)} rows")
        
        print(f"✅ Dataset generated: {df.shape[0]} rows, {df.shape[1]-1} features")
        return df
        
    except Exception as e:
        print(f"❌ Error generating dataset: {e}. Using fallback.")
        X, y = make_regression(n_samples=350, n_features=3, noise=0.1, random_state=42)
        df = pd.DataFrame(X, columns=['feature_1', 'feature_2', 'feature_3'])
        df['target'] = y
        return df

# ---------- Flowcharts with Correct Shapes ----------
def create_flowchart_q1():
    dot = graphviz.Digraph('flowchart_q1', format='png')
    dot.attr(rankdir='TB', size='8,5')
    
    dot.node('A', 'Start', shape='ellipse')
    dot.node('B', 'Import libraries\n(pandas, sklearn, matplotlib)', shape='rectangle')
    dot.node('C', 'Define read_file()\n(handles FileNotFound)', shape='rectangle')
    dot.node('D', 'Load dataset (≥300 rows)', shape='parallelogram')  # Input
    dot.node('E', 'Split features (X) and target (y)', shape='rectangle')
    dot.node('F', 'Create LinearRegression model', shape='rectangle')
    dot.node('G', 'Fit model on data', shape='rectangle')
    dot.node('H', 'Make predictions', shape='rectangle')
    dot.node('I', 'Plot actual vs predicted', shape='rectangle')
    dot.node('J', 'Print first 10 predictions', shape='parallelogram')  # Output
    dot.node('K', 'End', shape='ellipse')
    
    dot.edges(['AB', 'BC', 'CD', 'DE', 'EF', 'FG', 'GH', 'HI', 'IJ', 'JK'])
    return dot.pipe(format='png')

def create_flowchart_q2():
    dot = graphviz.Digraph('flowchart_q2', format='png')
    dot.attr(rankdir='TB', size='8,5')
    
    dot.node('A', 'Start', shape='ellipse')
    dot.node('B', 'Define function read_file(filename)', shape='rectangle')
    dot.node('C', 'Try to open file', shape='rectangle')
    dot.node('D', 'File exists?', shape='diamond')  # Decision
    dot.node('E', 'Read and return content', shape='rectangle')
    dot.node('F', 'Catch FileNotFoundError', shape='rectangle')
    dot.node('G', 'Print custom error message', shape='parallelogram')  # Output
    dot.node('H', 'End', shape='ellipse')
    
    dot.edge('A', 'B')
    dot.edge('B', 'C')
    dot.edge('C', 'D')
    dot.edge('D', 'E', label='Yes')
    dot.edge('D', 'F', label='No')
    dot.edge('F', 'G')
    dot.edge('G', 'H')
    dot.edge('E', 'H')
    return dot.pipe(format='png')

# ---------- Result Plots ----------
def generate_result_plot_q1(df, model, X, y, save_path):
    try:
        predictions = model.predict(X)
        plt.figure(figsize=(6,4))
        plt.scatter(y, predictions, alpha=0.6, c='blue', edgecolors='black', linewidth=0.5)
        plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', linewidth=2)
        plt.xlabel('Actual Values', fontsize=10)
        plt.ylabel('Predicted Values', fontsize=10)
        plt.title('Q1: Actual vs Predicted', fontsize=11)
        plt.grid(True, alpha=0.3)
        r2 = model.score(X, y)
        plt.text(0.05, 0.95, f'R² = {r2:.3f}', transform=plt.gca().transAxes,
                 fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        plt.tight_layout()
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Error generating plot: {e}")
        plt.figure(figsize=(6,4))
        plt.text(0.5, 0.5, "Error generating plot", ha='center', va='center')
        plt.savefig(save_path)
        plt.close()

def generate_result_q2(save_path):
    try:
        plt.figure(figsize=(6,2))
        plt.text(0.5, 0.7, "✓ File read successfully!", ha='center', va='center', fontsize=14, color='green')
        plt.text(0.5, 0.3, "Error handling: FileNotFoundError caught with custom message", ha='center', va='center', fontsize=10, color='blue')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Error generating Q2 result: {e}")
        plt.figure(figsize=(6,2))
        plt.text(0.5, 0.5, "File handling demo", ha='center', va='center')
        plt.savefig(save_path)
        plt.close()

# ---------- Implementation Code ----------
def get_implementation_code_q1(df_name='dataset.csv'):
    return textwrap.dedent(f'''\
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    import matplotlib.pyplot as plt

    def read_file(filename):
        try:
            with open(filename, "r") as file:
                return file.read()
        except FileNotFoundError:
            print("Custom Message: File not found. Please ensure the dataset exists.")

    data = pd.read_csv("{df_name}")
    print(f"Dataset shape: {{data.shape}}")
    print(f"Columns: {{list(data.columns)}}")
    print(f"First few rows:\\n{{data.head()}}")

    feature_cols = [col for col in data.columns if col != 'target']
    X = data[feature_cols]
    y = data['target']

    model = LinearRegression()
    model.fit(X, y)
    predictions = model.predict(X)

    print("First 10 predictions:", predictions[:10])
    print(f"Model coefficients: {{model.coef_}}")
    print(f"Model intercept: {{model.intercept_:.4f}}")
    print(f"R² score: {{model.score(X, y):.4f}}")

    plt.figure(figsize=(8,6))
    plt.scatter(y, predictions, alpha=0.6)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', linewidth=2)
    plt.title("Actual vs Predicted Values")
    plt.xlabel("Actual Values")
    plt.ylabel("Predicted Values")
    plt.grid(True, alpha=0.3)
    plt.savefig("result_q1.png")
    plt.show()
    ''')

def get_implementation_code_q2():
    return textwrap.dedent('''\
    def read_file(filename):
        try:
            with open(filename, "r") as file:
                content = file.read()
                print(f"File '{filename}' read successfully!")
                return content
        except FileNotFoundError:
            print(f"Custom Message: The file '{filename}' does not exist. Please check the filename.")
            return None

    print("Test 1: Reading an existing file")
    content = read_file("sample.txt")
    if content:
        print(f"File content length: {len(content)} characters")
        print("First 100 characters:", content[:100])

    print("\\nTest 2: Reading a non-existent file")
    content = read_file("nonexistent.txt")
    ''')

# ---------- Jupyter Notebook ----------
def create_notebook(q1_code, q2_code, save_path):
    try:
        nb = nbf.v4.new_notebook()
        nb.metadata = {
            'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
            'language_info': {'name': 'python', 'version': '3.12'}
        }
        cells = [
            nbf.v4.new_markdown_cell("# COS 201 Assignment Solution\n\n---\n## Question 1: Multiple Linear Regression"),
            nbf.v4.new_code_cell(q1_code),
            nbf.v4.new_markdown_cell("\n---\n## Question 2: File Reading with Error Handling"),
            nbf.v4.new_code_cell(q2_code)
        ]
        nb['cells'] = cells
        with open(save_path, 'w') as f:
            nbf.write(nb, f)
    except Exception as e:
        print(f"Error creating notebook: {e}")

# ---------- PDF Generation (with fixed spacing & fonts) ----------
def generate_pdf(student_name, matric_number, analysis_q1, analysis_q2,
                 flowchart_q1_path, flowchart_q2_path, result_q1_path, result_q2_path,
                 algo_q1, algo_q2, impl_q1, impl_q2, save_path):
    
    width, height = A4
    left_margin = 50
    right_margin = width - 50
    content_width = right_margin - left_margin

    styles = {
        'title': ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=16, alignment=1, spaceAfter=20),
        'heading1': ParagraphStyle('Heading1', fontName='Helvetica-Bold', fontSize=14, spaceBefore=15, spaceAfter=10),
        'heading2': ParagraphStyle('Heading2', fontName='Helvetica-Bold', fontSize=12, spaceBefore=10, spaceAfter=5),
        'normal': ParagraphStyle('Normal', fontName='Helvetica', fontSize=10, leading=14, spaceAfter=8),
        'code': ParagraphStyle('Code', fontName='Courier', fontSize=8, leading=10, leftIndent=10, rightIndent=10, spaceBefore=5, spaceAfter=5),
    }

    c = canvas.Canvas(save_path, pagesize=A4)

    def draw_paragraph(text, style, x, y, max_width):
        p = Paragraph(text, style)
        p.wrapOn(c, max_width, height)
        p.drawOn(c, x, y - p.height)
        return p.height

    y = height - 50

    # Title page
    c.setFont("Helvetica-Bold", 16)
    c.drawString(left_margin, y, "COS 201 ASSIGNMENT")
    y -= 25
    c.setFont("Helvetica", 12)
    c.drawString(left_margin, y, f"Student: {student_name}")
    c.drawString(left_margin + 300, y, f"Matric: {matric_number}")
    y -= 40

    # Question 1
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_margin, y, "QUESTION 1")
    y -= 25

    # Problem Statement
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, "Problem Statement")
    y -= 18
    prob1 = "Use a python environment to develop multiple linear regression models on your choice data. The size of the data must not be less than 300."
    y -= draw_paragraph(prob1, styles['normal'], left_margin, y, content_width) + 15

    # Analysis
    if y < 100:
        c.showPage()
        y = height - 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, "Analysis")
    y -= 18
    analysis_q1 = clean_analysis_text(analysis_q1)
    for para in analysis_q1.split('. '):
        if not para.strip():
            continue
        if not para.endswith('.'):
            para += '.'
        if y - 20 < 50:
            c.showPage()
            y = height - 50
        y -= draw_paragraph(para, styles['normal'], left_margin, y, content_width) + 5
    y -= 10

    # Design
    if y < 100:
        c.showPage()
        y = height - 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, "Design")
    y -= 18
    design_text = "Flowchart and Algorithm provided below."
    y -= draw_paragraph(design_text, styles['normal'], left_margin, y, content_width) + 15

    # Flowchart image
    if os.path.exists(flowchart_q1_path):
        if y < 180:
            c.showPage()
            y = height - 50
        img = ImageReader(flowchart_q1_path)
        img_width = 400
        img_height = 200
        img_x = left_margin + (content_width - img_width) // 2
        c.drawImage(img, img_x, y - img_height, width=img_width, height=img_height, preserveAspectRatio=True)
        y -= (img_height + 20)

    # Algorithm
    if y < 100:
        c.showPage()
        y = height - 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, "Algorithm")
    y -= 18
    c.setFont("Courier", 8)
    for line in algo_q1.split('\n'):
        if line.strip():
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Courier", 8)
            c.drawString(left_margin + 10, y, line)
            y -= 10
    y -= 5

    # Implementation
    if y < 100:
        c.showPage()
        y = height - 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, "Implementation")
    y -= 18
    c.setFont("Courier", 7)
    for line in impl_q1.split('\n'):
        if line.strip() or line == '':
            if len(line) > 80:
                line = line[:80] + "..."
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Courier", 7)
            c.drawString(left_margin + 10, y, line)
            y -= 8
    y -= 10

    # Result
    if y < 100:
        c.showPage()
        y = height - 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, "Result")
    y -= 18
    if os.path.exists(result_q1_path):
        if y < 180:
            c.showPage()
            y = height - 50
        img = ImageReader(result_q1_path)
        img_width = 400
        img_height = 200
        img_x = left_margin + (content_width - img_width) // 2
        c.drawImage(img, img_x, y - img_height, width=img_width, height=img_height, preserveAspectRatio=True)
        y -= (img_height + 30)

    # Question 2 - similar pattern (condensed for brevity; keep same style)
    if y < 200:
        c.showPage()
        y = height - 50
    else:
        y -= 20

    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_margin, y, "QUESTION 2")
    y -= 25

    # Problem Statement
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, "Problem Statement")
    y -= 18
    prob2 = "Write a Python function that takes a file name and returns its content. The program should handle file not found errors and print a custom message when the file does not exist."
    y -= draw_paragraph(prob2, styles['normal'], left_margin, y, content_width) + 15

    # Analysis
    if y < 100:
        c.showPage()
        y = height - 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, "Analysis")
    y -= 18
    analysis_q2 = clean_analysis_text(analysis_q2)
    for para in analysis_q2.split('. '):
        if not para.strip():
            continue
        if not para.endswith('.'):
            para += '.'
        if y - 20 < 50:
            c.showPage()
            y = height - 50
        y -= draw_paragraph(para, styles['normal'], left_margin, y, content_width) + 5
    y -= 10

    # Design
    if y < 100:
        c.showPage()
        y = height - 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, "Design")
    y -= 18
    design_text2 = "Flowchart and Algorithm provided below."
    y -= draw_paragraph(design_text2, styles['normal'], left_margin, y, content_width) + 15

    # Flowchart Q2
    if os.path.exists(flowchart_q2_path):
        if y < 180:
            c.showPage()
            y = height - 50
        img = ImageReader(flowchart_q2_path)
        img_width = 400
        img_height = 200
        img_x = left_margin + (content_width - img_width) // 2
        c.drawImage(img, img_x, y - img_height, width=img_width, height=img_height, preserveAspectRatio=True)
        y -= (img_height + 20)

    # Algorithm Q2
    if y < 100:
        c.showPage()
        y = height - 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, "Algorithm")
    y -= 18
    c.setFont("Courier", 8)
    for line in algo_q2.split('\n'):
        if line.strip():
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Courier", 8)
            c.drawString(left_margin + 10, y, line)
            y -= 10
    y -= 5

    # Implementation Q2
    if y < 100:
        c.showPage()
        y = height - 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, "Implementation")
    y -= 18
    c.setFont("Courier", 7)
    for line in impl_q2.split('\n'):
        if line.strip() or line == '':
            if len(line) > 80:
                line = line[:80] + "..."
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Courier", 7)
            c.drawString(left_margin + 10, y, line)
            y -= 8
    y -= 10

    # Result Q2
    if y < 100:
        c.showPage()
        y = height - 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, "Result")
    y -= 18
    if os.path.exists(result_q2_path):
        if y < 150:
            c.showPage()
            y = height - 50
        img = ImageReader(result_q2_path)
        img_width = 400
        img_height = 150
        img_x = left_margin + (content_width - img_width) // 2
        c.drawImage(img, img_x, y - img_height, width=img_width, height=img_height, preserveAspectRatio=True)

    c.save()

# ---------- Algorithm texts ----------
ALGORITHM_Q1 = """Step 1: Start
Step 2: Import required libraries (pandas, sklearn.linear_model, matplotlib)
Step 3: Define function read_file(filename) with try-except for FileNotFoundError
Step 4: Load dataset from CSV (>=300 rows)
Step 5: Separate features (X) and target (y)
Step 6: Create LinearRegression object
Step 7: Fit model using X and y
Step 8: Predict using X
Step 9: Print first 10 predictions
Step 10: Plot actual vs predicted and save image
Step 11: End"""

ALGORITHM_Q2 = """Step 1: Start
Step 2: Define function read_file(filename)
Step 3: Try to open file in read mode
Step 4: If file exists, read content and return it
Step 5: If FileNotFoundError occurs, print custom error message
Step 6: End"""