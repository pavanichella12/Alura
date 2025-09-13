import sqlite3
import json
import threading
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

class ContentModerationDB:
    def __init__(self, db_path: str = "data/database/content_moderation.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with proper cleanup"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")  # Use WAL mode for better concurrency
            conn.execute("PRAGMA synchronous=NORMAL")  # Faster writes
            conn.execute("PRAGMA cache_size=10000")  # Larger cache
            conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables
            yield conn
        except Exception as e:
            print(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    print(f"Error closing connection: {e}")
    
    def init_database(self):
        """Initialize the database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create all messages table (stores every message)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS all_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    is_flagged BOOLEAN DEFAULT FALSE,
                    flagged_message_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (flagged_message_id) REFERENCES flagged_messages (id)
                )
            ''')
            
            # Create flagged messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS flagged_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    flagged_words TEXT NOT NULL,
                    categories TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    alternatives TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_challenged BOOLEAN DEFAULT FALSE,
                    challenge_status TEXT DEFAULT 'pending'
                )
            ''')
            
            # Create user violations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    violation_count INTEGER DEFAULT 0,
                    last_violation DATETIME,
                    is_banned BOOLEAN DEFAULT FALSE,
                    training_completed BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Create challenge requests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS challenge_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    flagged_message_id INTEGER,
                    user_id TEXT NOT NULL,
                    challenge_reason TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    reviewer_notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at DATETIME,
                    FOREIGN KEY (flagged_message_id) REFERENCES flagged_messages (id)
                )
            ''')
            
            conn.commit()
    
    def store_message(self, user_id: str, message: str, is_flagged: bool = False, flagged_message_id: int = None) -> int:
        """Store any message (flagged or unflagged) in the database"""
        with self._lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                try:
                    cursor.execute('''
                        INSERT INTO all_messages (user_id, message, is_flagged, flagged_message_id)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, message, is_flagged, flagged_message_id))
                    
                    message_id = cursor.lastrowid
                    conn.commit()
                    return message_id
                except Exception as e:
                    print(f"Database error in store_message: {e}")
                    conn.rollback()
                    return 0
    
    def store_flagged_message(self, user_id: str, message: str, flagged_words: List[str], 
                            categories: List[str], confidence: float, alternatives: List[str]) -> int:
        """Store a flagged message in the database"""
        with self._lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                try:
                    # Store in flagged_messages table
                    cursor.execute('''
                        INSERT INTO flagged_messages (user_id, message, flagged_words, categories, confidence, alternatives)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_id, message, json.dumps(flagged_words), json.dumps(categories), confidence, json.dumps(alternatives)))
                    
                    flagged_message_id = cursor.lastrowid
                    
                    # Also store in all_messages table
                    cursor.execute('''
                        INSERT INTO all_messages (user_id, message, is_flagged, flagged_message_id)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, message, True, flagged_message_id))
                    
                    conn.commit()
                    
                    # Update user violation count
                    self.update_user_violation(user_id)
                    
                    return flagged_message_id
                except Exception as e:
                    print(f"Database error in store_flagged_message: {e}")
                    conn.rollback()
                    return 0
    
    def store_clean_message(self, user_id: str, message: str) -> int:
        """Store a message that was not flagged"""
        return self.store_message(user_id, message, is_flagged=False)
    
    def get_all_messages(self, user_id: str = None, limit: int = 100) -> List[Dict]:
        """Get all messages (flagged and unflagged)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT id, user_id, message, is_flagged, flagged_message_id, timestamp
                    FROM all_messages 
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT id, user_id, message, is_flagged, flagged_message_id, timestamp
                    FROM all_messages 
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
            
            results = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'user_id': row[1],
                    'message': row[2],
                    'is_flagged': bool(row[3]),
                    'flagged_message_id': row[4],
                    'timestamp': row[5]
                }
                for row in results
            ]
    
    def get_message_stats(self, user_id: str = None) -> Dict:
        """Get statistics about messages"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_messages,
                        SUM(CASE WHEN is_flagged THEN 1 ELSE 0 END) as flagged_messages,
                        SUM(CASE WHEN NOT is_flagged THEN 1 ELSE 0 END) as clean_messages
                    FROM all_messages 
                    WHERE user_id = ?
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_messages,
                        SUM(CASE WHEN is_flagged THEN 1 ELSE 0 END) as flagged_messages,
                        SUM(CASE WHEN NOT is_flagged THEN 1 ELSE 0 END) as clean_messages
                    FROM all_messages
                ''')
            
            result = cursor.fetchone()
            return {
                'total_messages': result[0],
                'flagged_messages': result[1] or 0,
                'clean_messages': result[2] or 0,
                'flag_rate': (result[1] or 0) / result[0] if result[0] > 0 else 0
            }
    
    def update_user_violation(self, user_id: str):
        """Update user violation count"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute('SELECT violation_count FROM user_violations WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if result:
                new_count = result[0] + 1
                cursor.execute('''
                    UPDATE user_violations 
                    SET violation_count = ?, last_violation = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (new_count, user_id))
            else:
                cursor.execute('''
                    INSERT INTO user_violations (user_id, violation_count, last_violation)
                    VALUES (?, 1, CURRENT_TIMESTAMP)
                ''', (user_id,))
            
            conn.commit()
    
    def get_user_violations(self, user_id: str) -> Dict:
        """Get user violation information"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT violation_count, is_banned, training_completed, last_violation
                FROM user_violations WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            
            if result is None:
                # User doesn't exist yet, return default values
                return {
                    'violation_count': 0,
                    'is_banned': False,
                    'training_completed': False,
                    'last_violation': None
                }
            
            return {
                'violation_count': result[0],
                'is_banned': bool(result[1]),
                'training_completed': bool(result[2]),
                'last_violation': result[3]
            }
    
    def create_challenge_request(self, flagged_message_id: int, user_id: str, challenge_reason: str) -> int:
        """Create a challenge request for a flagged message"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO challenge_requests (flagged_message_id, user_id, challenge_reason)
                VALUES (?, ?, ?)
            ''', (flagged_message_id, user_id, challenge_reason))
            
            challenge_id = cursor.lastrowid
            
            # Update flagged message as challenged
            cursor.execute('''
                UPDATE flagged_messages 
                SET is_challenged = TRUE 
                WHERE id = ?
            ''', (flagged_message_id,))
            
            conn.commit()
            return challenge_id
    
    def get_pending_challenges(self) -> List[Dict]:
        """Get all pending challenge requests"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT cr.id, cr.user_id, cr.challenge_reason, cr.created_at,
                       fm.message, fm.flagged_words, fm.categories
                FROM challenge_requests cr
                JOIN flagged_messages fm ON cr.flagged_message_id = fm.id
                WHERE cr.status = 'pending'
                ORDER BY cr.created_at DESC
            ''')
            
            results = cursor.fetchall()
            return [
                {
                    'challenge_id': row[0],
                    'user_id': row[1],
                    'challenge_reason': row[2],
                    'created_at': row[3],
                    'original_message': row[4],
                    'flagged_words': json.loads(row[5]),
                    'categories': json.loads(row[6])
                }
                for row in results
            ]
    
    def update_challenge_status(self, challenge_id: int, status: str, reviewer_notes: str = None):
        """Update challenge request status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE challenge_requests 
                SET status = ?, reviewer_notes = ?, reviewed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, reviewer_notes, challenge_id))
            
            conn.commit()
    
    def approve_challenge(self, challenge_id: int, reviewer_notes: str = None):
        """Approve a challenge - unflag the message and deliver it"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get the challenge details
            cursor.execute('''
                SELECT flagged_message_id, user_id
                FROM challenge_requests 
                WHERE id = ?
            ''', (challenge_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            flagged_message_id, user_id = result
            
            # Get the original flagged message
            cursor.execute('''
                SELECT message FROM flagged_messages WHERE id = ?
            ''', (flagged_message_id,))
            
            message_result = cursor.fetchone()
            if not message_result:
                return False
            
            original_message = message_result[0]
            
            # Update challenge status to approved
            cursor.execute('''
                UPDATE challenge_requests 
                SET status = 'approved', reviewer_notes = ?, reviewed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (reviewer_notes, challenge_id))
            
            # Mark the flagged message as approved (unflagged)
            cursor.execute('''
                UPDATE flagged_messages 
                SET challenge_status = 'approved'
                WHERE id = ?
            ''', (flagged_message_id,))
            
            # Update all_messages to mark as unflagged
            cursor.execute('''
                UPDATE all_messages 
                SET is_flagged = FALSE
                WHERE flagged_message_id = ?
            ''', (flagged_message_id,))
            
            # Reduce user violation count since it was approved
            cursor.execute('''
                UPDATE user_violations 
                SET violation_count = CASE 
                    WHEN violation_count > 0 THEN violation_count - 1 
                    ELSE 0 
                END
                WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
            return True
    
    def reject_challenge(self, challenge_id: int, reviewer_notes: str = None):
        """Reject a challenge - keep message flagged and blocked"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get the flagged message ID
            cursor.execute('''
                SELECT flagged_message_id FROM challenge_requests WHERE id = ?
            ''', (challenge_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            flagged_message_id = result[0]
            
            # Update challenge status to rejected
            cursor.execute('''
                UPDATE challenge_requests 
                SET status = 'rejected', reviewer_notes = ?, reviewed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (reviewer_notes, challenge_id))
            
            # Mark the flagged message as rejected (stays flagged)
            cursor.execute('''
                UPDATE flagged_messages 
                SET challenge_status = 'rejected'
                WHERE id = ?
            ''', (flagged_message_id,))
            
            conn.commit()
            return True
    
    def get_approved_messages(self, user_id: str) -> List[Dict]:
        """Get messages that were approved by reviewer (should be delivered)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT am.message, am.timestamp, cr.reviewer_notes
                FROM all_messages am
                JOIN flagged_messages fm ON am.flagged_message_id = fm.id
                JOIN challenge_requests cr ON fm.id = cr.flagged_message_id
                WHERE am.user_id = ? AND cr.status = 'approved'
                ORDER BY am.timestamp DESC
            ''', (user_id,))
            
            results = cursor.fetchall()
            return [
                {
                    'message': row[0],
                    'timestamp': row[1],
                    'reviewer_notes': row[2]
                }
                for row in results
            ]
    
    def mark_training_completed(self, user_id: str):
        """Mark user training as completed"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_violations 
                SET training_completed = TRUE 
                WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
    
    def clear_all_data(self):
        """Clear all data for testing purposes"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM all_messages')
            cursor.execute('DELETE FROM flagged_messages')
            cursor.execute('DELETE FROM user_violations')
            cursor.execute('DELETE FROM challenge_requests')
            conn.commit()
            print("✅ All data cleared for fresh testing") 