"""
Progress tracking utilities.
Calculates user progress based on completed exams.
"""
from typing import Dict, Tuple
from models import User, Step, UserExamResult, Section, Lesson


def calculate_progress(telegram_id: int) -> Dict[str, any]:
    """
    Calculate user progress based on completed sections (stages).
    A section is considered completed when all lessons in that section have passed exams.
    
    Args:
        telegram_id: User's Telegram ID
    
    Returns:
        Dictionary with:
        - percentage: Progress percentage (0-100)
        - completed: Number of completed sections (stages)
        - total: Total active sections (stages)
        - current_step_id: Current step ID
        - current_step_name: Current step name (in user's language)
    """
    # Try to use sections/lessons system first
    try:
        all_sections = Section.get_all_active()
        total_sections = len(all_sections)
        
        if total_sections == 0:
            # Fallback to old step-based system if no sections exist
            return _calculate_progress_steps(telegram_id)
        
        # Count completed sections (sections where all lessons have passed exams)
        completed_count = 0
        for section in all_sections:
            lessons = Lesson.get_by_section_id(section['id'])
            
            # Skip sections with no lessons
            if not lessons:
                continue
            
            # Check if all lessons in this section are completed
            all_lessons_completed = True
            for lesson in lessons:
                step_id = lesson['step_id']
                # Check if user has passed the exam for this lesson's step
                if not UserExamResult.has_passed(telegram_id, step_id):
                    all_lessons_completed = False
                    break
            
            if all_lessons_completed:
                completed_count += 1
        
        # Calculate percentage
        percentage = round((completed_count / total_sections) * 100) if total_sections > 0 else 0
        
        # Get current step info
        user = User.get_or_create(telegram_id)
        current_step_id = user.get('current_step', 1)
        current_step = Step.get_by_id(current_step_id)
        
        # Get current step name in user's language
        current_step_name = ""
        current_step_number = 0
        if current_step:
            user_language = user.get('language', 'en') or 'en'
            current_step_name = Step.get_text_by_language(current_step, 'title_json', user_language)
            # Get step position (1-based) among active steps
            current_step_number = Step.get_step_position(current_step_id)
        
        return {
            'percentage': percentage,
            'completed': completed_count,
            'total': total_sections,
            'current_step_id': current_step_id,
            'current_step_name': current_step_name,
            'current_step_number': current_step_number
        }
    except Exception:
        # Fallback to old step-based system if sections system is not available
        return _calculate_progress_steps(telegram_id)


def _calculate_progress_steps(telegram_id: int) -> Dict[str, any]:
    """
    Fallback: Calculate user progress based on completed steps (passed exams).
    Used when sections system is not available.
    
    Args:
        telegram_id: User's Telegram ID
    
    Returns:
        Dictionary with progress data
    """
    # Get all active steps
    all_steps = Step.get_all_active()
    total_steps = len(all_steps)
    
    if total_steps == 0:
        return {
            'percentage': 0,
            'completed': 0,
            'total': 0,
            'current_step_id': 1,
            'current_step_name': '',
            'current_step_number': 0
        }
    
    # Count completed steps (steps where user passed the exam)
    completed_count = 0
    for step in all_steps:
        if UserExamResult.has_passed(telegram_id, step['id']):
            completed_count += 1
    
    # Calculate percentage
    percentage = round((completed_count / total_steps) * 100) if total_steps > 0 else 0
    
    # Get current step info
    user = User.get_or_create(telegram_id)
    current_step_id = user.get('current_step', 1)
    current_step = Step.get_by_id(current_step_id)
    
    # Get current step name in user's language
    current_step_name = ""
    current_step_number = 0
    if current_step:
        user_language = user.get('language', 'en') or 'en'
        current_step_name = Step.get_text_by_language(current_step, 'title_json', user_language)
        # Get step position (1-based) among active steps
        current_step_number = Step.get_step_position(current_step_id)
    
    return {
        'percentage': percentage,
        'completed': completed_count,
        'total': total_steps,
        'current_step_id': current_step_id,
        'current_step_name': current_step_name,
        'current_step_number': current_step_number
    }


def generate_progress_bar(percentage: int, length: int = 10) -> str:
    """
    Generate an adaptive, visually appealing progress bar using Telegram-friendly emojis.
    
    Args:
        percentage: Progress percentage (0-100)
        length: Length of the progress bar (default: 10)
    
    Returns:
        Progress bar string with adaptive emojis based on progress
    """
    # Clamp percentage to 0-100
    percentage = max(0, min(100, percentage))
    
    filled = int((percentage / 100) * length)
    empty = length - filled
    
    # Adaptive emoji selection based on progress
    if percentage == 0:
        # No progress - use empty circles
        filled_emoji = "⚪"
        empty_emoji = "⚪"
    elif percentage < 25:
        # Just started - use blue circles
        filled_emoji = "🔵"
        empty_emoji = "⚪"
    elif percentage < 50:
        # Getting there - use yellow/orange
        filled_emoji = "🟡"
        empty_emoji = "⚪"
    elif percentage < 75:
        # Good progress - use orange
        filled_emoji = "🟠"
        empty_emoji = "⚪"
    elif percentage < 100:
        # Almost done - use green
        filled_emoji = "🟢"
        empty_emoji = "⚪"
    else:
        # Complete - use all green with sparkles
        filled_emoji = "🟢"
        empty_emoji = "✨"
    
    # Build the bar
    bar = filled_emoji * filled + empty_emoji * empty
    
    return bar


def format_progress_message(progress_data: Dict, language: str) -> str:
    """
    Format progress data into a user-friendly message with adaptive visual elements.
    
    Args:
        progress_data: Progress data from calculate_progress()
        language: User's language code
    
    Returns:
        Formatted progress message with emojis and visual appeal
    """
    from utils.i18n import get_text, format_text
    
    percentage = progress_data['percentage']
    completed = progress_data['completed']
    total = progress_data['total']
    current_step_name = progress_data.get('current_step_name', '')
    current_step_number = progress_data.get('current_step_number', 0)
    
    # Generate adaptive progress bar
    progress_bar = generate_progress_bar(percentage)
    
    # Add motivational emoji based on progress
    if percentage == 0:
        motivational_emoji = "🌱"
    elif percentage < 25:
        motivational_emoji = "💪"
    elif percentage < 50:
        motivational_emoji = "🔥"
    elif percentage < 75:
        motivational_emoji = "⭐"
    elif percentage < 100:
        motivational_emoji = "🎯"
    else:
        motivational_emoji = "🏆"
    
    # Build message with visual appeal
    message = format_text('progress_title', language) + "\n"
    message += f"{motivational_emoji} {progress_bar} {percentage}%\n\n"
    
    # Handle edge cases with appropriate emojis
    if completed == 0 and total > 0:
        message += "🚀 " + get_text('progress_no_steps', language) + "\n"
    elif completed == total and total > 0:
        message += "🎉 " + get_text('progress_all_completed', language) + "\n"
    else:
        # Show progress with visual indicators
        progress_indicator = "✅" * min(completed, 5)  # Show up to 5 checkmarks
        if completed > 5:
            progress_indicator += f" +{completed - 5}"
        message += f"{progress_indicator}\n"
        message += format_text('progress_completed', language, 
                             completed=completed, total=total) + "\n"
    
    return message
