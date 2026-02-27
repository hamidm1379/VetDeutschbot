"""
Data models and database operations.
i18n-ready: Uses JSON columns for multilingual content.
"""
import json
from db import db
from typing import Optional, List, Dict, Any
from datetime import datetime
from utils.i18n import get_i18n


class User:
    """User model and operations."""
    
    @staticmethod
    def get_or_create(telegram_id: int) -> Dict[str, Any]:
        """Get user by telegram_id or create if not exists."""
        user = db.execute_query(
            "SELECT * FROM users WHERE telegram_id = %s",
            (telegram_id,),
            fetch_one=True
        )
        
        if not user:
            db.execute_query(
                """INSERT INTO users (telegram_id, name, mobile, language, current_step, created_at)
                   VALUES (%s, NULL, NULL, NULL, 1, %s)""",
                (telegram_id, datetime.now())
            )
            user = db.execute_query(
                "SELECT * FROM users WHERE telegram_id = %s",
                (telegram_id,),
                fetch_one=True
            )
        
        return user
    
    @staticmethod
    def update_language(telegram_id: int, language: str):
        """Update user's language preference."""
        db.execute_query(
            "UPDATE users SET language = %s WHERE telegram_id = %s",
            (language, telegram_id)
        )
    
    @staticmethod
    def update_current_step(telegram_id: int, step_id: int):
        """Update user's current step."""
        db.execute_query(
            "UPDATE users SET current_step = %s WHERE telegram_id = %s",
            (step_id, telegram_id)
        )
    
    @staticmethod
    def get_current_step(telegram_id: int) -> int:
        """Get user's current step."""
        user = db.execute_query(
            "SELECT current_step FROM users WHERE telegram_id = %s",
            (telegram_id,),
            fetch_one=True
        )
        return user['current_step'] if user else 1
    
    @staticmethod
    def update_name(telegram_id: int, name: str):
        """Update user's name."""
        db.execute_query(
            "UPDATE users SET name = %s WHERE telegram_id = %s",
            (name, telegram_id)
        )
    
    @staticmethod
    def update_mobile(telegram_id: int, mobile: str):
        """Update user's mobile number."""
        db.execute_query(
            "UPDATE users SET mobile = %s WHERE telegram_id = %s",
            (mobile, telegram_id)
        )
    
    @staticmethod
    def update_account_expires_at(telegram_id: int, expires_at: datetime):
        """Update user's account expiration date."""
        db.execute_query(
            "UPDATE users SET account_expires_at = %s WHERE telegram_id = %s",
            (expires_at, telegram_id)
        )
    
    @staticmethod
    def get_account_remaining_time(telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user's account remaining time information."""
        user = User.get_or_create(telegram_id)
        expires_at = user.get('account_expires_at')
        
        if expires_at is None:
            return {'unlimited': True}
        
        now = datetime.now()
        
        # Handle string datetime from database
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
            except:
                try:
                    expires_at = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S.%f')
                except:
                    return {'unlimited': True}
        
        if expires_at <= now:
            return {'expired': True}
        
        delta = expires_at - now
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        return {
            'expired': False,
            'unlimited': False,
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'expires_at': expires_at
        }
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all users ordered by created_at."""
        return db.execute_query(
            "SELECT * FROM users ORDER BY created_at DESC",
            fetch_all=True
        )
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by id."""
        return db.execute_query(
            "SELECT * FROM users WHERE id = %s",
            (user_id,),
            fetch_one=True
        )
    
    @staticmethod
    def delete(user_id: int):
        """Delete a user and their history (exam results)."""
        # First, explicitly delete user's exam results (history)
        db.execute_query(
            "DELETE FROM user_exam_results WHERE user_id = %s",
            (user_id,)
        )
        # Then delete the user
        # This will also cascade delete any remaining related data
        db.execute_query(
            "DELETE FROM users WHERE id = %s",
            (user_id,)
        )


class Step:
    """Step model and operations (i18n-ready)."""
    
    @staticmethod
    def _parse_json_field(field, default=None):
        """Parse JSON field from database."""
        if field is None:
            return default or {}
        if isinstance(field, str):
            return json.loads(field)
        return field
    
    @staticmethod
    def get_text_by_language(step: Dict, field: str, language: str) -> str:
        """Get text from JSON field by language with fallback."""
        json_field = step.get(field, {})
        if isinstance(json_field, str):
            json_field = json.loads(json_field)
        
        # Try requested language
        text = json_field.get(language)
        if text:
            return text
        
        # Fallback to default language
        default_lang = get_i18n()._default_language
        text = json_field.get(default_lang)
        if text:
            return text
        
        # Fallback to first available language
        if json_field:
            return list(json_field.values())[0]
        
        return ""
    
    @staticmethod
    def get_all_active() -> List[Dict[str, Any]]:
        """Get all active steps ordered by id."""
        return db.execute_query(
            "SELECT * FROM steps WHERE is_active = 1 ORDER BY id ASC",
            fetch_all=True
        )
    
    @staticmethod
    def get_by_id(step_id: int) -> Optional[Dict[str, Any]]:
        """Get step by id."""
        return db.execute_query(
            "SELECT * FROM steps WHERE id = %s",
            (step_id,),
            fetch_one=True
        )
    
    @staticmethod
    def get_next_step(current_step_id: int) -> Optional[Dict[str, Any]]:
        """Get next active step after current."""
        return db.execute_query(
            """SELECT * FROM steps 
               WHERE id > %s AND is_active = 1 
               ORDER BY id ASC LIMIT 1""",
            (current_step_id,),
            fetch_one=True
        )
    
    @staticmethod
    def get_total_count() -> int:
        """Get total count of active steps."""
        result = db.execute_query(
            "SELECT COUNT(*) as count FROM steps WHERE is_active = 1",
            fetch_one=True
        )
        return result['count'] if result else 0
    
    @staticmethod
    def get_step_position(step_id: int) -> int:
        """Get step's position (1-based) among active steps ordered by id."""
        all_active = Step.get_all_active()
        for index, step in enumerate(all_active, start=1):
            if step['id'] == step_id:
                return index
        return 0  # Step not found or not active
    
    @staticmethod
    def get_first_active() -> Optional[Dict[str, Any]]:
        """Get first active step."""
        return db.execute_query(
            "SELECT * FROM steps WHERE is_active = 1 ORDER BY id ASC LIMIT 1",
            fetch_one=True
        )
    
    @staticmethod
    def create(title_json: Dict[str, str], description_json: Dict[str, str] = None, 
               file_id: str = None) -> int:
        """Create a new step with multilingual content."""
        title_json_str = json.dumps(title_json, ensure_ascii=False)
        description_json_str = json.dumps(description_json or {}, ensure_ascii=False)
        
        return db.execute_query(
            """INSERT INTO steps (title_json, description_json, file_id, is_active)
               VALUES (%s, %s, %s, 1)""",
            (title_json_str, description_json_str, file_id)
        )
    
    @staticmethod
    def update(step_id: int, title_json: Dict[str, str] = None,
               description_json: Dict[str, str] = None, file_id: str = None):
        """Update a step with multilingual content."""
        updates = []
        params = []
        
        if title_json is not None:
            updates.append("title_json = %s")
            params.append(json.dumps(title_json, ensure_ascii=False))
        
        if description_json is not None:
            updates.append("description_json = %s")
            params.append(json.dumps(description_json, ensure_ascii=False))
        
        if file_id is not None:
            updates.append("file_id = %s")
            params.append(file_id)
        
        if updates:
            params.append(step_id)
            query = f"UPDATE steps SET {', '.join(updates)} WHERE id = %s"
            db.execute_query(query, tuple(params))
    
    @staticmethod
    def delete(step_id: int):
        """Delete a step (soft delete by setting is_active = 0)."""
        db.execute_query(
            "UPDATE steps SET is_active = 0 WHERE id = %s",
            (step_id,)
        )
    
    @staticmethod
    def toggle_active(step_id: int):
        """Toggle step active status."""
        db.execute_query(
            "UPDATE steps SET is_active = NOT is_active WHERE id = %s",
            (step_id,)
        )
    
    @staticmethod
    def get_user_count(step_id: int) -> int:
        """Get number of users who reached this step."""
        result = db.execute_query(
            "SELECT COUNT(*) as count FROM users WHERE current_step >= %s",
            (step_id,),
            fetch_one=True
        )
        return result['count'] if result else 0


class Exam:
    """Exam model and operations."""
    
    @staticmethod
    def get_by_step_id(step_id: int) -> Optional[Dict[str, Any]]:
        """Get exam for a step."""
        return db.execute_query(
            "SELECT * FROM exams WHERE step_id = %s",
            (step_id,),
            fetch_one=True
        )
    
    @staticmethod
    def create(step_id: int) -> int:
        """Create exam for a step."""
        # Check if exam already exists
        existing = Exam.get_by_step_id(step_id)
        if existing:
            return existing['id']
        
        return db.execute_query(
            "INSERT INTO exams (step_id) VALUES (%s)",
            (step_id,)
        )
    
    @staticmethod
    def delete(exam_id: int):
        """Delete an exam and its questions."""
        # Delete questions first
        db.execute_query(
            "DELETE FROM questions WHERE exam_id = %s",
            (exam_id,)
        )
        # Delete exam
        db.execute_query(
            "DELETE FROM exams WHERE id = %s",
            (exam_id,)
        )


class Question:
    """Question model and operations (i18n-ready)."""
    
    @staticmethod
    def get_text_by_language(question: Dict, language: str) -> str:
        """Get question text from JSON field by language with fallback."""
        question_json = question.get('question_json', {})
        if isinstance(question_json, str):
            question_json = json.loads(question_json)
        
        # Try requested language
        text = question_json.get(language)
        if text:
            return text
        
        # Fallback to default language
        default_lang = get_i18n()._default_language
        text = question_json.get(default_lang)
        if text:
            return text
        
        # Fallback to first available language
        if question_json:
            return list(question_json.values())[0]
        
        return ""
    
    @staticmethod
    def get_by_exam_id(exam_id: int) -> List[Dict[str, Any]]:
        """Get all questions for an exam."""
        return db.execute_query(
            "SELECT * FROM questions WHERE exam_id = %s ORDER BY id ASC",
            (exam_id,),
            fetch_all=True
        )
    
    @staticmethod
    def create(exam_id: int, question_json: Dict[str, str], 
               options_json: str, correct_option: int) -> int:
        """Create a question with multilingual content."""
        question_json_str = json.dumps(question_json, ensure_ascii=False)
        return db.execute_query(
            """INSERT INTO questions (exam_id, question_json, 
               options_json, correct_option)
               VALUES (%s, %s, %s, %s)""",
            (exam_id, question_json_str, options_json, correct_option)
        )
    
    @staticmethod
    def update(question_id: int, question_json: Dict[str, str] = None,
               options_json: str = None, correct_option: int = None):
        """Update a question with multilingual content."""
        updates = []
        params = []
        
        if question_json is not None:
            updates.append("question_json = %s")
            params.append(json.dumps(question_json, ensure_ascii=False))
        
        if options_json is not None:
            updates.append("options_json = %s")
            params.append(options_json)
        
        if correct_option is not None:
            updates.append("correct_option = %s")
            params.append(correct_option)
        
        if updates:
            params.append(question_id)
            query = f"UPDATE questions SET {', '.join(updates)} WHERE id = %s"
            db.execute_query(query, tuple(params))
    
    @staticmethod
    def delete(question_id: int):
        """Delete a question."""
        db.execute_query(
            "DELETE FROM questions WHERE id = %s",
            (question_id,)
        )
    
    @staticmethod
    def get_by_id(question_id: int) -> Optional[Dict[str, Any]]:
        """Get question by id."""
        return db.execute_query(
            "SELECT * FROM questions WHERE id = %s",
            (question_id,),
            fetch_one=True
        )


class UserExamResult:
    """User exam result model and operations."""
    
    @staticmethod
    def get_user_result(telegram_id: int, step_id: int) -> Optional[Dict[str, Any]]:
        """Get user's exam result for a step."""
        user = User.get_or_create(telegram_id)
        return db.execute_query(
            """SELECT * FROM user_exam_results 
               WHERE user_id = %s AND step_id = %s""",
            (user['id'], step_id),
            fetch_one=True
        )
    
    @staticmethod
    def save_result(telegram_id: int, step_id: int, score: float, passed: bool):
        """Save or update user's exam result."""
        user = User.get_or_create(telegram_id)
        
        # Check if result exists
        existing = UserExamResult.get_user_result(telegram_id, step_id)
        
        if existing:
            db.execute_query(
                """UPDATE user_exam_results 
                   SET score = %s, passed = %s
                   WHERE user_id = %s AND step_id = %s""",
                (score, passed, user['id'], step_id)
            )
        else:
            db.execute_query(
                """INSERT INTO user_exam_results (user_id, step_id, score, passed)
                   VALUES (%s, %s, %s, %s)""",
                (user['id'], step_id, score, passed)
            )
    
    @staticmethod
    def has_passed(telegram_id: int, step_id: int) -> bool:
        """Check if user has passed the exam for a step."""
        result = UserExamResult.get_user_result(telegram_id, step_id)
        return result['passed'] if result else False


class Section:
    """Section model and operations (i18n-ready)."""
    
    @staticmethod
    def get_text_by_language(section: Dict, field: str, language: str) -> str:
        """Get text from JSON field by language with fallback."""
        json_field = section.get(field, {})
        if isinstance(json_field, str):
            json_field = json.loads(json_field)
        
        # Try requested language
        text = json_field.get(language)
        if text:
            return text
        
        # Fallback to default language
        default_lang = get_i18n()._default_language
        text = json_field.get(default_lang)
        if text:
            return text
        
        # Fallback to first available language
        if json_field:
            return list(json_field.values())[0]
        
        return ""
    
    @staticmethod
    def get_all_active() -> List[Dict[str, Any]]:
        """Get all active sections ordered by order_number."""
        return db.execute_query(
            "SELECT * FROM sections WHERE is_active = 1 ORDER BY order_number ASC",
            fetch_all=True
        )
    
    @staticmethod
    def get_by_id(section_id: int) -> Optional[Dict[str, Any]]:
        """Get section by id."""
        return db.execute_query(
            "SELECT * FROM sections WHERE id = %s",
            (section_id,),
            fetch_one=True
        )
    
    @staticmethod
    def create(title_json: Dict[str, str], description_json: Dict[str, str] = None,
               order_number: int = None) -> int:
        """Create a new section with multilingual content."""
        if order_number is None:
            # Get max order_number and add 1
            max_order = db.execute_query(
                "SELECT COALESCE(MAX(order_number), 0) as max_order FROM sections",
                fetch_one=True
            )
            order_number = (max_order['max_order'] if max_order else 0) + 1
        
        title_json_str = json.dumps(title_json, ensure_ascii=False)
        description_json_str = json.dumps(description_json or {}, ensure_ascii=False)
        
        return db.execute_query(
            """INSERT INTO sections (title_json, description_json, order_number, is_active)
               VALUES (%s, %s, %s, 1)""",
            (title_json_str, description_json_str, order_number)
        )
    
    @staticmethod
    def update(section_id: int, title_json: Dict[str, str] = None,
               description_json: Dict[str, str] = None, order_number: int = None):
        """Update a section with multilingual content."""
        updates = []
        params = []
        
        if title_json is not None:
            updates.append("title_json = %s")
            params.append(json.dumps(title_json, ensure_ascii=False))
        
        if description_json is not None:
            updates.append("description_json = %s")
            params.append(json.dumps(description_json, ensure_ascii=False))
        
        if order_number is not None:
            updates.append("order_number = %s")
            params.append(order_number)
        
        if updates:
            params.append(section_id)
            query = f"UPDATE sections SET {', '.join(updates)} WHERE id = %s"
            db.execute_query(query, tuple(params))
    
    @staticmethod
    def delete(section_id: int):
        """Delete a section (soft delete by setting is_active = 0)."""
        db.execute_query(
            "UPDATE sections SET is_active = 0 WHERE id = %s",
            (section_id,)
        )


class Lesson:
    """Lesson model and operations."""
    
    @staticmethod
    def get_by_section_id(section_id: int) -> List[Dict[str, Any]]:
        """Get all lessons for a section ordered by order_number."""
        return db.execute_query(
            """SELECT l.*, s.title_json as step_title_json, s.description_json as step_description_json,
                      s.file_id as step_file_id
               FROM lessons l
               JOIN steps s ON l.step_id = s.id
               WHERE l.section_id = %s AND l.is_active = 1 AND s.is_active = 1
               ORDER BY l.order_number ASC""",
            (section_id,),
            fetch_all=True
        )
    
    @staticmethod
    def get_by_id(lesson_id: int) -> Optional[Dict[str, Any]]:
        """Get lesson by id."""
        return db.execute_query(
            """SELECT l.*, s.title_json as step_title_json, s.description_json as step_description_json,
                      s.file_id as step_file_id
               FROM lessons l
               JOIN steps s ON l.step_id = s.id
               WHERE l.id = %s""",
            (lesson_id,),
            fetch_one=True
        )
    
    @staticmethod
    def create(section_id: int, step_id: int, order_number: int = None) -> int:
        """Create a new lesson."""
        if order_number is None:
            # Get max order_number for this section and add 1
            max_order = db.execute_query(
                "SELECT COALESCE(MAX(order_number), 0) as max_order FROM lessons WHERE section_id = %s",
                (section_id,),
                fetch_one=True
            )
            order_number = (max_order['max_order'] if max_order else 0) + 1
        
        return db.execute_query(
            """INSERT INTO lessons (section_id, step_id, order_number, is_active)
               VALUES (%s, %s, %s, 1)""",
            (section_id, step_id, order_number)
        )
    
    @staticmethod
    def delete(lesson_id: int):
        """Delete a lesson (soft delete by setting is_active = 0)."""
        db.execute_query(
            "UPDATE lessons SET is_active = 0 WHERE id = %s",
            (lesson_id,)
        )


class UserSectionProgress:
    """User section progress model and operations."""
    
    @staticmethod
    def is_unlocked(telegram_id: int, section_id: int) -> bool:
        """Check if a section is unlocked for user."""
        user = User.get_or_create(telegram_id)
        result = db.execute_query(
            """SELECT unlocked FROM user_section_progress 
               WHERE user_id = %s AND section_id = %s""",
            (user['id'], section_id),
            fetch_one=True
        )
        return result['unlocked'] if result else False
    
    @staticmethod
    def unlock(telegram_id: int, section_id: int):
        """Unlock a section for user."""
        user = User.get_or_create(telegram_id)
        from datetime import datetime
        
        # Check if exists
        existing = db.execute_query(
            "SELECT id FROM user_section_progress WHERE user_id = %s AND section_id = %s",
            (user['id'], section_id),
            fetch_one=True
        )
        
        if existing:
            db.execute_query(
                """UPDATE user_section_progress 
                   SET unlocked = TRUE, unlocked_at = %s
                   WHERE user_id = %s AND section_id = %s""",
                (datetime.now(), user['id'], section_id)
            )
        else:
            db.execute_query(
                """INSERT INTO user_section_progress (user_id, section_id, unlocked, unlocked_at)
                   VALUES (%s, %s, TRUE, %s)""",
                (user['id'], section_id, datetime.now())
            )
    
    @staticmethod
    def get_unlocked_sections(telegram_id: int) -> List[int]:
        """Get list of unlocked section IDs for user."""
        user = User.get_or_create(telegram_id)
        results = db.execute_query(
            """SELECT section_id FROM user_section_progress 
               WHERE user_id = %s AND unlocked = TRUE""",
            (user['id'],),
            fetch_all=True
        )
        return [r['section_id'] for r in results] if results else []


class UserLessonProgress:
    """User lesson progress model and operations."""
    
    @staticmethod
    def is_unlocked(telegram_id: int, lesson_id: int) -> bool:
        """Check if a lesson is unlocked for user."""
        user = User.get_or_create(telegram_id)
        result = db.execute_query(
            """SELECT unlocked FROM user_lesson_progress 
               WHERE user_id = %s AND lesson_id = %s""",
            (user['id'], lesson_id),
            fetch_one=True
        )
        return result['unlocked'] if result else False
    
    @staticmethod
    def unlock(telegram_id: int, lesson_id: int):
        """Unlock a lesson for user."""
        user = User.get_or_create(telegram_id)
        from datetime import datetime
        
        # Check if exists
        existing = db.execute_query(
            "SELECT id FROM user_lesson_progress WHERE user_id = %s AND lesson_id = %s",
            (user['id'], lesson_id),
            fetch_one=True
        )
        
        if existing:
            db.execute_query(
                """UPDATE user_lesson_progress 
                   SET unlocked = TRUE, unlocked_at = %s
                   WHERE user_id = %s AND lesson_id = %s""",
                (datetime.now(), user['id'], lesson_id)
            )
        else:
            db.execute_query(
                """INSERT INTO user_lesson_progress (user_id, lesson_id, unlocked, unlocked_at)
                   VALUES (%s, %s, TRUE, %s)""",
                (user['id'], lesson_id, datetime.now())
            )
    
    @staticmethod
    def get_unlocked_lessons(telegram_id: int, section_id: int) -> List[int]:
        """Get list of unlocked lesson IDs for user in a section."""
        user = User.get_or_create(telegram_id)
        results = db.execute_query(
            """SELECT ulp.lesson_id FROM user_lesson_progress ulp
               JOIN lessons l ON ulp.lesson_id = l.id
               WHERE ulp.user_id = %s AND l.section_id = %s AND ulp.unlocked = TRUE""",
            (user['id'], section_id),
            fetch_all=True
        )
        return [r['lesson_id'] for r in results] if results else []
