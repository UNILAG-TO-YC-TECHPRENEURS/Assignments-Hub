import os
import tempfile
import shutil
from datetime import datetime
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from .models import Token205
from . import utils_205

import cloudinary
import cloudinary.uploader


def send_assignment_email(to_email, student_name, file_links):
    links_html  = "\n".join(f'<li><a href="{u}">{n}</a></li>' for n, u in file_links.items())
    links_plain = "\n".join(f"- {n}: {u}" for n, u in file_links.items())

    msg = EmailMultiAlternatives(
        subject="Your COS205 Assignment – Files Ready",
        body=f"Hello {student_name},\n\nYour COS205 assignment is ready.\n\n{links_plain}\n\nGood luck!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(f"""
<html><body style="font-family:Arial;line-height:1.6">
<h2>Hello {student_name},</h2>
<p>Your <strong>COS205 assignment</strong> is ready. Download your files:</p>
<ul>{links_html}</ul>
</body></html>""", "text/html")
    msg.send(fail_silently=False)


@shared_task
def generate_assignment205_task(token_str, name, matric_number, email):
    try:
        token_obj = Token205.objects.get(token=token_str, used=False)
    except Token205.DoesNotExist:
        return {"error": "Token already used or invalid"}

    token_obj.task_status = Token205.AssignmentStatus.PROCESSING
    token_obj.save(update_fields=['task_status'])

    job_dir = tempfile.mkdtemp()
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_email = email.replace('@', '_at_').replace('.', '_dot_')
    prefix = f"{safe_email}_{ts}"

    try:
        # 1. Analysis
        print("📝 Generating analysis...")
        analysis = utils_205.generate_analysis()

        # 2. Dataset
        print("📊 Generating energy demand dataset...")
        df, signal_padded, original_len, full_len = utils_205.generate_dataset()
        dataset_path = os.path.join(job_dir, 'energy_demand.csv')
        df.to_csv(dataset_path, index=False)

        # 3. Flowcharts
        print("📐 Creating flowcharts...")
        flowchart_dft_path = os.path.join(job_dir, 'flowchart_dft.png')
        with open(flowchart_dft_path, 'wb') as f:
            f.write(utils_205.create_flowchart_dft())

        flowchart_fft_path = os.path.join(job_dir, 'flowchart_fft.png')
        with open(flowchart_fft_path, 'wb') as f:
            f.write(utils_205.create_flowchart_fft())

        # 4. DFT / FFT analysis + plots
        print("📈 Computing DFT and FFT...")
        result_paths = utils_205.run_analysis(signal_padded, original_len, full_len, job_dir)

        # 5. Code + notebook
        impl_code = utils_205.get_implementation_code()
        print("📓 Creating Jupyter notebook...")
        notebook_path = os.path.join(job_dir, 'solution_205.ipynb')
        utils_205.create_notebook(impl_code, notebook_path)

        # 6. PDF
        print("📄 Generating PDF...")
        pdf_path = os.path.join(job_dir, 'COS205_ASSIGNMENT.pdf')
        utils_205.generate_pdf(
            student_name=name,
            matric_number=matric_number,
            analysis=analysis,
            flowchart_dft_path=flowchart_dft_path,
            flowchart_fft_path=flowchart_fft_path,
            result_paths=result_paths,
            algo_dft=utils_205.ALGORITHM_DFT,
            algo_fft=utils_205.ALGORITHM_FFT,
            impl_code=impl_code,
            save_path=pdf_path,
        )

        # 7. Upload to Cloudinary
        print("☁️  Uploading files to Cloudinary...")
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
        )

        upload_manifest = [
            ("COS205_ASSIGNMENT.pdf",    pdf_path,                         "raw",   f"{prefix}/COS205_ASSIGNMENT"),
            ("flowchart_dft.png",        flowchart_dft_path,               "image", f"{prefix}/flowchart_dft"),
            ("flowchart_fft.png",        flowchart_fft_path,               "image", f"{prefix}/flowchart_fft"),
            ("original_signal.png",      result_paths['signal'],           "image", f"{prefix}/original_signal"),
            ("dft_serial_magnitude.png", result_paths['dft_serial_mag'],   "image", f"{prefix}/dft_serial_magnitude"),
            ("dft_parallel_magnitude.png",result_paths['dft_parallel_mag'],"image", f"{prefix}/dft_parallel_magnitude"),
            ("fft_magnitude.png",        result_paths['fft_mag'],          "image", f"{prefix}/fft_magnitude"),
            ("comparison.png",           result_paths['comparison'],       "image", f"{prefix}/comparison"),
            ("solution_205.ipynb",       notebook_path,                    "raw",   f"{prefix}/solution_205"),
            ("energy_demand.csv",        dataset_path,                     "raw",   f"{prefix}/energy_demand"),
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

        # 8. Save to DB before email so download always works
        token_obj.used          = True
        token_obj.used_by_email = email
        token_obj.file_links    = file_links
        token_obj.task_status   = Token205.AssignmentStatus.DONE
        token_obj.save(update_fields=['used', 'used_by_email', 'file_links', 'task_status'])
        print("✅ file_links saved to DB.")

        # 9. Email (non-fatal)
        print(f"📧 Sending email to {email}...")
        try:
            send_assignment_email(to_email=email, student_name=name, file_links=file_links)
            print("✅ Email sent.")
        except Exception as email_err:
            print(f"⚠️  Email failed (files still available): {email_err}")

        return {"success": True, "email": email, "file_links": file_links}

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        token_obj.task_status = Token205.AssignmentStatus.FAILED
        token_obj.save(update_fields=['task_status'])
        raise e

    finally:
        shutil.rmtree(job_dir, ignore_errors=True)
        print(f"🧹 Cleaned up temp dir: {job_dir}")