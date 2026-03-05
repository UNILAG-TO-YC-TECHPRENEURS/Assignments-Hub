import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from .models import Token
from . import utils

@shared_task
def generate_assignment_task(token_str, name, matric_number, email):
    # Mark token as used immediately to prevent double generation
    try:
        token_obj = Token.objects.get(token=token_str, used=False)
    except Token.DoesNotExist:
        return {"error": "Token already used or invalid"}

    # Create temp directory for this job
    job_dir = tempfile.mkdtemp()
    
    # Create permanent directory for this assignment
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_email = email.replace('@', '_at_').replace('.', '_dot_')
    permanent_dir = Path(settings.BASE_DIR) / 'generated_assignments' / f"{safe_email}_{timestamp}"
    permanent_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 **SAVING FILES TO: {permanent_dir}**")
    
    try:
        # 1. Generate dynamic analyses
        print("📝 Generating analysis for Q1...")
        analysis_q1 = utils.generate_analysis_q1()
        print("📝 Generating analysis for Q2...")
        analysis_q2 = utils.generate_analysis_q2()

        # 2. Generate dataset
        print("📊 Generating dataset...")
        df = utils.generate_dataset()
        dataset_path = os.path.join(job_dir, 'dataset.csv')
        df.to_csv(dataset_path, index=False)

        # 3. Flowcharts
        print("📐 Creating flowchart for Q1...")
        flowchart_q1 = utils.create_flowchart_q1()
        flowchart_q1_path = os.path.join(job_dir, 'flowchart_q1.png')
        with open(flowchart_q1_path, 'wb') as f:
            f.write(flowchart_q1)

        print("📐 Creating flowchart for Q2...")
        flowchart_q2 = utils.create_flowchart_q2()
        flowchart_q2_path = os.path.join(job_dir, 'flowchart_q2.png')
        with open(flowchart_q2_path, 'wb') as f:
            f.write(flowchart_q2)

        # 4. Result plots
        print("📈 Training model and generating plots...")
        from sklearn.linear_model import LinearRegression

        print(f"🔍 DataFrame columns: {list(df.columns)}")
        print(f"🔍 DataFrame shape: {df.shape}")

        # Select all columns except 'target' as features
        feature_cols = [col for col in df.columns if col != 'target']
        print(f"🔍 Feature columns: {feature_cols}")

        if not feature_cols:
            raise ValueError("No feature columns found! Check dataset generation.")

        X = df[feature_cols]
        y = df['target']

        print(f"🔍 X shape: {X.shape}, y shape: {y.shape}")

        if len(X) == 0 or len(y) == 0:
            raise ValueError("Empty dataset generated")

        model = LinearRegression().fit(X, y)
        result_q1_path = os.path.join(job_dir, 'result_q1.png')
        utils.generate_result_plot_q1(df, model, X, y, result_q1_path)

        result_q2_path = os.path.join(job_dir, 'result_q2.png')
        utils.generate_result_q2(result_q2_path)

        # 5. Implementation code
        impl_q1 = utils.get_implementation_code_q1('dataset.csv')
        impl_q2 = utils.get_implementation_code_q2()

        # 6. Jupyter notebook
        print("📓 Creating Jupyter notebook...")
        notebook_path = os.path.join(job_dir, 'solution.ipynb')
        utils.create_notebook(impl_q1, impl_q2, notebook_path)

        # 7. PDF
        print("📄 Generating PDF...")
        pdf_path = os.path.join(job_dir, 'COS201_ASSIGNMENT.pdf')
        utils.generate_pdf(
            student_name=name,
            matric_number=matric_number,
            analysis_q1=analysis_q1,
            analysis_q2=analysis_q2,
            flowchart_q1_path=flowchart_q1_path,
            flowchart_q2_path=flowchart_q2_path,
            result_q1_path=result_q1_path,
            result_q2_path=result_q2_path,
            algo_q1=utils.ALGORITHM_Q1,
            algo_q2=utils.ALGORITHM_Q2,
            impl_q1=impl_q1,
            impl_q2=impl_q2,
            save_path=pdf_path
        )

        # 8. Prepare attachments list
        attachments = [
            ('COS201_ASSIGNMENT.pdf', pdf_path, 'application/pdf'),
            ('flowchart_q1.png', flowchart_q1_path, 'image/png'),
            ('flowchart_q2.png', flowchart_q2_path, 'image/png'),
            ('result_q1.png', result_q1_path, 'image/png'),
            ('result_q2.png', result_q2_path, 'image/png'),
            ('solution.ipynb', notebook_path, 'application/x-ipynb+json'),
            ('dataset.csv', dataset_path, 'text/csv'),
        ]

        # 9. Copy all files to permanent directory
        print(f"💾 Copying files to permanent location...")
        for filename, file_path, _ in attachments:
            if os.path.exists(file_path):
                dest_path = permanent_dir / filename
                shutil.copy2(file_path, dest_path)
                print(f"  ✅ Copied: {filename} ({os.path.getsize(file_path)} bytes)")

        with open(permanent_dir / 'analysis_q1.txt', 'w') as f:
            f.write(analysis_q1)
        with open(permanent_dir / 'analysis_q2.txt', 'w') as f:
            f.write(analysis_q2)

        with open(permanent_dir / 'implementation_q1.py', 'w') as f:
            f.write(impl_q1)
        with open(permanent_dir / 'implementation_q2.py', 'w') as f:
            f.write(impl_q2)

        # 10. Email simulation
        print(f"\n{'='*60}")
        print(f"📧 EMAIL WOULD BE SENT TO: {email}")
        print(f"{'='*60}")
        print(f"Subject: Your COS201 Assignment")
        print(f"From: noreply@example.com")
        print(f"Attachments:")
        for filename, file_path, _ in attachments:
            if os.path.exists(file_path):
                print(f"  - {filename} ({os.path.getsize(file_path)} bytes)")
        print(f"{'='*60}\n")
        print(f"✅ Email simulation complete for {email}")

        # 11. Mark token as used
        token_obj.used = True
        token_obj.used_by_email = email
        token_obj.save()

        # 12. README
        with open(permanent_dir / 'README.txt', 'w') as f:
            f.write(f"""COS201 ASSIGNMENT GENERATED
==========================
Student: {name}
Matric: {matric_number}
Email: {email}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FILES GENERATED:
- COS201_ASSIGNMENT.pdf : Complete assignment document
- flowchart_q1.png      : Flowchart for Question 1
- flowchart_q2.png      : Flowchart for Question 2
- result_q1.png         : Regression plot for Question 1
- result_q2.png         : File handling demo for Question 2
- solution.ipynb        : Jupyter notebook with code
- dataset.csv           : Generated dataset (350+ rows)
- analysis_q1.txt       : Analysis text for Question 1
- analysis_q2.txt       : Analysis text for Question 2
- implementation_q1.py  : Python code for Question 1
- implementation_q2.py  : Python code for Question 2

All files successfully generated!
""")

        return {
            "success": True,
            "email": email,
            "message": "Assignment generated successfully",
            "files_location": str(permanent_dir)
        }

    except Exception as e:
        print(f"❌ Error in generate_assignment_task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e
    finally:
        shutil.rmtree(job_dir, ignore_errors=True)
        print(f"🧹 Cleaned up temp directory: {job_dir}")
        print(f"📁 Your files are SAFE and saved in: {permanent_dir}")
        print(f"📂 Open this folder: file://{permanent_dir}")