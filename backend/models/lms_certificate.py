"""LMS Certificate Model"""
from typing import Optional, Dict, Any, List
import uuid
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS lms_certificates (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
    certificate_number VARCHAR(100) UNIQUE,
    title VARCHAR(255) NOT NULL,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_date TIMESTAMP,
    pdf_url VARCHAR(500),
    UNIQUE(user_id, course_id)
)
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_lms_certificates_user ON lms_certificates(user_id)'
]


class LMSCertificate(BaseModel):
    """LMS Certificate model"""
    table_name = 'lms_certificates'
    
    def get_user_certificates(self, user_id: str) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            '''SELECT cert.*, c.title as course_title, c.icon FROM lms_certificates cert
               JOIN lms_courses c ON cert.course_id = c.id
               WHERE cert.user_id = %s ORDER BY cert.issued_at DESC''',
            (user_id,)
        )
    
    def issue(self, user_id: str, course_id: int, title: str, **kwargs) -> Optional[Dict[str, Any]]:
        cert_number = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        return self.db.execute_returning(
            '''INSERT INTO lms_certificates (user_id, course_id, certificate_number, title, pdf_url, expiry_date)
               VALUES (%s, %s, %s, %s, %s, %s)
               ON CONFLICT (user_id, course_id) DO NOTHING
               RETURNING *''',
            (user_id, course_id, cert_number, title, kwargs.get('pdf_url'), kwargs.get('expiry_date'))
        )
    
    def find_by_number(self, cert_number: str) -> Optional[Dict[str, Any]]:
        return self.db.fetch_one(
            'SELECT * FROM lms_certificates WHERE certificate_number = %s',
            (cert_number,)
        )

