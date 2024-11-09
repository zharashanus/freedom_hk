from celery import shared_task
from .models import BulkUpload, ResumeFile
from .services.text_processor import TextProcessor
from .services.nlp_processor import NLPProcessor
from .services.candidate_creator import CandidateCreator
import logging
import gc

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def process_resume_files(self, bulk_upload_id):
    logger.info(f"Starting process_resume_files for bulk_upload_id: {bulk_upload_id}")
    text_processor = TextProcessor()
    nlp_processor = NLPProcessor()
    
    # Проверяем подключение к GPT
    logger.info("Testing GPT connection...")
    if not nlp_processor.test_gpt_connection():
        logger.error("Failed to connect to GPT API")
        raise ValueError("GPT API connection failed")
    
    logger.info("GPT connection successful")
    candidate_creator = CandidateCreator()
    
    try:
        bulk_upload = BulkUpload.objects.get(id=bulk_upload_id)
        bulk_upload.status = 'processing'
        bulk_upload.save()
        
        total_files = bulk_upload.resume_files.filter(status='pending').count()
        processed = 0
        
        for resume_file in bulk_upload.resume_files.filter(status='pending'):
            try:
                logger.info(f"Processing file {resume_file.id}: {resume_file.original_filename}")
                
                # Проверяем статус остановки
                bulk_upload.refresh_from_db()
                if bulk_upload.status == 'stopped':
                    logger.info(f"Processing stopped for bulk upload {bulk_upload_id}")
                    return

                # Извлечение текста
                extracted_text = text_processor.extract_text(
                    resume_file.file.path,
                    resume_file.file_type
                )
                
                if not extracted_text:
                    raise ValueError("Failed to extract text from file")
                
                logger.info(f"Text extracted successfully from {resume_file.original_filename}")
                
                # Обработка текста через NLP
                parsed_data = nlp_processor.process_resume(extracted_text)
                
                if parsed_data:
                    logger.info(f"Successfully parsed data from {resume_file.original_filename}")
                    resume_file.extracted_text = extracted_text
                    resume_file.parsed_data = parsed_data
                    
                    # Создаем профиль кандидата
                    candidate = candidate_creator.create_from_parsed_data(parsed_data)
                    if candidate:
                        resume_file.created_candidate = candidate
                        resume_file.status = 'converted'
                    else:
                        resume_file.status = 'failed'
                        resume_file.error_message = 'Failed to create candidate profile'
                else:
                    resume_file.status = 'failed'
                    resume_file.error_message = 'Failed to parse resume data'
                
                resume_file.save()
                processed += 1
                
                # Обновляем прогресс
                bulk_upload.processing_progress = (processed / total_files) * 100
                bulk_upload.save()
                
            except Exception as e:
                logger.error(f"Error processing file {resume_file.id}: {str(e)}")
                resume_file.status = 'failed'
                resume_file.error_message = str(e)
                resume_file.save()
                
            # Очищаем память после каждого файла
            gc.collect()
        
        bulk_upload.status = 'completed'
        bulk_upload.save()
        logger.info(f"Completed processing bulk upload {bulk_upload_id}")
        
    except Exception as e:
        logger.error(f"Error in bulk processing: {str(e)}")
        bulk_upload.status = 'failed'
        bulk_upload.save()
        raise self.retry(exc=e, countdown=60)
    
@shared_task(bind=True)
def process_resume_batch(self, bulk_upload_id):
    bulk_upload = BulkUpload.objects.get(id=bulk_upload_id)
    text_processor = TextProcessor()
    nlp_processor = NLPProcessor()
    candidate_creator = CandidateCreator()
    
    try:
        bulk_upload.status = 'processing'
        bulk_upload.save()
        
        pending_files = bulk_upload.resume_files.filter(status='pending')
        total_files = pending_files.count()
        batch_size = bulk_upload.batch_size
        
        for i in range(0, total_files, batch_size):
            batch = pending_files[i:i + batch_size]
            
            for resume_file in batch:
                try:
                    # Проверяем, не была ли остановлена обработка
                    bulk_upload.refresh_from_db()
                    if bulk_upload.status == 'stopped':
                        logger.info(f"Processing stopped for bulk upload {bulk_upload_id}")
                        return
                        
                    # Извлечение текста
                    extracted_text = text_processor.extract_text(
                        resume_file.file.path,
                        resume_file.file_type
                    )
                    
                    if not extracted_text:
                        raise ValueError("Не удалось извлечь текст из файла")
                    
                    # Обработка текста через NLP
                    parsed_data = nlp_processor.process_resume(extracted_text)
                    
                    if parsed_data:
                        resume_file.extracted_text = extracted_text
                        resume_file.parsed_data = parsed_data
                        candidate = candidate_creator.create_from_parsed_data(parsed_data)
                        resume_file.created_candidate = candidate
                        resume_file.status = 'converted'
                    else:
                        resume_file.status = 'failed'
                        resume_file.error_message = 'Не удалось обработать данные резюме'
                    
                except ValueError as ve:
                    resume_file.status = 'failed'
                    resume_file.error_message = str(ve)
                    bulk_upload.failed_files += 1
                except Exception as e:
                    resume_file.status = 'failed'
                    resume_file.error_message = f'Ошибка обработки: {str(e)}'
                    bulk_upload.failed_files += 1
                finally:
                    resume_file.save()
                    bulk_upload.processed_files += 1
                    bulk_upload.processing_progress = (bulk_upload.processed_files / total_files) * 100
                    bulk_upload.save()
            
            gc.collect()
        
        bulk_upload.status = 'completed'
        bulk_upload.save()
        
    except Exception as e:
        bulk_upload.status = 'failed'
        bulk_upload.save()
        raise self.retry(exc=e)
    