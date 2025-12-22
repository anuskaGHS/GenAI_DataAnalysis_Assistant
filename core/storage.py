import os
import sqlite3
import pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename
import config

class Storage:
    """Handles file uploads and database operations"""
    
    def __init__(self):
        """Initialize storage and ensure folders/database exist"""
        # Create upload folder if it doesn't exist
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
        
        # Create database if it doesn't exist
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'uploaded'
            )
        ''')
        
        # Create analysis_results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                result_type TEXT NOT NULL,
                result_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS
    
    def save_upload(self, file, session_id):
        """Save uploaded file and register in database"""
        if file and self.allowed_file(file.filename):
            # Secure the filename
            filename = secure_filename(file.filename)
            
            # Create unique filename with session_id
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{session_id}_{timestamp}_{filename}"
            filepath = os.path.join(config.UPLOAD_FOLDER, unique_filename)
            
            # Save file
            file.save(filepath)
            
            # Register in database
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (session_id, filename, filepath, status)
                VALUES (?, ?, ?, 'uploaded')
            ''', (session_id, filename, filepath))
            conn.commit()
            conn.close()
            
            return filepath, filename
        
        return None, None
    
    def get_session(self, session_id):
        """Get session information from database"""
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT session_id, filename, filepath, uploaded_at, status
            FROM sessions
            WHERE session_id = ?
        ''', (session_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'session_id': result[0],
                'filename': result[1],
                'filepath': result[2],
                'uploaded_at': result[3],
                'status': result[4]
            }
        return None
    
    def update_session_status(self, session_id, status):
        """Update session status (uploaded, analyzing, completed, error)"""
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE sessions
            SET status = ?
            WHERE session_id = ?
        ''', (status, session_id))
        conn.commit()
        conn.close()
    
    def save_analysis_result(self, session_id, result_type, result_data):
        """Save analysis result to database"""
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analysis_results (session_id, result_type, result_data)
            VALUES (?, ?, ?)
        ''', (session_id, result_type, str(result_data)))
        conn.commit()
        conn.close()
    
    def get_analysis_result(self, session_id, result_type):
        """Get specific analysis result from database"""
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT result_data
            FROM analysis_results
            WHERE session_id = ? AND result_type = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (session_id, result_type))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def load_dataframe(self, filepath):
        """Load CSV or Excel file into pandas DataFrame"""
        try:
            # Get file extension
            file_ext = filepath.rsplit('.', 1)[1].lower()
            
            # Load based on extension
            if file_ext == 'csv':
                df = pd.read_csv(filepath)
            elif file_ext in ['xlsx', 'xls']:
                df = pd.read_excel(filepath)
            else:
                return None
            
            return df
        except Exception as e:
            print(f"Error loading file: {e}")
            return None
    
    def save_dataframe(self, df, session_id, suffix='cleaned'):
        """Save DataFrame to storage folder"""
        try:
            # Create filename
            filename = f"{session_id}_{suffix}.csv"
            filepath = os.path.join(config.UPLOAD_FOLDER, filename)
            
            # Save as CSV
            df.to_csv(filepath, index=False)
            
            return filepath
        except Exception as e:
            print(f"Error saving dataframe: {e}")
            return None