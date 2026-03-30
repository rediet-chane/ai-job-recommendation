import io
import PyPDF2
import docx

class CVParser:
    @staticmethod
    def extract_text_from_pdf(file_bytes):
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except:
            return ""
    
    @staticmethod
    def extract_text_from_docx(file_bytes):
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join([p.text for p in doc.paragraphs])
        except:
            return ""
    
    @staticmethod
    def extract_text_from_txt(file_bytes):
        try:
            return file_bytes.decode('utf-8', errors='ignore')
        except:
            return ""
    
    @staticmethod
    def analyze_cv(text):
        """Analyze CV and return insights"""
        words = text.split()
        sentences = text.split('.')
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'has_contact': bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)),
            'has_education': bool(re.search(r'education|university|college|degree|bachelor|master', text.lower())),
            'has_experience': bool(re.search(r'experience|worked|position|job|intern', text.lower())),
            'has_skills': bool(re.search(r'skills|technologies|tools|proficient', text.lower()))
        }