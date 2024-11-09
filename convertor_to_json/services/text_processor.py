import logging
import os
from typing import Optional
import chardet
import docx2txt
import re

from pdf2image import convert_from_path
import pdfplumber

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
        self.supported_formats = {
            'pdf': self._process_pdf,
            'docx': self._process_docx,
            'doc': self._process_doc,
            'txt': self._process_txt
        }
        self._init_pdf_processors()

    def _init_pdf_processors(self):
        """Инициализация доступных процессоров PDF"""
        self.pdf_processors = []
        
        # PyPDF2 процессор (базовый)
        try:
            import PyPDF2
            self.pdf_processors.append(self._extract_pdf_text_pypdf2)
        except ImportError:
            logger.warning("PyPDF2 not installed")

        # pdfplumber процессор (улучшенный)
        try:
            import pdfplumber
            self.pdf_processors.append(self._extract_pdf_text_pdfplumber)
        except ImportError:
            logger.warning("pdfplumber not installed")

        # Tesseract OCR процессор (если доступен)
        try:
            import pytesseract
            from pdf2image import convert_from_path
            pytesseract.get_tesseract_version()
            self.pdf_processors.append(self._extract_pdf_text_tesseract)
        except Exception:
            logger.warning("Tesseract OCR not available")

        if not self.pdf_processors:
            logger.warning("No PDF processors available. PDF processing will be limited")
            self.pdf_processors.append(self._extract_pdf_text_fallback)

    def _extract_pdf_text_pypdf2(self, file_path: str) -> str:
        import PyPDF2
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfFileReader(file)
            text = ""
            for page_num in range(reader.getNumPages()):
                page = reader.getPage(page_num)
                text += page.extract_text()
            return text

    def _extract_pdf_text_pdfplumber(self, file_path: str) -> str:
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages)

    def _process_pdf(self, file_path: str) -> str:
        text = ""
        errors = []
        
        for processor in self.pdf_processors:
            try:
                text = processor(file_path)
                if text.strip():
                    return text
            except Exception as e:
                errors.append(str(e))
                continue

        if not text.strip():
            error_msg = f"Failed to extract text from PDF using available processors. Errors: {'; '.join(errors)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        return text

    def _process_docx(self, file_path):
        return docx2txt.process(file_path)

    def _process_doc(self, file_path):
        # Используем antiword или другой конвертер для старых doc файлов
        try:
            import antiword
            return antiword.extract_text(file_path)
        except:
            logger.warning("Antiword not installed, falling back to basic extraction")
            return self._process_docx(file_path)

    def _process_txt(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _clean_text(self, text):
        # Очистка текста от специальных символов и лишних пробелов
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s@.,()-]+', ' ', text)
        return text.strip()

    def extract_text(self, file_path: str, file_type: str) -> str:
        """
        Извлекает текст из файла в зависимости от его типа
        """
        try:
            processor = self.supported_formats.get(file_type.lower())
            if not processor:
                logger.error(f"Unsupported file type: {file_type}")
                raise ValueError(f"Unsupported file type: {file_type}")
                
            text = processor(file_path)
            if not text:
                logger.warning(f"No text extracted from {file_path}")
                return ""
                
            # Очищаем извлеченный текст
            cleaned_text = self._clean_text(text)
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise