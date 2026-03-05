import os
import tempfile
import shutil
from datetime import datetime
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from .models import Token
from . import utils

import cloudinary
import cloudinary.uploader


def send_assignment_email(to_email: str, student_name: str, file_links: dict):
    links_html = "\n".join(
        f'<li><a href="{url}">{name}</a></li>'
        for name, url in file_links.items()
    )
    links_plain = "\n".join(
        f"- {name}: {url}" for name, url in file_links.items()
    )

    subject = "Your COS201 Assignment – Files Ready"
    body_plain = f"""Hello {student_name},

Your COS201 assignment has been generated successfully.
Download your files using the links below:

{links_plain}

Good luck with your studies!
"""
    body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
  <h2>Hello {student_name},</h2>
  <p>Your <strong>COS201 assignment</strong> has been generated successfully.</p>
  <p>Download your files using the links below:</p>
  <ul>{links_html}</ul>
  <hr/>
  <p style="font-size:0.9em; color:#666;">This email was generated automatically. Do not reply.</p>
</body>
</html>
"""
    msg = EmailMultiAlternatives(
        subject=subject,
        body=body_plain,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(body_html, "text/html")
    msg.send(fail_silently=False)


@shared_task
def generate_assignment_task(token_str, name, matric_number, email):
    try:
        token_obj = Token.objects.get(token=token_str, used=False)
    except Token.DoesNotExist:
        return {"error": "Token already used or invalid"}

    job_dir = tempfile.mkdtemp()

    try:
        # 1. Analyses
        print("📝 Generating analysis for Q1...")
        analysis_q1 = utils.generate_analysis_q1()
        print("📝 Generating analysis for Q2...")
        analysis_q2 = utils.generate_analysis_q2()

        # 2. Dataset
        print("📊 Generating dataset...")
        df = utils.generate_dataset()
        dataset_path = os.path.join(job_dir, 'dataset.csv')
        df.to_csv(dataset_path, index=False)

        # 3. Flowcharts
        print("📐 Creating flowcharts...")
        flowchart_q1_path = os.path.join(job_dir, 'flowchart_q1.png')
        with open(flowchart_q1_path, 'wb') as f:
            f.write(utils.create_flowchart_q1())

        flowchart_q2_path = os.path.join(job_dir, 'flowchart_q2.png')
        with open(flowchart_q2_path, 'wb') as f:
            f.write(utils.create_flowchart_q2())

        # 4. Model + plots
        print("📈 Training model and generating plots...")
        from sklearn.linear_model import LinearRegression
        feature_cols = [col for col in df.columns if col != 'target']
        if not feature_cols:
            raise ValueError("No feature columns found in dataset.")
        X = df[feature_cols]
        y = df['target']
        model = LinearRegression().fit(X, y)

        result_q1_path = os.path.join(job_dir, 'result_q1.png')
        utils.generate_result_plot_q1(df, model, X, y, result_q1_path)

        result_q2_path = os.path.join(job_dir, 'result_q2.png')
        utils.generate_result_q2(result_q2_path)

        # 5. Code
        impl_q1 = utils.get_implementation_code_q1('dataset.csv')
        impl_q2 = utils.get_implementation_code_q2()

        # 6. Notebook
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
            save_path=pdf_path,
        )

        # 8. Upload to Cloudinary
        print("☁️  Uploading files to Cloudinary...")
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_email = email.replace('@', '_at_').replace('.', '_dot_')
        prefix = f"{safe_email}_{ts}"

        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
        )

        upload_manifest = [
            ("COS201_ASSIGNMENT.pdf", pdf_path,          "raw",   f"{prefix}/COS201_ASSIGNMENT"),
            ("flowchart_q1.png",      flowchart_q1_path, "image", f"{prefix}/flowchart_q1"),
            ("flowchart_q2.png",      flowchart_q2_path, "image", f"{prefix}/flowchart_q2"),
            ("result_q1.png",         result_q1_path,    "image", f"{prefix}/result_q1"),
            ("result_q2.png",         result_q2_path,    "image", f"{prefix}/result_q2"),
            ("solution.ipynb",        notebook_path,     "raw",   f"{prefix}/solution"),
            ("dataset.csv",           dataset_path,      "raw",   f"{prefix}/dataset"),
        ]

        file_links = {}
        for display_name, local_path, res_type, public_id in upload_manifest:
            print(f"  ⬆️  Uploading {display_name}...")
            result = cloudinary.uploader.upload(
                local_path,
                public_id=f"assignments/{public_id}",
                resource_type=res_type,
                overwrite=True,
            )
            file_links[display_name] = result["secure_url"]
            print(f"  ✅ {display_name} → {result['secure_url']}")

        # 9. Save to DB immediately after upload — before email attempt.
        #    This means the frontend always gets the download links even if email fails.
        token_obj.used          = True
        token_obj.used_by_email = email
        token_obj.file_links    = file_links
        token_obj.task_status   = Token.AssignmentStatus.DONE
        token_obj.save(update_fields=['used', 'used_by_email', 'file_links', 'task_status'])
        print("✅ file_links saved to DB.")

        # 10. Send email — non-fatal: log failure but don't crash the task
        print(f"📧 Sending email to {email}...")
        try:
            send_assignment_email(to_email=email, student_name=name, file_links=file_links)
            print("✅ Email sent.")
        except Exception as email_err:
            # Email failed (e.g. unverified sender) but files are already uploaded.
            # Return success so the frontend still gets the download links.
            print(f"⚠️  Email failed (files still available): {email_err}")

        return {"success": True, "email": email, "file_links": file_links}

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        token_obj.task_status = Token.AssignmentStatus.FAILED
        token_obj.save(update_fields=['task_status'])
        raise e

    finally:
        shutil.rmtree(job_dir, ignore_errors=True)
        print(f"🧹 Cleaned up temp dir: {job_dir}")