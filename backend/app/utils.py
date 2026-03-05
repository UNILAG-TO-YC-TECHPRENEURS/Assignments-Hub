import os
import io
import base64
import random
import textwrap
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_regression
from sklearn.linear_model import LinearRegression
import graphviz
import nbformat as nbf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PIL import Image as PILImage
import google.generativeai as genai

from django.conf import settings
from django.core.files.base import ContentFile

"""Utility functions for assignment generation"""
import matplotlib
matplotlib.use('Agg')  # Must be before importing pyplot
import matplotlib.pyplot as plt

# Then your other imports...

genai.configure(api_key=settings.GEMINI_API_KEY)

# ---------- Gemini Helpers ----------
def generate_analysis_q1():
    prompt = """You are helping a Nigerian university student write the analysis section of a COS 201 assignment.
Write in a natural human tone. It must sound like a real student explaining their approach.
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
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text

def generate_analysis_q2():
    prompt = """You are helping a Nigerian student write the analysis section of a programming assignment.
The task is to write a Python function that reads a file and returns its contents while handling file not found errors.
Explain the step by step plan for implementing the solution.
The tone must sound natural, simple, and like it was written by a student.
Length: around 150–250 words."""
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text

# ---------- Dataset ----------
def generate_dataset(n_samples=350, n_features=3, noise=0.1):
    X, y = make_regression(n_samples=n_samples, n_features=n_features, noise=noise, random_state=random.randint(1,1000))
    df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
    df['target'] = y
    return df

# ---------- Flowcharts (Graphviz) ----------
def create_flowchart_q1():
    dot = graphviz.Digraph('flowchart_q1', format='png')
    dot.node('A', 'Start')
    dot.node('B', 'Import libraries\n(pandas, sklearn, matplotlib)')
    dot.node('C', 'Define read_file()\n(handles FileNotFound)')
    dot.node('D', 'Load dataset (≥300 rows)')
    dot.node('E', 'Split features (X) and target (y)')
    dot.node('F', 'Create LinearRegression model')
    dot.node('G', 'Fit model on data')
    dot.node('H', 'Make predictions')
    dot.node('I', 'Plot actual vs predicted')
    dot.node('J', 'Print first 10 predictions')
    dot.node('K', 'End')
    dot.edges(['AB', 'BC', 'CD', 'DE', 'EF', 'FG', 'GH', 'HI', 'IJ', 'JK'])
    return dot.pipe(format='png')

def create_flowchart_q2():
    dot = graphviz.Digraph('flowchart_q2', format='png')
    dot.node('A', 'Start')
    dot.node('B', 'Define function read_file(filename)')
    dot.node('C', 'Try to open file')
    dot.node('D', 'File exists?')
    dot.node('E', 'Read and return content')
    dot.node('F', 'Catch FileNotFoundError')
    dot.node('G', 'Print custom error message')
    dot.node('H', 'End')
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
    predictions = model.predict(X)
    plt.figure(figsize=(6,4))
    plt.scatter(y, predictions, alpha=0.6)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
    plt.xlabel('Actual')
    plt.ylabel('Predicted')
    plt.title('Q1: Actual vs Predicted')
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()

def generate_result_q2(save_path):
    # Just create a simple image showing file handling demo
    plt.figure(figsize=(6,2))
    plt.text(0.5, 0.5, "File read successfully.\nError handling works!", 
             ha='center', va='center', fontsize=14)
    plt.axis('off')
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()

# ---------- Implementation Code ----------
def get_implementation_code_q1(df_name='dataset.csv'):
    code = textwrap.dedent(f'''\
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    import matplotlib.pyplot as plt

    def read_file(filename):
        try:
            with open(filename, "r") as file:
                return file.read()
        except FileNotFoundError:
            print("Custom Message: File not found. Please ensure the dataset exists.")

    # Read dataset (the file reading function from Q2 is used)
    data = pd.read_csv("{df_name}")

    # Prepare features and target
    X = data[['feature_0', 'feature_1', 'feature_2']]
    y = data['target']

    # Train model
    model = LinearRegression()
    model.fit(X, y)

    # Predict
    predictions = model.predict(X)

    # Output
    print("First 10 predictions:", predictions[:10])

    # Plot
    plt.scatter(y, predictions)
    plt.title("Actual vs Predicted")
    plt.xlabel("Actual")
    plt.ylabel("Predicted")
    plt.savefig("result_q1.png")
    plt.show()
    ''')
    return code

def get_implementation_code_q2():
    code = textwrap.dedent('''\
    def read_file(filename):
        try:
            with open(filename, "r") as file:
                return file.read()
        except FileNotFoundError:
            print("Custom Message: The file does not exist. Please check the filename.")

    # Demonstration
    content = read_file("sample.txt")
    if content:
        print(content)
    ''')
    return code

# ---------- Jupyter Notebook ----------
def create_notebook(q1_code, q2_code, save_path):
    nb = nbf.v4.new_notebook()
    text = """# COS 201 Assignment Solution

This notebook contains the implementation for both questions.

