from celery import shared_task
from .models import BulkUpload, ResumeFile
from .services.parsers import PDFParser, DOCParser, DOCXParser, PPTXParser, TXTParser
from .services.candidate_creator import CandidateCreator

@shared_task
def process_resume_files(bulk_upload_id):
    bulk_upload = BulkUpload.objects.get(id=bulk_upload_id)
    bulk_upload.status = 'processing'
    bulk_upload.save()
    
    parsers = {
        'pdf': PDFParser(),
        'doc': DOCParser(),
        'docx': DOCXParser(),
        'pptx': PPTXParser(),
        'txt': TXTParser(),
    }
    
    candidate_creator = CandidateCreator()
    
    for resume_file in bulk_upload.resume_files.filter(status='pending'):
        try:
            resume_file.status = 'processing'
            resume_file.save()
            
            parser = parsers[resume_file.file_type]
            parsed_data = parser.parse(resume_file.file.path)
            
            resume_file.parsed_data = parsed_data
            resume_file.extracted_text = parsed_data.get('raw_text', '')
            resume_file.extracted_name = parsed_data.get('name', '')
            resume_file.extracted_email = parsed_data.get('email', '')
            resume_file.extracted_phone = parsed_data.get('phone', '')
            resume_file.extracted_experience_years = parsed_data.get('experience_years')
            resume_file.extracted_skills = parsed_data.get('skills', [])
            
            # Create candidate profile
            candidate_creator.create_from_parsed_data(parsed_data)
            
            resume_file.status = 'converted'
            bulk_upload.processed_files += 1
            
        except Exception as e:
            resume_file.status = 'failed'
            resume_file.error_message = str(e)
            bulk_upload.failed_files += 1
            
        finally:
            resume_file.save()
            bulk_upload.save()
    
    bulk_upload.status = 'completed'
    bulk_upload.save() 