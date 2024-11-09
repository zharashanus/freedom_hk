from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BulkUpload, ResumeFile
from .tasks import process_resume_files
from django.core.files.storage import default_storage
import os

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
        
        # Запуск асинхронной задачи для обработки файлов
        process_resume_files.delay(bulk_upload.id)
        
        messages.success(request, 'Файлы успешно загружены и поставлены в очередь на обработку')
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
