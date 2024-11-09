from celery import shared_task
from .models import BulkUpload, ResumeFile
from .services.text_processor import TextProcessor
from .services.nlp_processor import NLPProcessor
from .services.candidate_creator import CandidateCreator
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_resume_files(self, bulk_upload_id):
    text_processor = TextProcessor()
    nlp_processor = NLPProcessor()
    
    # Проверяем подключение к GPT
    if not nlp_processor.test_gpt_connection():
        logger.error("Failed to connect to GPT API")
        raise ValueError("GPT API connection failed")
        
    candidate_creator = CandidateCreator()
    
    try:
        bulk_upload = BulkUpload.objects.get(id=bulk_upload_id)
        bulk_upload.status = 'processing'
        bulk_upload.save()
        
        for resume_file in bulk_upload.resume_files.filter(status='pending'):
            try:
                # Извлечение текста
                extracted_text = text_processor.extract_text(
                    resume_file.file.path,
                    resume_file.file_type
                )
                
                # Обработка текста через NLP
                parsed_data = nlp_processor.process_resume(extracted_text)
                
                if parsed_data:
                    # Сохраняем извлеченные данные
                    resume_file.extracted_text = extracted_text
                    resume_file.parsed_data = parsed_data
                    
                    # Создаем профиль кандидата
                    candidate = candidate_creator.create_from_parsed_data(parsed_data)
                    resume_file.created_candidate = candidate
                    resume_file.status = 'converted'
                else:
                    resume_file.status = 'failed'
                    resume_file.error_message = 'Failed to parse resume data'
                
                resume_file.save()
                
            except Exception as e:
                logger.error(f"Error processing file {resume_file.id}: {str(e)}")
                resume_file.status = 'failed'
                resume_file.error_message = str(e)
                resume_file.save()
        
        bulk_upload.status = 'completed'
        bulk_upload.save()
        
    except Exception as e:
        logger.error(f"Error processing bulk upload {bulk_upload_id}: {str(e)}")
        raise self.retry(exc=e)
    