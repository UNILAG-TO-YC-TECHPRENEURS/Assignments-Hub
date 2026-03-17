import os
import tempfile
import shutil
import zipfile
from datetime import datetime
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from .models import Token
from . import utils

import cloudinary
import cloudinary.uploader


def create_zip_archive(file_paths, zip_path):
    """Create a zip archive containing all files in file_paths."""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for fp in file_paths:
            if os.path.exists(fp):
                zipf.write(fp, arcname=os.path.basename(fp))
    return zip_path


def send_assignment_email(to_email: str, student_name: str, zip_path: str, course: str = "COS201"):
    """Send an email with the zip file attached."""
    subject = f"Your {course} Assignment - Files Attached"
    body_plain = f"""Hello {student_name},

Your {course} assignment has been generated successfully.
All files are attached as a ZIP archive.

Good luck with your studies!
"""
    body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #0A0F1E 0%, #1a1f2e 100%); border-radius: 12px; padding: 30px; color: #fff;">
        <h2 style="margin-top: 0; color: #3b83f7;">Hello {student_name},</h2>
        <p>Your <strong style="color: #3b83f7;">{course} assignment</strong> has been generated successfully.</p>
        <p>All files are attached as a ZIP archive.</p>
        <hr style="border: 1px solid #3b83f733; margin: 20px 0;">
        <p style="font-size:0.9em; color:#aaa;">This email was generated automatically. Do not reply.</p>
    </div>
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
    with open(zip_path, 'rb') as f:
        msg.attach(f"{course}_Assignment_{student_name}.zip", f.read(), 'application/zip')
    msg.send(fail_silently=False)


