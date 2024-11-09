from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BulkUpload, ResumeFile
from .tasks import process_resume_files
from celery.exceptions import OperationalError
from redis.exceptions import ConnectionError as RedisConnectionError
from freedom_hk.celery import app
import os
import logging

logger = logging.getLogger(__name__)

@login_required
def upload_resumes(request):
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Доступ запрещен')
        return redirect('recruiting_system:vacancy_list')
    
    if request.method == 'POST':
        files = request.FILES.getlist('resume_files')
        
        if not files:
            messages.error(request, 'Выберите файлы для загрузки')
            return redirect('convertor_to_json:upload_resumes')
            
        bulk_upload = BulkUpload.objects.create(
            recruiter=request.user.recruiter_profile,
            total_files=len(files)
        )
        
        for file in files:
            file_extension = os.path.splitext(file.name)[1].lower()[1:]
            
            if file_extension not in ['pdf', 'doc', 'docx', 'pptx', 'txt']:
                messages.warning(request, f'Неподдерживаемый формат файла: {file.name}')
                continue
                
            resume_file = ResumeFile.objects.create(
                bulk_upload=bulk_upload,
                file=file,
                file_type=file_extension,
                original_filename=file.name
            )
        
        try:
            if not app.conf.broker_connection_retry_on_startup:
                raise OperationalError("Celery broker connection not available")
            
            task = process_resume_files.apply_async(
                args=[bulk_upload.id],
                countdown=1,
                retry=True,
                retry_policy={
                    'max_retries': 3,
                    'interval_start': 0,
                    'interval_step': 0.2,
                    'interval_max': 0.5,
                }
            )
            logger.info(f"Task created successfully with id: {task.id}")
            
        except (OperationalError, RedisConnectionError) as e:
            logger.error(f"Redis connection error: {str(e)}")
            # Попробуем переподключиться к Redis
            try:
                app.conf.broker_connection_retry_on_startup = True
                task = process_resume_files.apply_async(args=[bulk_upload.id])
                logger.info(f"Task created successfully after retry with id: {task.id}")
            except Exception as retry_error:
                logger.error(f"Retry failed, falling back to synchronous processing: {str(retry_error)}")
                process_resume_files(bulk_upload.id)
                messages.warning(request, 'Файлы обработаны синхронно из-за проблем с подключением')
            
        except Exception as e:
            messages.error(request, f'Ошибка при загрузке файлов: {str(e)}')
            return redirect('convertor_to_json:upload_resumes')
            
        return redirect('convertor_to_json:upload_status', bulk_upload.id)
            
    return render(request, 'convertor_to_json/upload_form.html')

@login_required
def upload_status(request, upload_id):
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Доступ запрещен')
        return redirect('recruiting_system:vacancy_list')
        
    bulk_upload = get_object_or_404(BulkUpload, id=upload_id, recruiter=request.user.recruiter_profile)
    resume_files = bulk_upload.resume_files.all()
    
    return render(request, 'convertor_to_json/upload_status.html', {
        'bulk_upload': bulk_upload,
        'resume_files': resume_files
    })
