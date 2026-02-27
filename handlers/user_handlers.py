"""
User-facing handlers (language selection, steps, exams).
i18n-ready: Uses dynamic language system.
"""
import logging
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import BadRequest
from models import User, Step, Exam, Question, UserExamResult, Section, Lesson, UserSectionProgress, UserLessonProgress
from db import db
from utils.i18n import get_text, format_text, get_available_languages
from utils.helpers import get_user_language, is_admin
from utils.progress import calculate_progress, format_progress_message, generate_progress_bar

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_LANGUAGE = 1


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    telegram_id = update.effective_user.id
    user = User.get_or_create(telegram_id)
    
    # Check if user has selected language
    if not user.get('language'):
        # Show dynamic language selection
        languages = get_available_languages()
        keyboard = []
        
        # Create buttons in rows of 2
        for i in range(0, len(languages), 2):
            row = []
            for lang in languages[i:i+2]:
                flag = "🇮🇷" if lang['code'] == 'fa' else "🇩🇪" if lang['code'] == 'de' else "🇬🇧"
                row.append(InlineKeyboardButton(
                    f"{flag} {lang['native_name']}",
                    callback_data=f"lang_{lang['code']}"
                ))
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Use default language for selection message
        await update.message.reply_text(
            get_text('select_language'),
            reply_markup=reply_markup
        )
        return SELECTING_LANGUAGE
    else:
        # Show main menu
        await show_main_menu(update, context)
        return ConversationHandler.END


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection callback (dynamic language support)."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = query.from_user.id
    language = query.data.split('_')[1]  # 'lang_fa' -> 'fa'
    
    # Validate language exists
    available_codes = [lang['code'] for lang in get_available_languages()]
    if language not in available_codes:
        language = 'en'  # Fallback to English
    
    User.update_language(telegram_id, language)
    
    await query.edit_message_text(
        get_text('language_selected', language)
    )
    
    # Show main menu
    await show_main_menu_from_callback(update, context, language)
    return ConversationHandler.END


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu."""
    telegram_id = update.effective_user.id
    language = get_user_language(telegram_id)
    
    # Create buttons list
    buttons = [
        InlineKeyboardButton(
            get_text('start_learning', language),
            callback_data="start_learning"
        ),
        InlineKeyboardButton(
            get_text('my_profile', language),
            callback_data="my_profile"
        ),
        InlineKeyboardButton(
            get_text('change_language', language),
            callback_data="change_language"
        )
    ]
    
    # Add admin panel button if user is admin
    if is_admin(telegram_id):
        buttons.append(InlineKeyboardButton(
            get_text('admin_panel', language),
            callback_data="admin_panel"
        ))
    
    # Arrange buttons in rows of 2
    keyboard = []
    for i in range(0, len(buttons), 2):
        row = buttons[i:i+2]
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = get_text('main_menu', language)
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
        except BadRequest as e:
            # If message has no text (e.g., it's a photo), delete it and send a new one
            if "no text" in str(e).lower():
                try:
                    await update.callback_query.delete_message()
                except:
                    pass
                await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
            else:
                raise


async def show_main_menu_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
    """Show main menu from callback query."""
    telegram_id = update.callback_query.from_user.id if update.callback_query else update.effective_user.id
    
    # Create buttons list
    buttons = [
        InlineKeyboardButton(
            get_text('start_learning', language),
            callback_data="start_learning"
        ),
        InlineKeyboardButton(
            get_text('my_profile', language),
            callback_data="my_profile"
        ),
        InlineKeyboardButton(
            get_text('change_language', language),
            callback_data="change_language"
        )
    ]
    
    # Add admin panel button if user is admin
    if is_admin(telegram_id):
        buttons.append(InlineKeyboardButton(
            get_text('admin_panel', language),
            callback_data="admin_panel"
        ))
    
    # Arrange buttons in rows of 2
    keyboard = []
    for i in range(0, len(buttons), 2):
        row = buttons[i:i+2]
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = get_text('main_menu', language)
    try:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    except BadRequest as e:
        # If message has no text (e.g., it's a photo), delete it and send a new one
        if "no text" in str(e).lower():
            try:
                await update.callback_query.delete_message()
            except:
                pass
            await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
        else:
            raise


async def start_learning_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start learning callback - shows sections menu or falls back to old system."""
    query = update.callback_query
    await query.answer()
    
    try:
        telegram_id = query.from_user.id
        language = get_user_language(telegram_id)
        
        # Try to use sections/lessons system first
        try:
            active_sections = Section.get_all_active()
            if active_sections:
                await show_sections_menu(update, context, language)
                return
        except Exception as e:
            # If sections table doesn't exist or error, fall back to old system
            logger.warning(f"Sections system not available, falling back to old system: {e}")
        
        # Fallback to old step-based system
        # Check if there are any active steps
        active_steps = Step.get_all_active()
        if not active_steps:
            text = get_text('no_steps_available', language)
            keyboard = [[InlineKeyboardButton(
                get_text('back_to_menu', language),
                callback_data="main_menu"
            )]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
            return
        
        # Get current step ID
        current_step_id = User.get_current_step(telegram_id)
        
        # Check if current step exists and is active
        current_step = Step.get_by_id(current_step_id)
        if not current_step or not current_step['is_active']:
            # Find first active step
            first_step = Step.get_first_active()
            if first_step:
                current_step_id = first_step['id']
                User.update_current_step(telegram_id, current_step_id)
            else:
                text = get_text('no_steps_available', language)
                keyboard = [[InlineKeyboardButton(
                    get_text('back_to_menu', language),
                    callback_data="main_menu"
                )]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text, reply_markup=reply_markup)
                return
        
        await show_step(update, context, current_step_id, language)
    except Exception as e:
        logger.error(f"Error in start_learning_callback: {e}", exc_info=True)
        telegram_id = query.from_user.id
        language = get_user_language(telegram_id)
        text = get_text('error_occurred', language)
        keyboard = [[InlineKeyboardButton(
            get_text('back_to_menu', language),
            callback_data="main_menu"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(text, reply_markup=reply_markup)
        except:
            await query.message.reply_text(text, reply_markup=reply_markup)


async def show_sections_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
    """Show sections menu with lock icons."""
    try:
        telegram_id = update.effective_user.id if update.effective_user else (update.callback_query.from_user.id if update.callback_query else None)
        if not telegram_id:
            return
        
        active_sections = Section.get_all_active()
        if not active_sections:
            text = get_text('no_sections_available', language)
            keyboard = [[InlineKeyboardButton(
                get_text('back_to_menu', language),
                callback_data="main_menu"
            )]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if update.callback_query:
                await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
            return
        
        # Get unlocked sections for this user
        unlocked_section_ids = list(UserSectionProgress.get_unlocked_sections(telegram_id))
        
        # Always unlock first section (ensure it's always available)
        first_section_id = None
        if active_sections:
            first_section = active_sections[0]
            first_section_id = first_section['id']
            if first_section_id not in unlocked_section_ids:
                UserSectionProgress.unlock(telegram_id, first_section_id)
                unlocked_section_ids.append(first_section_id)
        
        text = get_text('sections_menu', language)
        keyboard = []
        
        for index, section in enumerate(active_sections):
            section_title = Section.get_text_by_language(section, 'title_json', language)
            section_id = section['id']
            
            # First section (index 0) is ALWAYS unlocked - no exceptions, no lock icon
            if index == 0:
                # First section: always unlocked, no lock icon, always show_section callback
                display_title = section_title.replace('🔒 ', '')  # Remove lock icon if present
                callback_data = f"show_section_{section_id}"
            else:
                # Other sections: check if unlocked
                is_unlocked = section_id in unlocked_section_ids
                if is_unlocked:
                    display_title = section_title.replace('🔒 ', '')  # Remove lock icon if present
                    callback_data = f"show_section_{section_id}"
                else:
                    display_title = f"🔒 {section_title.replace('🔒 ', '')}"  # Add lock icon
                    callback_data = f"section_locked_{section_id}"
            
            keyboard.append([InlineKeyboardButton(
                display_title,
                callback_data=callback_data
            )])
        
        keyboard.append([InlineKeyboardButton(
            get_text('back_to_menu', language),
            callback_data="main_menu"
        )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
            except BadRequest as e:
                if "no text" in str(e).lower():
                    try:
                        await update.callback_query.delete_message()
                    except:
                        pass
                    await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
                else:
                    raise
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in show_sections_menu: {e}", exc_info=True)


async def show_section_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE, section_id: int, language: str):
    """Show lessons for a section with lock icons."""
    try:
        telegram_id = update.effective_user.id if update.effective_user else (update.callback_query.from_user.id if update.callback_query else None)
        if not telegram_id:
            return
        
        section = Section.get_by_id(section_id)
        if not section or not section['is_active']:
            text = get_text('section_not_found', language)
            keyboard = [[InlineKeyboardButton(
                get_text('back_to_menu', language),
                callback_data="main_menu"
            )]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if update.callback_query:
                await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
            return
        
        # Check if section is unlocked (first section is ALWAYS unlocked)
        active_sections = Section.get_all_active()
        is_first_section = active_sections and len(active_sections) > 0 and active_sections[0]['id'] == section_id
        
        # First section is ALWAYS accessible - unlock it if needed
        if is_first_section:
            if not UserSectionProgress.is_unlocked(telegram_id, section_id):
                UserSectionProgress.unlock(telegram_id, section_id)
        else:
            # For other sections, check if unlocked
            if not UserSectionProgress.is_unlocked(telegram_id, section_id):
                text = get_text('section_locked', language)
                keyboard = [[InlineKeyboardButton(
                    get_text('back_to_sections', language),
                    callback_data="start_learning"
                )]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if update.callback_query:
                    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
                return
        
        lessons = Lesson.get_by_section_id(section_id)
        if not lessons:
            text = get_text('no_lessons_available', language)
            keyboard = [[InlineKeyboardButton(
                get_text('back_to_sections', language),
                callback_data="start_learning"
            )]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if update.callback_query:
                await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
            return
        
        # Get unlocked lessons for this user in this section
        unlocked_lesson_ids = UserLessonProgress.get_unlocked_lessons(telegram_id, section_id)
        
        # Unlock first 2 lessons by default if section is just unlocked
        if not unlocked_lesson_ids and lessons:
            # Unlock first 2 lessons
            for i, lesson in enumerate(lessons[:2]):
                UserLessonProgress.unlock(telegram_id, lesson['id'])
            unlocked_lesson_ids = [lesson['id'] for lesson in lessons[:2]]
        
        section_title = Section.get_text_by_language(section, 'title_json', language)
        text = format_text('section_lessons_title', language, section_title=section_title)
        keyboard = []
        
        for lesson in lessons:
            # Get lesson title from step
            step_title = Step.get_text_by_language(lesson, 'step_title_json', language)
            is_unlocked = lesson['id'] in unlocked_lesson_ids
            
            # Add lock icon if not unlocked
            display_title = f"📖 {step_title}" if is_unlocked else f"🔒 {step_title}"
            
            if is_unlocked:
                keyboard.append([InlineKeyboardButton(
                    display_title,
                    callback_data=f"show_lesson_{lesson['id']}"
                )])
            else:
                keyboard.append([InlineKeyboardButton(
                    display_title,
                    callback_data=f"lesson_locked_{lesson['id']}"
                )])
        
        keyboard.append([InlineKeyboardButton(
            get_text('back_to_sections', language),
            callback_data="start_learning"
        )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
            except BadRequest as e:
                if "no text" in str(e).lower():
                    try:
                        await update.callback_query.delete_message()
                    except:
                        pass
                    await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
                else:
                    raise
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in show_section_lessons: {e}", exc_info=True)


async def show_lesson_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle show lesson callback."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = query.from_user.id
    language = get_user_language(telegram_id)
    lesson_id = int(query.data.split('_')[-1])
    
    lesson = Lesson.get_by_id(lesson_id)
    if not lesson:
        text = get_text('lesson_not_found', language)
        keyboard = [[InlineKeyboardButton(
            get_text('back_to_menu', language),
            callback_data="main_menu"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        return
    
    # Check if lesson is unlocked
    if not UserLessonProgress.is_unlocked(telegram_id, lesson_id):
        text = get_text('lesson_locked', language)
        keyboard = [[InlineKeyboardButton(
            get_text('back_to_sections', language),
            callback_data="start_learning"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        return
    
    # Show the step content (lesson uses step content)
    step_id = lesson['step_id']
    await show_step(update, context, step_id, language)


async def show_section_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle show section callback."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = query.from_user.id
    language = get_user_language(telegram_id)
    section_id = int(query.data.split('_')[-1])
    
    await show_section_lessons(update, context, section_id, language)


async def section_locked_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle locked section callback."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = query.from_user.id
    language = get_user_language(telegram_id)
    section_id = int(query.data.split('_')[-1])
    
    # Check if this is the first section - if so, unlock it and show it
    active_sections = Section.get_all_active()
    is_first_section = active_sections and active_sections[0]['id'] == section_id
    
    if is_first_section:
        # Unlock first section and show it
        UserSectionProgress.unlock(telegram_id, section_id)
        await show_section_lessons(update, context, section_id, language)
        return
    
    text = get_text('section_locked_message', language)
    keyboard = [[InlineKeyboardButton(
        get_text('back_to_sections', language),
        callback_data="start_learning"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)


async def lesson_locked_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle locked lesson callback."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = query.from_user.id
    language = get_user_language(telegram_id)
    
    text = get_text('lesson_locked_message', language)
    keyboard = [[InlineKeyboardButton(
        get_text('back_to_sections', language),
        callback_data="start_learning"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)


async def show_step(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                   step_id: int, language: str = None):
    """Show step content to user."""
    try:
        # Get telegram_id
        telegram_id = update.effective_user.id if update.effective_user else (update.callback_query.from_user.id if update.callback_query else None)
        if not telegram_id:
            return
        
        if language is None:
            language = get_user_language(telegram_id)
        
        step = Step.get_by_id(step_id)
        if not step or not step['is_active']:
            # Try to find first active step
            first_step = Step.get_first_active()
            if first_step:
                step_id = first_step['id']
                User.update_current_step(telegram_id, step_id)
                step = first_step
            else:
                text = get_text('no_steps_available', language)
                keyboard = [[InlineKeyboardButton(
                    get_text('back_to_menu', language),
                    callback_data="main_menu"
                )]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if update.callback_query:
                    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
                return
        
        # Check if step is locked (user hasn't passed previous step)
        if step_id > 1:
            prev_step = Step.get_by_id(step_id - 1)
            if prev_step and prev_step['is_active']:
                if not UserExamResult.has_passed(telegram_id, step_id - 1):
                    text = get_text('step_locked', language)
                    keyboard = [[InlineKeyboardButton(
                        get_text('back_to_menu', language),
                        callback_data="main_menu"
                    )]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    if update.callback_query:
                        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
                    return
        
        # Check if this step belongs to a lesson (for dynamic step numbering within section)
        lesson = db.execute_query(
            """SELECT l.id, l.section_id, l.order_number FROM lessons l 
               WHERE l.step_id = %s AND l.is_active = 1 LIMIT 1""",
            (step_id,),
            fetch_one=True
        )
        
        # Calculate step position and total steps dynamically
        if lesson:
            # Step belongs to a lesson - use lesson position within section
            section_id = lesson['section_id']
            step_position = lesson['order_number']
            # Get total lessons in this section
            all_lessons = Lesson.get_by_section_id(section_id)
            total_steps = len(all_lessons) if all_lessons else 1
        else:
            # Legacy: use global step position
            total_steps = Step.get_total_count()
            if total_steps == 0:
                text = get_text('no_steps_available', language)
                keyboard = [[InlineKeyboardButton(
                    get_text('back_to_menu', language),
                    callback_data="main_menu"
                )]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if update.callback_query:
                    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
                return
            
            # Get step position (1-based) among active steps
            step_position = Step.get_step_position(step_id)
            if step_position == 0:
                # Step not found in active steps, find first active step
                first_step = Step.get_first_active()
                if first_step:
                    step_id = first_step['id']
                    User.update_current_step(telegram_id, step_id)
                    step = first_step
                    step_position = Step.get_step_position(step_id)
                else:
                    text = get_text('no_steps_available', language)
                    keyboard = [[InlineKeyboardButton(
                        get_text('back_to_menu', language),
                        callback_data="main_menu"
                    )]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    if update.callback_query:
                        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
                    return
        
        # Use i18n-ready method to get text by language
        step_title = Step.get_text_by_language(step, 'title_json', language)
        step_description = Step.get_text_by_language(step, 'description_json', language)
        
        if not step_title:
            step_title = get_text('error_occurred', language)
        
        text = format_text('step_title', language, step_num=step_position, total_steps=total_steps)
        text += f"\n\n<b>{step_title}</b>\n\n"
        
        if step_description:
            text += format_text('step_description', language, description=step_description)
        
        keyboard = []
        
        # Check if user has passed exam for this step
        exam_passed = UserExamResult.has_passed(telegram_id, step_id)
        exam = Exam.get_by_step_id(step_id)
        
        if exam and not exam_passed:
            keyboard.append([InlineKeyboardButton(
                get_text('start_exam', language),
                callback_data=f"start_exam_{step_id}"
            )])
        elif exam_passed:
            # Show next step button
            next_step = Step.get_next_step(step_id)
            if next_step:
                keyboard.append([InlineKeyboardButton(
                    get_text('next_step', language),
                    callback_data=f"show_step_{next_step['id']}"
                )])
            else:
                text += f"\n\n{get_text('no_more_steps', language)}"
        
        # Add back button - check if we came from a lesson
        # (lesson variable already retrieved above for dynamic step numbering)
        if lesson:
            # Add back to section button
            keyboard.append([InlineKeyboardButton(
                get_text('back_to_sections', language),
                callback_data="start_learning"
            )])
        else:
            # Legacy: back to menu
            keyboard.append([InlineKeyboardButton(
                get_text('back_to_menu', language),
                callback_data="main_menu"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send file if available
        if step.get('file_id'):
            try:
                # Try to send file (could be photo, video, document, audio, voice)
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=step['file_id'],
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
                if update.callback_query:
                    await update.callback_query.delete_message()
                return
            except:
                try:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=step['file_id'],
                        caption=text,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
                    if update.callback_query:
                        await update.callback_query.delete_message()
                    return
                except:
                    try:
                        # Try sending as voice message
                        await context.bot.send_voice(
                            chat_id=update.effective_chat.id,
                            voice=step['file_id'],
                            caption=text,
                            reply_markup=reply_markup,
                            parse_mode='HTML'
                        )
                        if update.callback_query:
                            await update.callback_query.delete_message()
                        return
                    except:
                        pass
        
        # Send text message if file sending failed or no file
        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
            except BadRequest as e:
                # If message has no text (e.g., it's a photo), delete it and send a new one
                if "no text" in str(e).lower():
                    try:
                        await update.callback_query.delete_message()
                    except:
                        pass
                    await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
                else:
                    raise
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in show_step: {e}", exc_info=True)
        telegram_id = update.effective_user.id if update.effective_user else (update.callback_query.from_user.id if update.callback_query else None)
        if telegram_id:
            language = get_user_language(telegram_id)
            text = get_text('error_occurred', language)
            keyboard = [[InlineKeyboardButton(
                get_text('back_to_menu', language),
                callback_data="main_menu"
            )]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                if update.callback_query:
                    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(text, reply_markup=reply_markup)
            except:
                if update.callback_query:
                    try:
                        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
                    except:
                        pass


async def start_exam_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start exam callback."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = query.from_user.id
    language = get_user_language(telegram_id)
    step_id = int(query.data.split('_')[-1])
    
    exam = Exam.get_by_step_id(step_id)
    if not exam:
        text = get_text('no_exam', language)
        await query.edit_message_text(text)
        return
    
    questions = Question.get_by_exam_id(exam['id'])
    if not questions:
        text = get_text('no_exam', language)
        await query.edit_message_text(text)
        return
    
    # Get step to preserve file_id
    step = Step.get_by_id(step_id)
    step_file_id = step.get('file_id') if step else None
    
    # Store exam data in context (including file_id to preserve it)
    context.user_data['exam_step_id'] = step_id
    context.user_data['exam_questions'] = questions
    context.user_data['exam_answers'] = []
    context.user_data['exam_question_status'] = {}  # Track correct/incorrect status
    context.user_data['exam_current_question'] = 0
    context.user_data['exam_step_file_id'] = step_file_id  # Store file_id to preserve during exam
    
    # Show first question
    await show_exam_question(update, context, 0, language)


async def show_exam_question(update: Update, context: ContextTypes.DEFAULT_TYPE,
                            question_index: int, language: str):
    """Show exam question to user."""
    questions = context.user_data.get('exam_questions', [])
    if question_index >= len(questions):
        # Exam completed
        await finish_exam(update, context, language)
        return
    
    question = questions[question_index]
    question_text = Question.get_text_by_language(question, language)
    options = json.loads(question['options_json']) if isinstance(question['options_json'], str) else question['options_json']
    total_questions = len(questions)
    question_status = context.user_data.get('exam_question_status', {})
    answers = context.user_data.get('exam_answers', [])
    
    # Get step position for display
    exam_step_id = context.user_data.get('exam_step_id', 0)
    step_position = Step.get_step_position(exam_step_id) if exam_step_id > 0 else 0
    text = format_text('exam_start', language, step_num=step_position)
    text += f"\n\n{format_text('question_num', language, current=question_index + 1, total=total_questions)}"
    
    # Show list of all questions with their status
    text += f"\n\n<b>{get_text('question_list', language)}:</b>\n"
    for idx, q in enumerate(questions):
        status_icon = ""
        if idx in question_status:
            if question_status[idx] == 'correct':
                status_icon = "✅"  # Green checkmark for correct
            else:
                status_icon = "❌"  # Red X for incorrect
        elif idx < len(answers) and answers[idx] != -1:
            # Question answered but status not set yet (shouldn't happen, but just in case)
            status_icon = "⏳"
        else:
            status_icon = "⚪"  # Not answered yet
        
        current_marker = "👉" if idx == question_index else ""
        # Simple question number display
        q_num_text = format_text('question_num', language, current=idx + 1, total=total_questions)
        # Extract just the question part (remove emoji and newlines)
        q_num_text = q_num_text.replace('❓ ', '').split('\n')[0] if '\n' in q_num_text else q_num_text.replace('❓ ', '')
        text += f"{current_marker} {status_icon} {q_num_text}\n"
    
    text += f"\n<b>{question_text}</b>\n\n"
    text += get_text('select_answer', language) + "\n"
    
    keyboard = []
    current_answer = answers[question_index] if question_index < len(answers) else -1
    is_correct = question_status.get(question_index) == 'correct'
    is_incorrect = question_status.get(question_index) == 'incorrect'
    
    for i, option in enumerate(options):
        button_text = f"{i + 1}. {option}"
        
        # Add status indicators to buttons
        if current_answer == i:
            if is_correct:
                button_text = f"✅ {button_text}"  # Green checkmark
            elif is_incorrect:
                button_text = f"❌ {button_text}"  # Red X
        
        keyboard.append([InlineKeyboardButton(
            button_text,
            callback_data=f"exam_answer_{question_index}_{i}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        get_text('cancel', language),
        callback_data="cancel_exam"
    )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Get file_id from context to preserve it during exam
    file_id = context.user_data.get('exam_step_file_id')
    
    # If file exists, send it with the question (preserve file during all exam stages)
    if file_id:
        try:
            # Try to send file (could be photo, video, document, audio, voice)
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=file_id,
                caption=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            if update.callback_query:
                try:
                    await update.callback_query.delete_message()
                except:
                    pass
            return
        except:
            try:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=file_id,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
                if update.callback_query:
                    try:
                        await update.callback_query.delete_message()
                    except:
                        pass
                return
            except:
                try:
                    # Try sending as voice message
                    await context.bot.send_voice(
                        chat_id=update.effective_chat.id,
                        voice=file_id,
                        caption=text,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
                    if update.callback_query:
                        try:
                            await update.callback_query.delete_message()
                        except:
                            pass
                    return
                except:
                    pass
    
    # If no file or file sending failed, send text message
    try:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    except BadRequest as e:
        # If message has no text (e.g., it's a photo), delete it and send a new one
        if "no text" in str(e).lower():
            try:
                await update.callback_query.delete_message()
            except:
                pass
            await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            raise


async def exam_answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle exam answer callback."""
    query = update.callback_query
    telegram_id = query.from_user.id
    language = get_user_language(telegram_id)
    
    parts = query.data.split('_')
    question_index = int(parts[2])
    answer_index = int(parts[3])
    
    # Store answer
    if 'exam_answers' not in context.user_data:
        context.user_data['exam_answers'] = []
    
    # Ensure list is long enough
    while len(context.user_data['exam_answers']) <= question_index:
        context.user_data['exam_answers'].append(-1)
    
    context.user_data['exam_answers'][question_index] = answer_index
    
    # Check if answer is correct and store status
    questions = context.user_data.get('exam_questions', [])
    feedback_text = ""
    if question_index < len(questions):
        question = questions[question_index]
        correct_option = question['correct_option']
        
        if 'exam_question_status' not in context.user_data:
            context.user_data['exam_question_status'] = {}
        
        if answer_index == correct_option:
            context.user_data['exam_question_status'][question_index] = 'correct'
            feedback_text = "✅ درست!"
        else:
            context.user_data['exam_question_status'][question_index] = 'incorrect'
            feedback_text = "❌ اشتباه!"
    
    # Show feedback and move to next question
    await query.answer(feedback_text, show_alert=False)
    await show_exam_question(update, context, question_index + 1, language)


async def finish_exam(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
    """Finish exam and show results."""
    questions = context.user_data.get('exam_questions', [])
    answers = context.user_data.get('exam_answers', [])
    step_id = context.user_data.get('exam_step_id')
    
    # Calculate score
    correct_answers = [q['correct_option'] for q in questions]
    
    # Pad answers if needed
    while len(answers) < len(correct_answers):
        answers.append(-1)
    
    correct = sum(1 for a, c in zip(answers, correct_answers) if a == c)
    score = (correct / len(correct_answers)) * 100.0 if correct_answers else 0.0
    passed = score >= 80.0
    
    # Save result
    telegram_id = update.effective_user.id
    UserExamResult.save_result(telegram_id, step_id, score, passed)
    
    # Show results
    text = get_text('exam_completed', language)
    text += f"\n\n{format_text('exam_score', language, score=f'{score:.1f}')}"
    text += f"\n{get_text('passing_score', language)}\n\n"
    
    # Show detailed results for each question
    text += f"{get_text('exam_results_title', language)}\n"
    for idx, question in enumerate(questions):
        user_answer_idx = answers[idx] if idx < len(answers) else -1
        correct_answer_idx = question['correct_option']
        is_correct = user_answer_idx == correct_answer_idx
        
        # Get option texts
        options = json.loads(question['options_json']) if isinstance(question['options_json'], str) else question['options_json']
        
        if is_correct:
            text += format_text('question_result_correct', language, num=idx + 1) + "\n"
        else:
            user_answer_text = options[user_answer_idx] if 0 <= user_answer_idx < len(options) else get_text('no_answer', language)
            text += format_text('question_result_incorrect', language, 
                              num=idx + 1, 
                              user_answer=user_answer_text) + "\n"
    
    text += "\n"
    
    if passed:
        text += get_text('exam_passed', language)
        
        # Find which lesson this step belongs to
        lesson = db.execute_query(
            """SELECT l.*, l.section_id FROM lessons l 
               WHERE l.step_id = %s AND l.is_active = 1 LIMIT 1""",
            (step_id,),
            fetch_one=True
        )
        
        if lesson:
            lesson_id = lesson['id']
            section_id = lesson['section_id']
            
            # Unlock next lesson in the same section
            next_lesson = db.execute_query(
                """SELECT * FROM lessons 
                   WHERE section_id = %s AND order_number > %s AND is_active = 1 
                   ORDER BY order_number ASC LIMIT 1""",
                (section_id, lesson['order_number']),
                fetch_one=True
            )
            
            if next_lesson:
                UserLessonProgress.unlock(telegram_id, next_lesson['id'])
                text += f"\n\n✅ {get_text('next_lesson_unlocked', language)}"
            else:
                # All lessons in this section are completed, unlock next section
                current_section = Section.get_by_id(section_id)
                if current_section:
                    next_section = db.execute_query(
                        """SELECT * FROM sections 
                           WHERE order_number > %s AND is_active = 1 
                           ORDER BY order_number ASC LIMIT 1""",
                        (current_section['order_number'],),
                        fetch_one=True
                    )
                    
                    if next_section:
                        UserSectionProgress.unlock(telegram_id, next_section['id'])
                        # Unlock first 2 lessons of next section
                        next_section_lessons = Lesson.get_by_section_id(next_section['id'])
                        for i, next_lesson in enumerate(next_section_lessons[:2]):
                            UserLessonProgress.unlock(telegram_id, next_lesson['id'])
                        text += f"\n\n🎉 {get_text('next_section_unlocked', language)}"
        
        # Unlock next step (legacy support)
        next_step = Step.get_next_step(step_id)
        if next_step:
            User.update_current_step(telegram_id, next_step['id'])
        
        # Show updated progress after passing exam with visual appeal
        text += "\n\n"
        progress_data = calculate_progress(telegram_id)
        progress_bar = generate_progress_bar(progress_data['percentage'])
        
        # Add celebration emoji for progress update
        if progress_data['percentage'] == 100:
            celebration = "🏆"
        elif progress_data['percentage'] >= 75:
            celebration = "🎯"
        else:
            celebration = "📈"
        
        text += f"{celebration} {get_text('progress_title', language).split(':')[0]}\n"
        text += f"{progress_bar} {progress_data['percentage']}%"
    else:
        text += get_text('exam_failed', language)
    
    keyboard = []
    if passed:
        next_step = Step.get_next_step(step_id)
        if next_step:
            keyboard.append([InlineKeyboardButton(
                get_text('next_step', language),
                callback_data=f"show_step_{next_step['id']}"
            )])
    
    keyboard.append([InlineKeyboardButton(
        get_text('back_to_menu', language),
        callback_data="main_menu"
    )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    except BadRequest as e:
        # If message has no text (e.g., it's a photo), delete it and send a new one
        if "no text" in str(e).lower():
            try:
                await update.callback_query.delete_message()
            except:
                pass
            await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
        else:
            raise


async def cancel_exam_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cancel exam callback."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = query.from_user.id
    language = get_user_language(telegram_id)
    
    # Clear exam data (but preserve file_id in case user wants to see step again)
    context.user_data.pop('exam_step_id', None)
    context.user_data.pop('exam_questions', None)
    context.user_data.pop('exam_answers', None)
    context.user_data.pop('exam_question_status', None)
    context.user_data.pop('exam_current_question', None)
    # Note: We keep 'exam_step_file_id' in context in case it's needed later
    # It will be cleared when starting a new exam or when user_data is cleared
    
    await show_main_menu_from_callback(update, context, language)


async def my_progress_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle my progress callback (legacy - shows basic info)."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = query.from_user.id
    language = get_user_language(telegram_id)
    current_step_id = User.get_current_step(telegram_id)
    total_steps = Step.get_total_count()
    
    text = format_text('progress_info', language, 
                      current_step=current_step_id, 
                      total_steps=total_steps)
    
    keyboard = [[InlineKeyboardButton(
        get_text('back_to_menu', language),
        callback_data="main_menu"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(text, reply_markup=reply_markup)
    except BadRequest as e:
        # If message has no text (e.g., it's a photo), delete it and send a new one
        if "no text" in str(e).lower():
            try:
                await query.delete_message()
            except:
                pass
            await query.message.reply_text(text, reply_markup=reply_markup)
        else:
            raise


async def view_progress_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle view progress callback (shows detailed progress with visual bar)."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = query.from_user.id
    language = get_user_language(telegram_id)
    
    # Calculate progress
    progress_data = calculate_progress(telegram_id)
    
    # Format progress message
    text = format_progress_message(progress_data, language)
    
    keyboard = [[InlineKeyboardButton(
        get_text('back_to_menu', language),
        callback_data="main_menu"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(text, reply_markup=reply_markup)
    except BadRequest as e:
        # If message has no text (e.g., it's a photo), delete it and send a new one
        if "no text" in str(e).lower():
            try:
                await query.delete_message()
            except:
                pass
            await query.message.reply_text(text, reply_markup=reply_markup)
        else:
            raise


async def my_profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle my profile callback - shows profile with progress and account time."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = query.from_user.id
    language = get_user_language(telegram_id)
    
    # Build profile message
    text = get_text('profile_title', language) + "\n\n"
    
    # Add progress information
    progress_data = calculate_progress(telegram_id)
    progress_text = format_progress_message(progress_data, language)
    text += progress_text + "\n"
    
    # Add account remaining time
    text += "─" * 20 + "\n\n"
    remaining_time = User.get_account_remaining_time(telegram_id)
    
    if remaining_time.get('unlimited'):
        text += get_text('account_no_expiration', language)
    elif remaining_time.get('expired'):
        text += get_text('account_expired', language)
    else:
        text += get_text('account_remaining_time', language) + "\n"
        days = remaining_time.get('days', 0)
        hours = remaining_time.get('hours', 0)
        minutes = remaining_time.get('minutes', 0)
        
        time_parts = []
        if days > 0:
            time_parts.append(format_text('days_remaining', language, days=days))
        if hours > 0:
            time_parts.append(format_text('hours_remaining', language, hours=hours))
        if minutes > 0 or len(time_parts) == 0:
            time_parts.append(format_text('minutes_remaining', language, minutes=minutes))
        
        text += " ".join(time_parts)
    
    # Create keyboard with back button
    keyboard = [
        [InlineKeyboardButton(
            get_text('back_to_menu', language),
            callback_data="main_menu"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(text, reply_markup=reply_markup)
    except BadRequest as e:
        # If message has no text (e.g., it's a photo), delete it and send a new one
        if "no text" in str(e).lower():
            try:
                await query.delete_message()
            except:
                pass
            await query.message.reply_text(text, reply_markup=reply_markup)
        else:
            raise


async def show_step_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle show step callback."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = query.from_user.id
    language = get_user_language(telegram_id)
    step_id = int(query.data.split('_')[-1])
    
    await show_step(update, context, step_id, language)


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu callback."""
    query = update.callback_query
    await query.answer()
    
    await show_main_menu(update, context)


async def change_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle change language callback."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = query.from_user.id
    current_language = get_user_language(telegram_id)
    
    # Show dynamic language selection
    languages = get_available_languages()
    keyboard = []
    
    # Create buttons in rows of 2
    for i in range(0, len(languages), 2):
        row = []
        for lang in languages[i:i+2]:
            flag = "🇮🇷" if lang['code'] == 'fa' else "🇩🇪" if lang['code'] == 'de' else "🇬🇧"
            row.append(InlineKeyboardButton(
                f"{flag} {lang['native_name']}",
                callback_data=f"lang_{lang['code']}"
            ))
        keyboard.append(row)
    
    # Add back button
    keyboard.append([InlineKeyboardButton(
        get_text('back_to_menu', current_language),
        callback_data="main_menu"
    )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Use current language for selection message
    await query.edit_message_text(
        get_text('select_language', current_language),
        reply_markup=reply_markup
    )