@shared_task
def generate_assignment_task(token_str, name, matric_number, email, department):
    try:
        token_obj = Token.objects.get(token=token_str, used=False)
    except Token.DoesNotExist:
        return {"error": "Token already used or invalid"}

    job_dir = tempfile.mkdtemp()

    try:
        # ── Defaults (overridden per department below) ─────────────────────
        q1_problem_statement = None
        q2_problem_statement = None
        algo_q2              = utils.ALGORITHM_Q2
        flowchart_q2_path    = os.path.join(job_dir, 'flowchart_q2.png')
        result_q2_path       = os.path.join(job_dir, 'result_q2.png')

        # ── Q2 analysis: default for CS/Geo, overridden for Chem ───────────
        print("📝 Generating analysis for Q2...")
        analysis_q2 = utils.generate_analysis_q2()

        # ── Department-specific Q1 setup ───────────────────────────────────
        print("📝 Generating analysis for Q1...")

        if department == 'geo':
            analysis_q1       = utils.generate_analysis_geo()
            df                = utils.generate_seismic_dataset()
            flowchart_q1_path = os.path.join(job_dir, 'flowchart_geo.png')
            with open(flowchart_q1_path, 'wb') as f:
                f.write(utils.create_flowchart_geo())
            impl_q1   = utils.get_implementation_code_geo('dataset.csv')
            plot_func = utils.generate_seismic_plot

            q1_problem_statement = (
                "Use an interactive Python environment to analyze seismic data. "
                "Load the provided dataset, plot the time series, compute basic statistics "
                "(mean, standard deviation), and identify peaks or anomalies."
            )

            # Default Q2 (file reading)
            impl_q2 = utils.get_implementation_code_q2()
            with open(flowchart_q2_path, 'wb') as f:
                f.write(utils.create_flowchart_q2())
            utils.generate_result_q2(result_q2_path)

        elif department == 'chem':
            analysis_q1       = utils.generate_analysis_chem()
            df                = utils.generate_chem_dataset()
            flowchart_q1_path = os.path.join(job_dir, 'flowchart_chem.png')
            with open(flowchart_q1_path, 'wb') as f:
                f.write(utils.create_flowchart_chem())
            impl_q1   = utils.get_implementation_code_chem('dataset.csv')
            plot_func = utils.generate_chem_plot

            q1_problem_statement = (
                "Use the ChEMBL database to discover chemicals that can inhibit the Plasmodium falciparum "
                "protein target. Retrieve molecules and their molecular descriptors (molecular weight "
                "and ALogP) using the ChEMBL REST API."
            )

            # Chem-specific Q2 — ChEMBL descriptor lookup
            print("📝 Generating chem Q2 content...")
            analysis_q2          = utils.generate_analysis_chem_q2()
            algo_q2              = utils.ALGORITHM_Q2_CHEM
            impl_q2              = utils.get_implementation_code_chem_q2()
            q2_problem_statement = (
                "Use the ChEMBL ID to get the molecular descriptors of the molecules. "
                "Write a Python function that takes a ChEMBL ID and returns its molecular "
                "descriptors (molecular weight and ALogP) using the ChEMBL REST API. "
                "The function should handle errors when an invalid ID is provided and "
                "print a custom error message."
            )
            with open(flowchart_q2_path, 'wb') as f:
                f.write(utils.create_flowchart_chem_q2())
            utils.generate_result_chem_q2(result_q2_path)

        else:  # default: Computer Science
            analysis_q1       = utils.generate_analysis_q1()
            df                = utils.generate_dataset()
            flowchart_q1_path = os.path.join(job_dir, 'flowchart_q1.png')
            with open(flowchart_q1_path, 'wb') as f:
                f.write(utils.create_flowchart_q1())
            impl_q1   = utils.get_implementation_code_q1('dataset.csv')
            plot_func = None  # handled separately (sklearn model)

            q1_problem_statement = (
                "Use a Python environment to develop multiple linear regression models on your "
                "choice data. The size of the data must not be less than 300."
            )

            # Default Q2 (file reading)
            impl_q2 = utils.get_implementation_code_q2()
            with open(flowchart_q2_path, 'wb') as f:
                f.write(utils.create_flowchart_q2())
            utils.generate_result_q2(result_q2_path)

        # ── Save dataset ───────────────────────────────────────────────────
        dataset_path = os.path.join(job_dir, 'dataset.csv')
        df.to_csv(dataset_path, index=False)

        # ── Generate Q1 plot ───────────────────────────────────────────────
        print("📈 Generating Q1 plot...")
        result_q1_path = os.path.join(job_dir, 'result_q1.png')

        if department in ('geo', 'chem'):
            plot_func(df, result_q1_path)
        else:  # Computer Science
            from sklearn.linear_model import LinearRegression
            feature_cols = [col for col in df.columns if col != 'target']
            if not feature_cols:
                raise ValueError("No feature columns found in dataset.")
            X     = df[feature_cols]
            y     = df['target']
            model = LinearRegression().fit(X, y)
            utils.generate_result_plot_q1(df, model, X, y, result_q1_path)

        # ── Notebook ───────────────────────────────────────────────────────
        print("📓 Creating Jupyter notebook...")
        notebook_path = os.path.join(job_dir, 'solution.ipynb')
        utils.create_notebook(impl_q1, impl_q2, notebook_path)

        # ── PDF ────────────────────────────────────────────────────────────
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
            algo_q2=algo_q2,
            impl_q1=impl_q1,
            impl_q2=impl_q2,
            save_path=pdf_path,
            q1_problem_statement=q1_problem_statement,
            q2_problem_statement=q2_problem_statement,
        )

        # ── ZIP ────────────────────────────────────────────────────────────
        print("📦 Creating ZIP archive...")
        all_files = [
            pdf_path, flowchart_q1_path, flowchart_q2_path,
            result_q1_path, result_q2_path, notebook_path, dataset_path
        ]
        safe_email = email.replace('@', '_at_').replace('.', '_dot_')
        zip_path   = os.path.join(job_dir, f"COS201_Assignment_{safe_email}.zip")
        create_zip_archive(all_files, zip_path)
        print(f"✅ ZIP archive created: {zip_path}")

        # ── Cloudinary upload ──────────────────────────────────────────────
        print("☁️  Uploading files to Cloudinary...")
        ts     = datetime.now().strftime('%Y%m%d_%H%M%S')
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
            ("COS201_Assignment.zip", zip_path,          "raw",   f"{prefix}/COS201_Assignment"),
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

        # ── Save to DB ─────────────────────────────────────────────────────
        token_obj.used           = True
        token_obj.used_by_email  = email
        token_obj.file_links     = file_links
        token_obj.task_status    = Token.AssignmentStatus.DONE
        token_obj.save(update_fields=['used', 'used_by_email', 'file_links', 'task_status'])
        print("✅ file_links saved to DB.")

        # ── Email ──────────────────────────────────────────────────────────
        print(f"📧 Sending email to {email}...")
        try:
            send_assignment_email(to_email=email, student_name=name,
                                  zip_path=zip_path, course="COS201")
            print("✅ Email sent with ZIP attachment.")
        except Exception as email_err:
            print(f"⚠️  Email failed (files still available via Cloudinary): {email_err}")

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