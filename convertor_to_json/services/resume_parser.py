from .nlp_processor import NLPProcessor
import logging

logger = logging.getLogger(__name__)

class ResumeParser:
    def __init__(self):
        self.nlp_processor = NLPProcessor()
        
    def parse(self, text):
        try:
            processed_data = self.nlp_processor.process_resume(text)
            
            if not processed_data:
                return self._get_empty_result()
                
            return {
                'raw_text': text[:1000],
                'name': processed_data.get('name', '')[:100],
                'email': processed_data.get('email', '')[:100],
                'phone': processed_data.get('phone', '')[:20],
                'experience_years': processed_data.get('experience_years', 0),
                'specialization': processed_data.get('specialization', '')[:99],
                'tech_stack': processed_data.get('tech_stack', [])[:10],
                'hard_skills': processed_data.get('hard_skills', [])[:10],
                'soft_skills': processed_data.get('soft_skills', [])[:10],
                'education': processed_data.get('education', {}),
                'work_experience': processed_data.get('work_experience', [])[:5],
                'languages': processed_data.get('languages', ['Русский'])[:5],
                'desired_salary': processed_data.get('desired_salary', 0),
                'location': processed_data.get('location', {'country': 'Казахстан'}),
                'certifications': []
            }
            
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            return self._get_empty_result()
            
    def _get_empty_result(self):
        return {
            'raw_text': '',
            'name': '',
            'email': '',
            'phone': '',
            'experience_years': 0,
            'specialization': '',
            'tech_stack': [],
            'hard_skills': [],
            'soft_skills': [],
            'education': {},
            'work_experience': [],
            'languages': ['Русский'],
            'desired_salary': 0,
            'location': {'country': ''},
            'certifications': []
        }