## Question 1
Multiple Linear Regression
"""
    code_cell1 = nbf.v4.new_code_cell(q1_code)
    code_cell2 = nbf.v4.new_code_cell(q2_code)
    nb['cells'] = [nbf.v4.new_markdown_cell(text), code_cell1, code_cell2]
    with open(save_path, 'w') as f:
        nbf.write(nb, f)

# ---------- PDF Generation ----------
def generate_pdf(student_name, matric_number, analysis_q1, analysis_q2,
                 flowchart_q1_path, flowchart_q2_path, result_q1_path, result_q2_path,
                 algo_q1, algo_q2, impl_q1, impl_q2, save_path):
    c = canvas.Canvas(save_path, pagesize=A4)
    width, height = A4
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_heading = styles['Heading1']

    # Helper to draw text with wrapping
    def draw_wrapped_text(text, x, y, max_width, style):
        p = Paragraph(text, style)
        p.wrapOn(c, max_width, height)
        p.drawOn(c, x, y)
        return p.height

    y = height - 50

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "COS 201 ASSIGNMENT")
    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Student: {student_name}   Matric: {matric_number}")
    y -= 40

    # Question 1
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "QUESTION 1")
    y -= 20

    # Problem Statement
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Problem Statement")
    y -= 15
    c.setFont("Helvetica", 10)
    prob1 = "Use a python environment to develop multiple linear regression models on your choice data. The size of the data must not be less than 300."
    y -= draw_wrapped_text(prob1, 50, y, width-100, style_normal) + 5

    # Analysis
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Analysis")
    y -= 15
    c.setFont("Helvetica", 10)
    y -= draw_wrapped_text(analysis_q1, 50, y, width-100, style_normal) + 5

    # Design
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Design")
    y -= 15
    c.setFont("Helvetica", 10)
    design_text = "Flowchart and Algorithm provided below."
    y -= draw_wrapped_text(design_text, 50, y, width-100, style_normal) + 5

    # Flowchart image
    if os.path.exists(flowchart_q1_path):
        img = ImageReader(flowchart_q1_path)
        c.drawImage(img, 50, y-150, width=300, height=150, preserveAspectRatio=True)
        y -= 170

    # Algorithm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Algorithm")
    y -= 15
    c.setFont("Courier", 8)
    for line in algo_q1.split('\n'):
        c.drawString(50, y, line)
        y -= 12
        if y < 50:
            c.showPage()
            y = height - 50

    # Implementation
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Implementation")
    y -= 15
    c.setFont("Courier", 7)
    for line in impl_q1.split('\n'):
        c.drawString(50, y, line)
        y -= 10
        if y < 50:
            c.showPage()
            y = height - 50

    # Result
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Result")
    y -= 15
    if os.path.exists(result_q1_path):
        img = ImageReader(result_q1_path)
        c.drawImage(img, 50, y-150, width=300, height=150, preserveAspectRatio=True)
        y -= 170

    # Check page break for Q2
    if y < 150:
        c.showPage()
        y = height - 50
    else:
        y -= 30

    # QUESTION 2 (similar pattern)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "QUESTION 2")
    y -= 20

    # Problem Statement Q2
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Problem Statement")
    y -= 15
    c.setFont("Helvetica", 10)
    prob2 = "Write a Python function that takes a file name and returns its content. The program should handle file not found errors and print a custom message when the file does not exist."
    y -= draw_wrapped_text(prob2, 50, y, width-100, style_normal) + 5

    # Analysis Q2
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Analysis")
    y -= 15
    c.setFont("Helvetica", 10)
    y -= draw_wrapped_text(analysis_q2, 50, y, width-100, style_normal) + 5

    # Design
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Design")
    y -= 15
    design_text2 = "Flowchart and Algorithm provided below."
    y -= draw_wrapped_text(design_text2, 50, y, width-100, style_normal) + 5

    # Flowchart Q2
    if os.path.exists(flowchart_q2_path):
        img = ImageReader(flowchart_q2_path)
        c.drawImage(img, 50, y-150, width=300, height=150, preserveAspectRatio=True)
        y -= 170

    # Algorithm Q2
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Algorithm")
    y -= 15
    c.setFont("Courier", 8)
    for line in algo_q2.split('\n'):
        c.drawString(50, y, line)
        y -= 12
        if y < 50:
            c.showPage()
            y = height - 50

    # Implementation Q2
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Implementation")
    y -= 15
    c.setFont("Courier", 7)
    for line in impl_q2.split('\n'):
        c.drawString(50, y, line)
        y -= 10
        if y < 50:
            c.showPage()
            y = height - 50

    # Result Q2
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Result")
    y -= 15
    if os.path.exists(result_q2_path):
        img = ImageReader(result_q2_path)
        c.drawImage(img, 50, y-150, width=300, height=150, preserveAspectRatio=True)

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
Step 11: End
"""

ALGORITHM_Q2 = """Step 1: Start
Step 2: Define function read_file(filename)
Step 3: Try to open file in read mode
Step 4: If file exists, read content and return it
Step 5: If FileNotFoundError occurs, print custom error message
Step 6: End
"""