import os
import tempfile
import shutil
from pathlib import Path
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
    try:
        # 1. Generate dynamic analyses
        analysis_q1 = utils.generate_analysis_q1()
        analysis_q2 = utils.generate_analysis_q2()

        # 2. Generate dataset
        df = utils.generate_dataset()
        dataset_path = os.path.join(job_dir, 'dataset.csv')
        df.to_csv(dataset_path, index=False)

        # 3. Flowcharts
        flowchart_q1 = utils.create_flowchart_q1()
        flowchart_q1_path = os.path.join(job_dir, 'flowchart_q1.png')
        with open(flowchart_q1_path, 'wb') as f:
            f.write(flowchart_q1)

        flowchart_q2 = utils.create_flowchart_q2()
        flowchart_q2_path = os.path.join(job_dir, 'flowchart_q2.png')
        with open(flowchart_q2_path, 'wb') as f:
            f.write(flowchart_q2)

        # 4. Result plots
        # For Q1 we need to train a quick model using the dataset
        from sklearn.linear_model import LinearRegression
        X = df[[c for c in df.columns if c.startswith('feature')]]
        y = df['target']
        model = LinearRegression().fit(X, y)
        result_q1_path = os.path.join(job_dir, 'result_q1.png')
        utils.generate_result_plot_q1(df, model, X, y, result_q1_path)

        result_q2_path = os.path.join(job_dir, 'result_q2.png')
        utils.generate_result_q2(result_q2_path)

        # 5. Implementation code
        impl_q1 = utils.get_implementation_code_q1('dataset.csv')
        impl_q2 = utils.get_implementation_code_q2()

        # 6. Jupyter notebook
        notebook_path = os.path.join(job_dir, 'solution.ipynb')
        utils.create_notebook(impl_q1, impl_q2, notebook_path)

        # 7. PDF
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

        # 8. Prepare email attachments
        attachments = [
            (pdf_path, 'application/pdf'),
            (flowchart_q1_path, 'image/png'),
            (flowchart_q2_path, 'image/png'),
            (result_q1_path, 'image/png'),
            (result_q2_path, 'image/png'),
            (notebook_path, 'application/x-ipynb+json'),
            (dataset_path, 'text/csv'),  # optionally include dataset
        ]

        # 9. Send email via SendGrid
        subject = "Your COS201 Assignment"
        body = f"Dear {name},\n\nPlease find attached your COS201 assignment solution.\n\nRegards,\nCOS201 Generator"
        from_email = settings.FROM_EMAIL
        to_email = [email]

        email_msg = EmailMessage(subject, body, from_email, to_email)
        for file_path, mime_type in attachments:
            with open(file_path, 'rb') as f:
                email_msg.attach(os.path.basename(file_path), f.read(), mime_type)

        email_msg.send(fail_silently=False)

        # 10. Mark token as used
        token_obj.used = True
        token_obj.used_by_email = email
        token_obj.save()

        return {"success": True, "email": email}

    except Exception as e:
        # Log error and maybe re-raise
        raise e
    finally:
        # Cleanup temp dir
        shutil.rmtree(job_dir, ignore_errors=True)