"""
Admin panel handlers (CRUD operations for steps and exams).
i18n-ready: Uses dynamic language system.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from models import Step, Exam, Question, User, Section, Lesson
from utils.i18n import get_text, format_text, get_available_languages
from utils.helpers import is_admin, get_user_language, parse_options, validate_correct_option, safe_answer_callback, safe_reply_text
import json
import os

# Conversation states for admin
ADMIN_MENU = 1
MANAGE_STEPS = 2
ADD_STEP_TITLE_FA = 3
ADD_STEP_TITLE_DE = 4
ADD_STEP_DESC_FA = 5
ADD_STEP_DESC_DE = 6
ADD_STEP_FILE = 7
EDIT_STEP_SELECT = 8
EDIT_STEP_TITLE_FA = 9
EDIT_STEP_TITLE_DE = 10
EDIT_STEP_DESC_FA = 11
EDIT_STEP_DESC_DE = 12
EDIT_STEP_FILE = 13
MANAGE_EXAMS = 14
SELECT_STEP_FOR_EXAM = 15
EXAM_MENU = 16
ADD_QUESTION_FA = 17
ADD_QUESTION_DE = 18
ADD_QUESTION_OPTIONS = 19
ADD_QUESTION_CORRECT = 20
EDIT_QUESTION_SELECT = 21
EDIT_QUESTION_FA = 22
EDIT_QUESTION_DE = 23
EDIT_QUESTION_OPTIONS = 24
EDIT_QUESTION_CORRECT = 25
MANAGE_USERS = 26
EDIT_USER_NAME = 27
EDIT_USER_MOBILE = 28
MANAGE_SECTIONS = 29
ADD_SECTION_TITLE_FA = 30
ADD_SECTION_TITLE_DE = 31
ADD_SECTION_DESC_FA = 32
ADD_SECTION_DESC_DE = 33
EDIT_SECTION_SELECT = 34
EDIT_SECTION_TITLE_FA = 35
EDIT_SECTION_TITLE_DE = 36
EDIT_SECTION_DESC_FA = 37
EDIT_SECTION_DESC_DE = 38
SELECT_SECTION_FOR_LESSON = 39
SELECT_STEP_FOR_LESSON = 40


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command."""
    telegram_id = update.effective_user.id
    
    if not is_admin(telegram_id):
        language = get_user_language(telegram_id)
        await update.message.reply_text(get_text('admin_only', language))
        return ConversationHandler.END
    
    await show_admin_menu(update, context)
    return ADMIN_MENU


async def admin_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin panel button callback."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    
    if not is_admin(telegram_id):
        language = get_user_language(telegram_id)
        await query.edit_message_text(get_text('admin_only', language))
        return
    
    await show_admin_menu(update, context)
    return ADMIN_MENU


async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin menu."""
    telegram_id = update.effective_user.id
    language = get_user_language(telegram_id)
    
    keyboard = [
        [InlineKeyboardButton(
            get_text('manage_steps', language),
            callback_data="admin_manage_steps"
        )],
        [InlineKeyboardButton(
            get_text('manage_sections', language),
            callback_data="admin_manage_sections"
        )],
        [InlineKeyboardButton(
            get_text('manage_exams', language),
            callback_data="admin_manage_exams"
        )],
        [InlineKeyboardButton(
            get_text('manage_users', language),
            callback_data="admin_manage_users"
        )],
        [InlineKeyboardButton(
            get_text('back_to_menu', language),
            callback_data="main_menu"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = get_text('admin_menu', language)
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)


# Step management callbacks
async def admin_manage_steps_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle manage steps callback."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    
    keyboard = [
        [InlineKeyboardButton(
            get_text('add_step', language),
            callback_data="admin_add_step"
        )],
        [InlineKeyboardButton(
            get_text('step_list', language),
            callback_data="admin_step_list"
        )],
        [InlineKeyboardButton(
            get_text('back', language),
            callback_data="admin_menu"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = get_text('manage_steps', language)
    await query.edit_message_text(text, reply_markup=reply_markup)
    
    return MANAGE_STEPS


async def admin_add_step_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding a new step (i18n-ready)."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    languages = get_available_languages()
    
    # Initialize collection state
    context.user_data['collecting_languages'] = [lang['code'] for lang in languages]
    context.user_data['current_lang_index'] = 0
    # Initialize individual language fields
    context.user_data['new_step_title_fa'] = ''
    context.user_data['new_step_title_de'] = ''
    context.user_data['new_step_desc_fa'] = ''
    context.user_data['new_step_desc_de'] = ''
    
    # Start with Persian title
    await query.edit_message_text(
        get_text('enter_title_fa', language)
    )
    return ADD_STEP_TITLE_FA


async def admin_add_another_step_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle adding another step after successfully creating one."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    languages = get_available_languages()
    
    # Initialize collection state
    context.user_data['collecting_languages'] = [lang['code'] for lang in languages]
    context.user_data['current_lang_index'] = 0
    # Initialize individual language fields
    context.user_data['new_step_title_fa'] = ''
    context.user_data['new_step_title_de'] = ''
    context.user_data['new_step_desc_fa'] = ''
    context.user_data['new_step_desc_de'] = ''
    
    # Start with first language (Persian)
    await query.edit_message_text(
        get_text('enter_title_fa', language)
    )
    return ADD_STEP_TITLE_FA


async def admin_add_step_title_fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive step title in Farsi."""
    context.user_data['new_step_title_fa'] = update.message.text
    language = get_user_language(update.effective_user.id)
    
    await update.message.reply_text(get_text('enter_title_de', language))
    return ADD_STEP_TITLE_DE


async def admin_add_step_title_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive step title in German."""
    context.user_data['new_step_title_de'] = update.message.text
    language = get_user_language(update.effective_user.id)
    
    await update.message.reply_text(get_text('enter_description_fa', language))
    return ADD_STEP_DESC_FA


async def admin_add_step_desc_fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive step description in Farsi."""
    context.user_data['new_step_desc_fa'] = update.message.text
    language = get_user_language(update.effective_user.id)
    
    await update.message.reply_text(get_text('enter_description_de', language))
    return ADD_STEP_DESC_DE


async def admin_add_step_desc_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive step description in German."""
    context.user_data['new_step_desc_de'] = update.message.text
    language = get_user_language(update.effective_user.id)
    
    await update.message.reply_text(get_text('upload_file', language))
    return ADD_STEP_FILE


async def admin_add_step_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive step file."""
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    
    # Get file_id from message
    file_id = None
    if update.message.document:
        file_id = update.message.document.file_id
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
    elif update.message.video:
        file_id = update.message.video.file_id
    elif update.message.audio:
        file_id = update.message.audio.file_id
    elif update.message.voice:
        file_id = update.message.voice.file_id
    
    if not file_id:
        await update.message.reply_text(get_text('invalid_input', language))
        return ADD_STEP_FILE
    
    # Create step with multilingual content (i18n-ready)
    title_json = {
        'fa': context.user_data.get('new_step_title_fa', ''),
        'de': context.user_data.get('new_step_title_de', '')
    }
    description_json = {
        'fa': context.user_data.get('new_step_desc_fa', ''),
        'de': context.user_data.get('new_step_desc_de', '')
    }
    
    step_id = Step.create(
        title_json=title_json,
        description_json=description_json,
        file_id=file_id
    )
    
    # Clear temp data
    context.user_data.pop('new_step_title_fa', None)
    context.user_data.pop('new_step_title_de', None)
    context.user_data.pop('new_step_desc_fa', None)
    context.user_data.pop('new_step_desc_de', None)
    context.user_data.pop('collecting_languages', None)
    context.user_data.pop('current_lang_index', None)
    
    # Show success message with option to add another step
    text = get_text('step_created', language)
    text += "\n\n" + get_text('add_another_step_prompt', language)
    
    keyboard = [
        [InlineKeyboardButton(
            get_text('add_another_step', language),
            callback_data="admin_add_another_step"
        )],
        [InlineKeyboardButton(
            get_text('back_to_admin_menu', language),
            callback_data="admin_menu"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)
    return ConversationHandler.END


async def admin_step_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of steps."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    steps = Step.get_all_active()
    
    if not steps:
        text = "No steps available."
        keyboard = [[InlineKeyboardButton(
            get_text('back', language),
            callback_data="admin_manage_steps"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        return
    
    keyboard = []
    for step in steps:
        status = "✅" if step['is_active'] else "❌"
        step_title = Step.get_text_by_language(step, 'title_json', language)
        step_position = Step.get_step_position(step['id'])
        keyboard.append([InlineKeyboardButton(
            f"{status} Step {step_position}: {step_title}",
            callback_data=f"admin_step_detail_{step['id']}"
        )])
        # Add edit and delete buttons for each step
        keyboard.append([
            InlineKeyboardButton(
                get_text('edit_step', language),
                callback_data=f"admin_edit_step_{step['id']}"
            ),
            InlineKeyboardButton(
                get_text('delete_step', language),
                callback_data=f"admin_delete_step_{step['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(
        get_text('back', language),
        callback_data="admin_manage_steps"
    )])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = get_text('step_list', language)
    await query.edit_message_text(text, reply_markup=reply_markup)


async def admin_step_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show step details and actions."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    step_id = int(query.data.split('_')[-1])
    step = Step.get_by_id(step_id)
    
    if not step:
        await query.edit_message_text(get_text('error_occurred', language))
        return
    
    # Get step position (1-based) instead of using step_id
    step_position = Step.get_step_position(step_id)
    text = format_text('step_details', language, step_id=step_position)
    
    # Get multilingual content (i18n-ready)
    title_fa = Step.get_text_by_language(step, 'title_json', 'fa')
    title_de = Step.get_text_by_language(step, 'title_json', 'de')
    
    text += f"\n\n<b>FA:</b> {title_fa}\n"
    text += f"<b>DE:</b> {title_de}\n"
    text += f"<b>Active:</b> {'Yes' if step['is_active'] else 'No'}\n"
    text += f"<b>Users:</b> {Step.get_user_count(step_id)}"
    
    keyboard = [
        [InlineKeyboardButton(
            get_text('edit_step', language),
            callback_data=f"admin_edit_step_{step_id}"
        )],
        [InlineKeyboardButton(
            get_text('toggle_step', language),
            callback_data=f"admin_toggle_step_{step_id}"
        )],
        [InlineKeyboardButton(
            get_text('delete_step', language),
            callback_data=f"admin_delete_step_{step_id}"
        )],
        [InlineKeyboardButton(
            get_text('back', language),
            callback_data="admin_step_list"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')


async def admin_toggle_step_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle step active status."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    step_id = int(query.data.split('_')[-1])
    
    Step.toggle_active(step_id)
    await safe_answer_callback(query, get_text('step_toggled', language))
    
    # Refresh step detail
    await admin_step_detail_callback(update, context)


async def admin_delete_step_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show confirmation dialog for deleting a step."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    step_id = int(query.data.split('_')[-1])
    
    # Show confirmation dialog
    text = get_text('confirm_delete_step', language)
    
    keyboard = [
        [InlineKeyboardButton(
            get_text('yes', language),
            callback_data=f"admin_confirm_delete_step_{step_id}"
        )],
        [InlineKeyboardButton(
            get_text('no', language),
            callback_data="admin_step_list"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)


async def admin_confirm_delete_step_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and delete a step."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    step_id = int(query.data.split('_')[-1])
    
    # Clear any edit-related data
    context.user_data.pop('editing_step_id', None)
    context.user_data.pop('edit_step_title_fa', None)
    context.user_data.pop('edit_step_title_de', None)
    context.user_data.pop('edit_step_desc_fa', None)
    context.user_data.pop('edit_step_desc_de', None)
    
    Step.delete(step_id)
    await safe_answer_callback(query, get_text('step_deleted', language))
    
    # Go back to step list
    await admin_step_list_callback(update, context)
    
    return ConversationHandler.END


async def admin_edit_step_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start editing a step."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    step_id = int(query.data.split('_')[-1])
    context.user_data['editing_step_id'] = step_id
    
    step = Step.get_by_id(step_id)
    if not step:
        await query.edit_message_text(get_text('error_occurred', language))
        return ConversationHandler.END
    
    # Parse JSON fields (i18n-ready)
    title_json = step.get('title_json', {})
    if isinstance(title_json, str):
        title_json = json.loads(title_json)
    description_json = step.get('description_json', {})
    if isinstance(description_json, str):
        description_json = json.loads(description_json)
    
    context.user_data['edit_step_title_fa'] = title_json.get('fa', '')
    context.user_data['edit_step_title_de'] = title_json.get('de', '')
    context.user_data['edit_step_desc_fa'] = description_json.get('fa', '')
    context.user_data['edit_step_desc_de'] = description_json.get('de', '')
    
    # Show current value in prompt
    current_fa = title_json.get('fa', '')
    prompt_text = get_text('enter_title_fa', language)
    if current_fa:
        prompt_text += f"\n\n📝 مقدار فعلی:\n{current_fa}"
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data=f"cancel_edit_step_{step_id}"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(prompt_text, reply_markup=reply_markup)
    return EDIT_STEP_TITLE_FA


async def admin_edit_step_title_fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive edited step title in Farsi."""
    context.user_data['edit_step_title_fa'] = update.message.text
    language = get_user_language(update.effective_user.id)
    step_id = context.user_data.get('editing_step_id')
    
    # Show current value in prompt
    current_de = context.user_data.get('edit_step_title_de', '')
    prompt_text = get_text('enter_title_de', language)
    if current_de:
        prompt_text += f"\n\n📝 مقدار فعلی:\n{current_de}"
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data=f"cancel_edit_step_{step_id}"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(prompt_text, reply_markup=reply_markup)
    return EDIT_STEP_TITLE_DE


async def admin_edit_step_title_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive edited step title in German."""
    context.user_data['edit_step_title_de'] = update.message.text
    language = get_user_language(update.effective_user.id)
    step_id = context.user_data.get('editing_step_id')
    
    # Show current value in prompt
    current_fa = context.user_data.get('edit_step_desc_fa', '')
    prompt_text = get_text('enter_description_fa', language)
    if current_fa:
        prompt_text += f"\n\n📝 مقدار فعلی:\n{current_fa}"
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data=f"cancel_edit_step_{step_id}"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(prompt_text, reply_markup=reply_markup)
    return EDIT_STEP_DESC_FA


async def admin_edit_step_desc_fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive edited step description in Farsi."""
    context.user_data['edit_step_desc_fa'] = update.message.text
    language = get_user_language(update.effective_user.id)
    step_id = context.user_data.get('editing_step_id')
    
    # Show current value in prompt
    current_de = context.user_data.get('edit_step_desc_de', '')
    prompt_text = get_text('enter_description_de', language)
    if current_de:
        prompt_text += f"\n\n📝 مقدار فعلی:\n{current_de}"
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data=f"cancel_edit_step_{step_id}"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(prompt_text, reply_markup=reply_markup)
    return EDIT_STEP_DESC_DE


async def admin_edit_step_desc_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive edited step description in German."""
    context.user_data['edit_step_desc_de'] = update.message.text
    language = get_user_language(update.effective_user.id)
    step_id = context.user_data.get('editing_step_id')
    
    prompt_text = get_text('upload_file', language)
    prompt_text += "\n\n💡 می‌توانید فایل را رد کنید و فقط متن را تغییر دهید."
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data=f"cancel_edit_step_{step_id}"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(prompt_text, reply_markup=reply_markup)
    return EDIT_STEP_FILE


async def admin_edit_step_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive edited step file."""
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    
    step_id = context.user_data.get('editing_step_id')
    if not step_id:
        await update.message.reply_text(get_text('error_occurred', language))
        return ConversationHandler.END
    
    # Get file_id from message (optional - user can skip by sending /skip or text)
    file_id = None
    if update.message.document:
        file_id = update.message.document.file_id
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
    elif update.message.video:
        file_id = update.message.video.file_id
    elif update.message.audio:
        file_id = update.message.audio.file_id
    elif update.message.voice:
        file_id = update.message.voice.file_id
    
    # Build multilingual content from collected data
    title_json = {
        'fa': context.user_data.get('edit_step_title_fa', ''),
        'de': context.user_data.get('edit_step_title_de', '')
    }
    description_json = {
        'fa': context.user_data.get('edit_step_desc_fa', ''),
        'de': context.user_data.get('edit_step_desc_de', '')
    }
    
    # Update step (file_id is optional - if not provided, keep existing)
    if file_id:
        Step.update(
            step_id=step_id,
            title_json=title_json,
            description_json=description_json,
            file_id=file_id
        )
    else:
        Step.update(
            step_id=step_id,
            title_json=title_json,
            description_json=description_json
        )
    
    # Clear temp data
    context.user_data.pop('editing_step_id', None)
    context.user_data.pop('edit_step_title_fa', None)
    context.user_data.pop('edit_step_title_de', None)
    context.user_data.pop('edit_step_desc_fa', None)
    context.user_data.pop('edit_step_desc_de', None)
    
    await update.message.reply_text(get_text('step_updated', language))
    await show_admin_menu(update, context)
    return ADMIN_MENU


async def admin_cancel_edit_step_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel editing a step."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    step_id = int(query.data.split('_')[-1])
    
    # Clear temp data
    context.user_data.pop('editing_step_id', None)
    context.user_data.pop('edit_step_title_fa', None)
    context.user_data.pop('edit_step_title_de', None)
    context.user_data.pop('edit_step_desc_fa', None)
    context.user_data.pop('edit_step_desc_de', None)
    
    # Show step detail again
    step = Step.get_by_id(step_id)
    if step:
        # Get step position (1-based) instead of using step_id
        step_position = Step.get_step_position(step_id)
        text = format_text('step_details', language, step_id=step_position)
        
        # Get multilingual content (i18n-ready)
        title_fa = Step.get_text_by_language(step, 'title_json', 'fa')
        title_de = Step.get_text_by_language(step, 'title_json', 'de')
        
        text += f"\n\n<b>FA:</b> {title_fa}\n"
        text += f"<b>DE:</b> {title_de}\n"
        text += f"<b>Active:</b> {'Yes' if step['is_active'] else 'No'}\n"
        text += f"<b>Users:</b> {Step.get_user_count(step_id)}"
        
        keyboard = [
            [InlineKeyboardButton(
                get_text('edit_step', language),
                callback_data=f"admin_edit_step_{step_id}"
            )],
            [InlineKeyboardButton(
                get_text('toggle_step', language),
                callback_data=f"admin_toggle_step_{step_id}"
            )],
            [InlineKeyboardButton(
                get_text('delete_step', language),
                callback_data=f"admin_delete_step_{step_id}"
            )],
            [InlineKeyboardButton(
                get_text('back', language),
                callback_data="admin_step_list"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    else:
        # If step not found, go back to step list
        await admin_step_list_callback(update, context)
    
    return ConversationHandler.END


# Exam management callbacks
async def admin_manage_exams_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle manage exams callback."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    steps = Step.get_all_active()
    
    if not steps:
        text = "No steps available."
        keyboard = [[InlineKeyboardButton(
            get_text('back', language),
            callback_data="admin_menu"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        return
    
    keyboard = []
    for step in steps:
        step_title = Step.get_text_by_language(step, 'title_json', language)
        step_position = Step.get_step_position(step['id'])
        keyboard.append([InlineKeyboardButton(
            f"Step {step_position}: {step_title}",
            callback_data=f"admin_exam_step_{step['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        get_text('back', language),
        callback_data="admin_menu"
    )])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = get_text('select_step_for_exam', language)
    await query.edit_message_text(text, reply_markup=reply_markup)
    
    return SELECT_STEP_FOR_EXAM


async def show_exam_menu_for_step(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                   step_id: int, language: str = None):
    """Helper function to show exam menu for a step."""
    telegram_id = update.effective_user.id if update.effective_user else (update.callback_query.from_user.id if update.callback_query else None)
    if not telegram_id or not is_admin(telegram_id):
        return
    
    if language is None:
        language = get_user_language(telegram_id)
    
    context.user_data['exam_step_id'] = step_id
    
    exam = Exam.get_by_step_id(step_id)
    if not exam:
        # Create exam if it doesn't exist
        exam_id = Exam.create(step_id)
        exam = Exam.get_by_step_id(step_id)
    
    questions = Question.get_by_exam_id(exam['id'])
    
    step_position = Step.get_step_position(step_id)
    text = format_text('exam_management', language, step_id=step_position)
    text += f"\n\nQuestions: {len(questions)}"
    
    keyboard = [
        [InlineKeyboardButton(
            get_text('add_question', language),
            callback_data="admin_add_question"
        )],
        [InlineKeyboardButton(
            get_text('question_list', language),
            callback_data="admin_question_list"
        )],
        [InlineKeyboardButton(
            get_text('back', language),
            callback_data="admin_manage_exams"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)


async def admin_exam_step_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show exam management for a step."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    step_id = int(query.data.split('_')[-1])
    
    await show_exam_menu_for_step(update, context, step_id, language)
    return EXAM_MENU


async def admin_add_question_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding a new question."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    step_id = context.user_data.get('exam_step_id')
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data="cancel_add_question"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(get_text('enter_question_fa', language), reply_markup=reply_markup)
    return ADD_QUESTION_FA


async def admin_add_question_fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive question text in Farsi."""
    context.user_data['new_question_fa'] = update.message.text
    language = get_user_language(update.effective_user.id)
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data="cancel_add_question"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(get_text('enter_question_de', language), reply_markup=reply_markup)
    return ADD_QUESTION_DE


async def admin_add_question_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive question text in German."""
    context.user_data['new_question_de'] = update.message.text
    language = get_user_language(update.effective_user.id)
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data="cancel_add_question"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(get_text('enter_options', language), reply_markup=reply_markup)
    return ADD_QUESTION_OPTIONS


async def admin_add_question_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive question options."""
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    options = parse_options(update.message.text)
    
    if len(options) < 2:
        # Add cancel button to error message
        keyboard = [[InlineKeyboardButton(
            get_text('cancel', language),
            callback_data="cancel_add_question"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(get_text('invalid_input', language), reply_markup=reply_markup)
        return ADD_QUESTION_OPTIONS
    
    context.user_data['new_question_options'] = options
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data="cancel_add_question"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(get_text('enter_correct_option', language), reply_markup=reply_markup)
    return ADD_QUESTION_CORRECT


async def admin_add_question_correct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive correct option number."""
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    options = context.user_data.get('new_question_options', [])
    correct_option = validate_correct_option(update.message.text, len(options))
    
    if correct_option == -1:
        # Add cancel button to error message
        keyboard = [[InlineKeyboardButton(
            get_text('cancel', language),
            callback_data="cancel_add_question"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_reply_text(update.message, get_text('invalid_input', language), reply_markup=reply_markup)
        return ADD_QUESTION_CORRECT
    
    # Get exam for current step
    step_id = context.user_data.get('exam_step_id')
    if step_id is None:
        await safe_reply_text(update.message, get_text('error_occurred', language))
        return ConversationHandler.END
    
    exam = Exam.get_by_step_id(step_id)
    if not exam:
        exam_id = Exam.create(step_id)
        exam = Exam.get_by_step_id(step_id)
    
    # Create question
    question_json = {
        'fa': context.user_data.get('new_question_fa', ''),
        'de': context.user_data.get('new_question_de', '')
    }
    question_id = Question.create(
        exam_id=exam['id'],
        question_json=question_json,
        options_json=json.dumps(options),
        correct_option=correct_option
    )
    
    # Clear temp data
    context.user_data.pop('new_question_fa', None)
    context.user_data.pop('new_question_de', None)
    context.user_data.pop('new_question_options', None)
    
    await safe_reply_text(update.message, get_text('question_created', language))
    
    # Show question details with edit/delete buttons
    question = Question.get_by_id(question_id)
    if question:
        options_list = json.loads(question['options_json'])
        question_data = question.get('question_json', {})
        if isinstance(question_data, str):
            question_data = json.loads(question_data)
        text = f"<b>Question {question_id}</b>\n\n"
        text += f"<b>FA:</b> {question_data.get('fa', '')}\n"
        text += f"<b>DE:</b> {question_data.get('de', '')}\n\n"
        text += "<b>Options:</b>\n"
        for i, option in enumerate(options_list):
            marker = "✓" if i == question['correct_option'] else "○"
            text += f"{marker} {i+1}. {option}\n"
        
        keyboard = [
            [InlineKeyboardButton(
                get_text('edit_question', language),
                callback_data=f"admin_edit_question_{question_id}"
            )],
            [InlineKeyboardButton(
                get_text('delete_question', language),
                callback_data=f"admin_delete_question_{question_id}"
            )],
            [InlineKeyboardButton(
                get_text('back', language),
                callback_data="admin_question_list"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_reply_text(update.message, text, reply_markup=reply_markup, parse_mode='HTML')
    
    return ConversationHandler.END


async def admin_cancel_add_question_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel adding a new question."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    step_id = context.user_data.get('exam_step_id')
    
    # Clear temp data
    context.user_data.pop('new_question_fa', None)
    context.user_data.pop('new_question_de', None)
    context.user_data.pop('new_question_options', None)
    
    # Return to exam menu for the step
    if step_id:
        await show_exam_menu_for_step(update, context, step_id, language)
    else:
        await show_admin_menu(update, context)
    
    return ConversationHandler.END


async def admin_question_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of questions for current exam."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    step_id = context.user_data.get('exam_step_id')
    if step_id is None:
        await query.edit_message_text(get_text('error_occurred', language))
        return
    
    exam = Exam.get_by_step_id(step_id)
    
    if not exam:
        text = "No exam found."
        keyboard = [[InlineKeyboardButton(
            get_text('back', language),
            callback_data=f"admin_exam_step_{step_id}"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        return
    
    questions = Question.get_by_exam_id(exam['id'])
    
    if not questions:
        text = "No questions available."
        keyboard = [[InlineKeyboardButton(
            get_text('back', language),
            callback_data=f"admin_exam_step_{step_id}"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        return
    
    keyboard = []
    for i, question in enumerate(questions, 1):
        question_text = Question.get_text_by_language(question, language)
        keyboard.append([InlineKeyboardButton(
            f"Q{i}: {question_text[:50]}...",
            callback_data=f"admin_question_detail_{question['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        get_text('back', language),
        callback_data=f"admin_exam_step_{step_id}"
    )])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = get_text('question_list', language)
    await query.edit_message_text(text, reply_markup=reply_markup)


async def admin_question_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show question details and actions."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    question_id = int(query.data.split('_')[-1])
    question = Question.get_by_id(question_id)
    
    if not question:
        await query.edit_message_text(get_text('error_occurred', language))
        return
    
    options = json.loads(question['options_json'])
    question_json = question.get('question_json', {})
    if isinstance(question_json, str):
        question_json = json.loads(question_json)
    text = f"<b>Question {question_id}</b>\n\n"
    text += f"<b>FA:</b> {question_json.get('fa', '')}\n"
    text += f"<b>DE:</b> {question_json.get('de', '')}\n\n"
    text += "<b>Options:</b>\n"
    for i, option in enumerate(options):
        marker = "✓" if i == question['correct_option'] else "○"
        text += f"{marker} {i+1}. {option}\n"
    
    keyboard = [
        [InlineKeyboardButton(
            get_text('edit_question', language),
            callback_data=f"admin_edit_question_{question_id}"
        )],
        [InlineKeyboardButton(
            get_text('delete_question', language),
            callback_data=f"admin_delete_question_{question_id}"
        )],
        [InlineKeyboardButton(
            get_text('back', language),
            callback_data="admin_question_list"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')


async def admin_delete_question_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show confirmation dialog for deleting a question."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    question_id = int(query.data.split('_')[-1])
    
    # Show confirmation dialog
    text = get_text('confirm_delete_question', language)
    
    keyboard = [
        [InlineKeyboardButton(
            get_text('yes', language),
            callback_data=f"admin_confirm_delete_question_{question_id}"
        )],
        [InlineKeyboardButton(
            get_text('no', language),
            callback_data=f"admin_question_detail_{question_id}"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)


async def admin_confirm_delete_question_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and delete a question."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    question_id = int(query.data.split('_')[-1])
    
    Question.delete(question_id)
    await safe_answer_callback(query, get_text('question_deleted', language))
    
    # Go back to question list
    await admin_question_list_callback(update, context)


async def admin_cancel_edit_question_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel editing a question."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    question_id = int(query.data.split('_')[-1])
    
    # Clear temp data
    context.user_data.pop('editing_question_id', None)
    context.user_data.pop('edit_question_fa', None)
    context.user_data.pop('edit_question_de', None)
    context.user_data.pop('edit_question_options', None)
    context.user_data.pop('edit_question_correct', None)
    
    # Show question detail again
    question = Question.get_by_id(question_id)
    if question:
        options = json.loads(question['options_json'])
        question_json = question.get('question_json', {})
        if isinstance(question_json, str):
            question_json = json.loads(question_json)
        text = f"<b>Question {question_id}</b>\n\n"
        text += f"<b>FA:</b> {question_json.get('fa', '')}\n"
        text += f"<b>DE:</b> {question_json.get('de', '')}\n\n"
        text += "<b>Options:</b>\n"
        for i, option in enumerate(options):
            marker = "✓" if i == question['correct_option'] else "○"
            text += f"{marker} {i+1}. {option}\n"
        
        keyboard = [
            [InlineKeyboardButton(
                get_text('edit_question', language),
                callback_data=f"admin_edit_question_{question_id}"
            )],
            [InlineKeyboardButton(
                get_text('delete_question', language),
                callback_data=f"admin_delete_question_{question_id}"
            )],
            [InlineKeyboardButton(
                get_text('back', language),
                callback_data="admin_question_list"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    return ConversationHandler.END


async def admin_edit_question_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start editing a question."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    question_id = int(query.data.split('_')[-1])
    context.user_data['editing_question_id'] = question_id
    
    question = Question.get_by_id(question_id)
    if question:
        question_json = question.get('question_json', {})
        if isinstance(question_json, str):
            question_json = json.loads(question_json)
        context.user_data['edit_question_fa'] = question_json.get('fa', '')
        context.user_data['edit_question_de'] = question_json.get('de', '')
        context.user_data['edit_question_options'] = json.loads(question['options_json'])
        context.user_data['edit_question_correct'] = question['correct_option']
        
        # Show current value in prompt
        current_fa = question_json.get('fa', '')
        prompt_text = get_text('enter_question_fa', language)
        if current_fa:
            prompt_text += f"\n\n📝 مقدار فعلی:\n{current_fa}"
    else:
        prompt_text = get_text('enter_question_fa', language)
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data=f"cancel_edit_question_{question_id}"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(prompt_text, reply_markup=reply_markup)
    return EDIT_QUESTION_FA


async def admin_edit_question_fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive edited question text in Farsi."""
    context.user_data['edit_question_fa'] = update.message.text
    language = get_user_language(update.effective_user.id)
    question_id = context.user_data.get('editing_question_id')
    
    # Show current value in prompt
    current_de = context.user_data.get('edit_question_de', '')
    prompt_text = get_text('enter_question_de', language)
    if current_de:
        prompt_text += f"\n\n📝 مقدار فعلی:\n{current_de}"
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data=f"cancel_edit_question_{question_id}"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(prompt_text, reply_markup=reply_markup)
    return EDIT_QUESTION_DE


async def admin_edit_question_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive edited question text in German."""
    context.user_data['edit_question_de'] = update.message.text
    language = get_user_language(update.effective_user.id)
    question_id = context.user_data.get('editing_question_id')
    
    # Show current options in prompt
    current_options = context.user_data.get('edit_question_options', [])
    prompt_text = get_text('enter_options', language)
    if current_options:
        prompt_text += f"\n\n📝 گزینه‌های فعلی:\n"
        for i, opt in enumerate(current_options, 1):
            prompt_text += f"{i}. {opt}\n"
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data=f"cancel_edit_question_{question_id}"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(prompt_text, reply_markup=reply_markup)
    return EDIT_QUESTION_OPTIONS


async def admin_edit_question_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive edited question options."""
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    options = parse_options(update.message.text)
    
    if len(options) < 2:
        await update.message.reply_text(get_text('invalid_input', language))
        return EDIT_QUESTION_OPTIONS
    
    context.user_data['edit_question_options'] = options
    question_id = context.user_data.get('editing_question_id')
    
    # Show current correct option in prompt
    current_correct = context.user_data.get('edit_question_correct', -1)
    prompt_text = get_text('enter_correct_option', language)
    if current_correct >= 0:
        prompt_text += f"\n\n📝 گزینه صحیح فعلی: {current_correct + 1}"
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data=f"cancel_edit_question_{question_id}"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(prompt_text, reply_markup=reply_markup)
    return EDIT_QUESTION_CORRECT


async def admin_edit_question_correct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive edited correct option number."""
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    options = context.user_data.get('edit_question_options', [])
    correct_option = validate_correct_option(update.message.text, len(options))
    
    if correct_option == -1:
        await update.message.reply_text(get_text('invalid_input', language))
        return EDIT_QUESTION_CORRECT
    
    question_id = context.user_data.get('editing_question_id')
    question_json = {
        'fa': context.user_data.get('edit_question_fa', ''),
        'de': context.user_data.get('edit_question_de', '')
    }
    Question.update(
        question_id=question_id,
        question_json=question_json,
        options_json=json.dumps(options),
        correct_option=correct_option
    )
    
    # Clear temp data
    context.user_data.pop('editing_question_id', None)
    context.user_data.pop('edit_question_fa', None)
    context.user_data.pop('edit_question_de', None)
    context.user_data.pop('edit_question_options', None)
    context.user_data.pop('edit_question_correct', None)
    
    await update.message.reply_text(get_text('question_updated', language))
    
    # Show question details with edit/delete buttons
    question = Question.get_by_id(question_id)
    if question:
        options_list = json.loads(question['options_json'])
        question_data = question.get('question_json', {})
        if isinstance(question_data, str):
            question_data = json.loads(question_data)
        text = f"<b>Question {question_id}</b>\n\n"
        text += f"<b>FA:</b> {question_data.get('fa', '')}\n"
        text += f"<b>DE:</b> {question_data.get('de', '')}\n\n"
        text += "<b>Options:</b>\n"
        for i, option in enumerate(options_list):
            marker = "✓" if i == question['correct_option'] else "○"
            text += f"{marker} {i+1}. {option}\n"
        
        keyboard = [
            [InlineKeyboardButton(
                get_text('edit_question', language),
                callback_data=f"admin_edit_question_{question_id}"
            )],
            [InlineKeyboardButton(
                get_text('delete_question', language),
                callback_data=f"admin_delete_question_{question_id}"
            )],
            [InlineKeyboardButton(
                get_text('back', language),
                callback_data="admin_question_list"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    return ConversationHandler.END


async def admin_statistics_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    steps = Step.get_all_active()
    
    text = get_text('statistics', language)
    for step in steps:
        count = Step.get_user_count(step['id'])
        text += format_text('step_users_count', language, step_id=step['id'], count=count) + "\n"
    
    keyboard = [[InlineKeyboardButton(
        get_text('back', language),
        callback_data="admin_menu"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)


async def admin_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin menu callback."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    await show_admin_menu(update, context)


# User management callbacks
async def admin_manage_users_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle manage users callback."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    
    # Get all users
    users = User.get_all()
    
    if not users:
        text = get_text('no_users', language)
        keyboard = [[InlineKeyboardButton(
            get_text('back', language),
            callback_data="admin_menu"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        return
    
    # Display users list (paginated if needed)
    text = get_text('users_list', language) + "\n\n"
    
    # Show first 10 users
    for i, user in enumerate(users[:10], 1):
        name = user.get('name') or get_text('no_name', language)
        mobile = user.get('mobile') or get_text('no_mobile', language)
        text += f"{i}. {name} - {mobile}\n"
        text += f"   ID: {user['id']} | Telegram ID: {user['telegram_id']}\n\n"
    
    if len(users) > 10:
        text += f"\n{format_text('showing_first', language, count=10, total=len(users))}"
    
    keyboard = []
    # Add buttons for each user (first 10)
    for i, user in enumerate(users[:10], 1):
        name = user.get('name') or f"User {user['id']}"
        keyboard.append([InlineKeyboardButton(
            f"{i}. {name}",
            callback_data=f"admin_user_detail_{user['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        get_text('back', language),
        callback_data="admin_menu"
    )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)
    
    return MANAGE_USERS


async def admin_user_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user detail callback."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    user_id = int(query.data.split('_')[-1])
    
    user = User.get_by_id(user_id)
    if not user:
        await query.edit_message_text(get_text('user_not_found', language))
        return
    
    name = user.get('name') or get_text('no_name', language)
    mobile = user.get('mobile') or get_text('no_mobile', language)
    lang = user.get('language') or get_text('no_language', language)
    
    text = get_text('user_details', language) + "\n\n"
    text += f"{get_text('name', language)}: {name}\n"
    text += f"{get_text('mobile', language)}: {mobile}\n"
    text += f"{get_text('language', language)}: {lang}\n"
    text += f"{get_text('current_step', language)}: {user.get('current_step', 1)}\n"
    text += f"Telegram ID: {user['telegram_id']}\n"
    text += f"{get_text('created_at', language)}: {user.get('created_at', 'N/A')}\n"
    
    keyboard = [
        [InlineKeyboardButton(
            get_text('edit_user', language),
            callback_data=f"admin_edit_user_{user_id}"
        )],
        [InlineKeyboardButton(
            get_text('delete_user', language),
            callback_data=f"admin_delete_user_{user_id}"
        )],
        [InlineKeyboardButton(
            get_text('back', language),
            callback_data="admin_manage_users"
        )]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)


async def admin_edit_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle edit user callback."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    user_id = int(query.data.split('_')[-1])
    
    user = User.get_by_id(user_id)
    if not user:
        await query.edit_message_text(get_text('user_not_found', language))
        return ConversationHandler.END
    
    # Store user_id in context
    context.user_data['editing_user_id'] = user_id
    
    keyboard = [
        [InlineKeyboardButton(
            get_text('edit_name', language),
            callback_data=f"admin_edit_user_name_{user_id}"
        )],
        [InlineKeyboardButton(
            get_text('edit_mobile', language),
            callback_data=f"admin_edit_user_mobile_{user_id}"
        )],
        [InlineKeyboardButton(
            get_text('back', language),
            callback_data=f"admin_user_detail_{user_id}"
        )]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = get_text('edit_user_menu', language)
    await query.edit_message_text(text, reply_markup=reply_markup)
    
    return MANAGE_USERS


async def admin_edit_user_name_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start editing user name."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    user_id = int(query.data.split('_')[-1])
    
    context.user_data['editing_user_id'] = user_id
    context.user_data['editing_field'] = 'name'
    
    await query.edit_message_text(get_text('enter_new_name', language))
    return EDIT_USER_NAME


async def admin_edit_user_mobile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start editing user mobile."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    user_id = int(query.data.split('_')[-1])
    
    context.user_data['editing_user_id'] = user_id
    context.user_data['editing_field'] = 'mobile'
    
    await query.edit_message_text(get_text('enter_new_mobile', language))
    return EDIT_USER_MOBILE


async def admin_save_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save edited user name."""
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    user_id = context.user_data.get('editing_user_id')
    
    if not user_id:
        await update.message.reply_text(get_text('error_occurred', language))
        return ConversationHandler.END
    
    name = update.message.text.strip()
    if not name or len(name) < 2:
        await update.message.reply_text(get_text('invalid_name', language))
        return EDIT_USER_NAME
    
    # Get user by id to get telegram_id
    user = User.get_by_id(user_id)
    if user:
        User.update_name(user['telegram_id'], name)
        await update.message.reply_text(get_text('user_updated', language))
        
        # Show user detail
        user = User.get_by_id(user_id)
        name_display = user.get('name') or get_text('no_name', language)
        mobile = user.get('mobile') or get_text('no_mobile', language)
        lang = user.get('language') or get_text('no_language', language)
        
        text = get_text('user_details', language) + "\n\n"
        text += f"{get_text('name', language)}: {name_display}\n"
        text += f"{get_text('mobile', language)}: {mobile}\n"
        text += f"{get_text('language', language)}: {lang}\n"
        text += f"{get_text('current_step', language)}: {user.get('current_step', 1)}\n"
        text += f"Telegram ID: {user['telegram_id']}\n"
        text += f"{get_text('created_at', language)}: {user.get('created_at', 'N/A')}\n"
        
        keyboard = [
            [InlineKeyboardButton(
                get_text('edit_user', language),
                callback_data=f"admin_edit_user_{user_id}"
            )],
            [InlineKeyboardButton(
                get_text('delete_user', language),
                callback_data=f"admin_delete_user_{user_id}"
            )],
            [InlineKeyboardButton(
                get_text('back', language),
                callback_data="admin_manage_users"
            )]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    return ConversationHandler.END


async def admin_save_user_mobile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save edited user mobile."""
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    user_id = context.user_data.get('editing_user_id')
    
    if not user_id:
        await update.message.reply_text(get_text('error_occurred', language))
        return ConversationHandler.END
    
    mobile = update.message.text.strip()
    mobile_clean = ''.join(filter(str.isdigit, mobile))
    if not mobile_clean or len(mobile_clean) < 10:
        await update.message.reply_text(get_text('invalid_mobile', language))
        return EDIT_USER_MOBILE
    
    # Get user by id to get telegram_id
    user = User.get_by_id(user_id)
    if user:
        User.update_mobile(user['telegram_id'], mobile_clean)
        await update.message.reply_text(get_text('user_updated', language))
        
        # Show user detail
        user = User.get_by_id(user_id)
        name = user.get('name') or get_text('no_name', language)
        mobile_display = user.get('mobile') or get_text('no_mobile', language)
        lang = user.get('language') or get_text('no_language', language)
        
        text = get_text('user_details', language) + "\n\n"
        text += f"{get_text('name', language)}: {name}\n"
        text += f"{get_text('mobile', language)}: {mobile_display}\n"
        text += f"{get_text('language', language)}: {lang}\n"
        text += f"{get_text('current_step', language)}: {user.get('current_step', 1)}\n"
        text += f"Telegram ID: {user['telegram_id']}\n"
        text += f"{get_text('created_at', language)}: {user.get('created_at', 'N/A')}\n"
        
        keyboard = [
            [InlineKeyboardButton(
                get_text('edit_user', language),
                callback_data=f"admin_edit_user_{user_id}"
            )],
            [InlineKeyboardButton(
                get_text('delete_user', language),
                callback_data=f"admin_delete_user_{user_id}"
            )],
            [InlineKeyboardButton(
                get_text('back', language),
                callback_data="admin_manage_users"
            )]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    return ConversationHandler.END


async def admin_delete_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle delete user callback - show confirmation."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    user_id = int(query.data.split('_')[-1])
    
    user = User.get_by_id(user_id)
    if not user:
        await query.edit_message_text(get_text('user_not_found', language))
        return
    
    name = user.get('name') or f"User {user_id}"
    text = format_text('confirm_delete_user', language, name=name)
    
    keyboard = [
        [InlineKeyboardButton(
            get_text('yes', language),
            callback_data=f"admin_confirm_delete_user_{user_id}"
        )],
        [InlineKeyboardButton(
            get_text('no', language),
            callback_data=f"admin_user_detail_{user_id}"
        )]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)


async def admin_confirm_delete_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirm delete user callback."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    user_id = int(query.data.split('_')[-1])
    
    User.delete(user_id)
    
    await query.edit_message_text(get_text('user_deleted', language))
    
    # Return to users list
    keyboard = [[InlineKeyboardButton(
        get_text('back', language),
        callback_data="admin_manage_users"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        get_text('user_deleted', language),
        reply_markup=reply_markup
    )
    return ADMIN_MENU


# Section management callbacks
async def admin_manage_sections_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle manage sections callback."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    
    keyboard = [
        [InlineKeyboardButton(
            get_text('add_section', language),
            callback_data="admin_add_section"
        )],
        [InlineKeyboardButton(
            get_text('section_list', language),
            callback_data="admin_section_list"
        )],
        [InlineKeyboardButton(
            get_text('add_lesson_to_section', language),
            callback_data="admin_add_lesson_to_section"
        )],
        [InlineKeyboardButton(
            get_text('back', language),
            callback_data="admin_menu"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = get_text('manage_sections', language)
    await query.edit_message_text(text, reply_markup=reply_markup)
    
    return MANAGE_SECTIONS


async def admin_add_section_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding a new section."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    languages = get_available_languages()
    
    # Clear any previous data
    context.user_data.pop('new_section_title_json', None)
    context.user_data.pop('new_section_desc_json', None)
    
    # Initialize title_json with empty strings for all languages
    context.user_data['new_section_title_json'] = {lang['code']: '' for lang in languages}
    context.user_data['new_section_desc_json'] = {lang['code']: '' for lang in languages}
    
    # Start with first language (usually 'fa')
    first_lang = languages[0]['code'] if languages else 'fa'
    text = format_text('enter_title', language, lang=first_lang.upper())
    
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data="admin_menu"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)
    
    return ADD_SECTION_TITLE_FA if first_lang == 'fa' else ADD_SECTION_TITLE_DE


async def admin_add_another_section_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding another section (same as add_section)."""
    return await admin_add_section_callback(update, context)


async def admin_add_section_title_fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle section title in Persian."""
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    title_fa = update.message.text.strip()
    
    context.user_data['new_section_title_json']['fa'] = title_fa
    
    text = get_text('enter_title_de', language)
    await update.message.reply_text(text)
    
    return ADD_SECTION_TITLE_DE


async def admin_add_section_title_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle section title in German."""
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    title_de = update.message.text.strip()
    
    context.user_data['new_section_title_json']['de'] = title_de
    
    text = get_text('enter_description_fa', language)
    await update.message.reply_text(text)
    
    return ADD_SECTION_DESC_FA


async def admin_add_section_desc_fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle section description in Persian."""
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    desc_fa = update.message.text.strip()
    
    context.user_data['new_section_desc_json']['fa'] = desc_fa
    
    text = get_text('enter_description_de', language)
    await update.message.reply_text(text)
    
    return ADD_SECTION_DESC_DE


async def admin_add_section_desc_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle section description in German and create section."""
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    desc_de = update.message.text.strip()
    
    context.user_data['new_section_desc_json']['de'] = desc_de
    
    # Create section
    title_json = context.user_data.get('new_section_title_json', {})
    desc_json = context.user_data.get('new_section_desc_json', {})
    
    section_id = Section.create(
        title_json=title_json,
        description_json=desc_json
    )
    
    # Clear temp data
    context.user_data.pop('new_section_title_json', None)
    context.user_data.pop('new_section_desc_json', None)
    
    text = get_text('section_created', language)
    keyboard = [
        [InlineKeyboardButton(
            get_text('add_lesson_to_section', language),
            callback_data=f"admin_add_lesson_section_{section_id}"
        )],
        [InlineKeyboardButton(
            get_text('add_another_section', language),
            callback_data="admin_add_section"
        )],
        [InlineKeyboardButton(
            get_text('back', language),
            callback_data="admin_manage_sections"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
    
    return ConversationHandler.END


async def admin_section_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of sections."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    
    sections = Section.get_all_active()
    
    if not sections:
        text = get_text('no_sections_available', language)
        keyboard = [[InlineKeyboardButton(
            get_text('back', language),
            callback_data="admin_manage_sections"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        return
    
    text = get_text('section_list', language) + "\n\n"
    keyboard = []
    
    for section in sections:
        title = Section.get_text_by_language(section, 'title_json', language)
        section_id = section['id']
        lessons = Lesson.get_by_section_id(section_id)
        lessons_count = len(lessons)
        
        text += f"{section['order_number']}. {title} ({lessons_count} درس)\n"
        
        keyboard.append([InlineKeyboardButton(
            f"{section['order_number']}. {title}",
            callback_data=f"admin_section_detail_{section_id}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        get_text('back', language),
        callback_data="admin_manage_sections"
    )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)


async def admin_section_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show section details."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    section_id = int(query.data.split('_')[-1])
    
    section = Section.get_by_id(section_id)
    if not section:
        await query.edit_message_text(get_text('section_not_found', language))
        return
    
    title_fa = Section.get_text_by_language(section, 'title_json', 'fa')
    title_de = Section.get_text_by_language(section, 'title_json', 'de')
    desc_fa = Section.get_text_by_language(section, 'description_json', 'fa')
    desc_de = Section.get_text_by_language(section, 'description_json', 'de')
    
    lessons = Lesson.get_by_section_id(section_id)
    
    text = format_text('section_details', language, section_id=section['order_number'])
    text += f"\n\n<b>FA:</b> {title_fa}\n"
    text += f"<b>DE:</b> {title_de}\n"
    if desc_fa:
        text += f"\n<b>توضیحات FA:</b> {desc_fa}\n"
    if desc_de:
        text += f"<b>توضیحات DE:</b> {desc_de}\n"
    text += f"<b>Active:</b> {'Yes' if section['is_active'] else 'No'}\n"
    text += f"<b>Lessons:</b> {len(lessons)}"
    
    keyboard = [
        [InlineKeyboardButton(
            get_text('edit_section', language),
            callback_data=f"admin_edit_section_{section_id}"
        )],
        [InlineKeyboardButton(
            get_text('add_lesson_to_section', language),
            callback_data=f"admin_add_lesson_section_{section_id}"
        )],
        [InlineKeyboardButton(
            get_text('delete_section', language),
            callback_data=f"admin_delete_section_{section_id}"
        )],
        [InlineKeyboardButton(
            get_text('back', language),
            callback_data="admin_section_list"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')


async def admin_edit_section_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start editing a section."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    section_id = int(query.data.split('_')[-1])
    context.user_data['editing_section_id'] = section_id
    
    section = Section.get_by_id(section_id)
    if not section:
        await query.edit_message_text(get_text('section_not_found', language))
        return ConversationHandler.END
    
    # Parse JSON fields (i18n-ready)
    title_json = section.get('title_json', {})
    if isinstance(title_json, str):
        title_json = json.loads(title_json)
    description_json = section.get('description_json', {})
    if isinstance(description_json, str):
        description_json = json.loads(description_json)
    
    context.user_data['edit_section_title_fa'] = title_json.get('fa', '')
    context.user_data['edit_section_title_de'] = title_json.get('de', '')
    context.user_data['edit_section_desc_fa'] = description_json.get('fa', '')
    context.user_data['edit_section_desc_de'] = description_json.get('de', '')
    
    # Show current value in prompt
    current_fa = title_json.get('fa', '')
    prompt_text = get_text('enter_title_fa', language)
    if current_fa:
        prompt_text += f"\n\n📝 مقدار فعلی:\n{current_fa}"
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data=f"cancel_edit_section_{section_id}"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(prompt_text, reply_markup=reply_markup)
    return EDIT_SECTION_TITLE_FA


async def admin_edit_section_title_fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive edited section title in Farsi."""
    context.user_data['edit_section_title_fa'] = update.message.text
    language = get_user_language(update.effective_user.id)
    section_id = context.user_data.get('editing_section_id')
    
    # Show current value in prompt
    current_de = context.user_data.get('edit_section_title_de', '')
    prompt_text = get_text('enter_title_de', language)
    if current_de:
        prompt_text += f"\n\n📝 مقدار فعلی:\n{current_de}"
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data=f"cancel_edit_section_{section_id}"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(prompt_text, reply_markup=reply_markup)
    return EDIT_SECTION_TITLE_DE


async def admin_edit_section_title_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive edited section title in German."""
    context.user_data['edit_section_title_de'] = update.message.text
    language = get_user_language(update.effective_user.id)
    section_id = context.user_data.get('editing_section_id')
    
    # Show current value in prompt
    current_fa = context.user_data.get('edit_section_desc_fa', '')
    prompt_text = get_text('enter_description_fa', language)
    if current_fa:
        prompt_text += f"\n\n📝 مقدار فعلی:\n{current_fa}"
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data=f"cancel_edit_section_{section_id}"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(prompt_text, reply_markup=reply_markup)
    return EDIT_SECTION_DESC_FA


async def admin_edit_section_desc_fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive edited section description in Farsi."""
    context.user_data['edit_section_desc_fa'] = update.message.text
    language = get_user_language(update.effective_user.id)
    section_id = context.user_data.get('editing_section_id')
    
    # Show current value in prompt
    current_de = context.user_data.get('edit_section_desc_de', '')
    prompt_text = get_text('enter_description_de', language)
    if current_de:
        prompt_text += f"\n\n📝 مقدار فعلی:\n{current_de}"
    
    # Add cancel button
    keyboard = [[InlineKeyboardButton(
        get_text('cancel', language),
        callback_data=f"cancel_edit_section_{section_id}"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(prompt_text, reply_markup=reply_markup)
    return EDIT_SECTION_DESC_DE


async def admin_edit_section_desc_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive edited section description in German and save."""
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    
    section_id = context.user_data.get('editing_section_id')
    if not section_id:
        await update.message.reply_text(get_text('error_occurred', language))
        return ConversationHandler.END
    
    context.user_data['edit_section_desc_de'] = update.message.text
    
    # Build multilingual content from collected data
    title_json = {
        'fa': context.user_data.get('edit_section_title_fa', ''),
        'de': context.user_data.get('edit_section_title_de', '')
    }
    description_json = {
        'fa': context.user_data.get('edit_section_desc_fa', ''),
        'de': context.user_data.get('edit_section_desc_de', '')
    }
    
    # Update section
    Section.update(
        section_id=section_id,
        title_json=title_json,
        description_json=description_json
    )
    
    # Clear temp data
    context.user_data.pop('editing_section_id', None)
    context.user_data.pop('edit_section_title_fa', None)
    context.user_data.pop('edit_section_title_de', None)
    context.user_data.pop('edit_section_desc_fa', None)
    context.user_data.pop('edit_section_desc_de', None)
    
    await update.message.reply_text(get_text('section_updated', language))
    
    # Show section detail again
    section = Section.get_by_id(section_id)
    if section:
        title_fa = Section.get_text_by_language(section, 'title_json', 'fa')
        title_de = Section.get_text_by_language(section, 'title_json', 'de')
        desc_fa = Section.get_text_by_language(section, 'description_json', 'fa')
        desc_de = Section.get_text_by_language(section, 'description_json', 'de')
        
        lessons = Lesson.get_by_section_id(section_id)
        
        text = format_text('section_details', language, section_id=section['order_number'])
        text += f"\n\n<b>FA:</b> {title_fa}\n"
        text += f"<b>DE:</b> {title_de}\n"
        if desc_fa:
            text += f"\n<b>توضیحات FA:</b> {desc_fa}\n"
        if desc_de:
            text += f"<b>توضیحات DE:</b> {desc_de}\n"
        text += f"<b>Active:</b> {'Yes' if section['is_active'] else 'No'}\n"
        text += f"<b>Lessons:</b> {len(lessons)}"
        
        keyboard = [
            [InlineKeyboardButton(
                get_text('edit_section', language),
                callback_data=f"admin_edit_section_{section_id}"
            )],
            [InlineKeyboardButton(
                get_text('add_lesson_to_section', language),
                callback_data=f"admin_add_lesson_section_{section_id}"
            )],
            [InlineKeyboardButton(
                get_text('delete_section', language),
                callback_data=f"admin_delete_section_{section_id}"
            )],
            [InlineKeyboardButton(
                get_text('back', language),
                callback_data="admin_section_list"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    return ConversationHandler.END


async def admin_cancel_edit_section_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel editing a section."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return ConversationHandler.END
    
    language = get_user_language(telegram_id)
    section_id = int(query.data.split('_')[-1])
    
    # Clear temp data
    context.user_data.pop('editing_section_id', None)
    context.user_data.pop('edit_section_title_fa', None)
    context.user_data.pop('edit_section_title_de', None)
    context.user_data.pop('edit_section_desc_fa', None)
    context.user_data.pop('edit_section_desc_de', None)
    
    # Show section detail again
    section = Section.get_by_id(section_id)
    if section:
        title_fa = Section.get_text_by_language(section, 'title_json', 'fa')
        title_de = Section.get_text_by_language(section, 'title_json', 'de')
        desc_fa = Section.get_text_by_language(section, 'description_json', 'fa')
        desc_de = Section.get_text_by_language(section, 'description_json', 'de')
        
        lessons = Lesson.get_by_section_id(section_id)
        
        text = format_text('section_details', language, section_id=section['order_number'])
        text += f"\n\n<b>FA:</b> {title_fa}\n"
        text += f"<b>DE:</b> {title_de}\n"
        if desc_fa:
            text += f"\n<b>توضیحات FA:</b> {desc_fa}\n"
        if desc_de:
            text += f"<b>توضیحات DE:</b> {desc_de}\n"
        text += f"<b>Active:</b> {'Yes' if section['is_active'] else 'No'}\n"
        text += f"<b>Lessons:</b> {len(lessons)}"
        
        keyboard = [
            [InlineKeyboardButton(
                get_text('edit_section', language),
                callback_data=f"admin_edit_section_{section_id}"
            )],
            [InlineKeyboardButton(
                get_text('add_lesson_to_section', language),
                callback_data=f"admin_add_lesson_section_{section_id}"
            )],
            [InlineKeyboardButton(
                get_text('delete_section', language),
                callback_data=f"admin_delete_section_{section_id}"
            )],
            [InlineKeyboardButton(
                get_text('back', language),
                callback_data="admin_section_list"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    return ConversationHandler.END


async def admin_delete_section_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle delete section callback."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    section_id = int(query.data.split('_')[-1])
    
    section = Section.get_by_id(section_id)
    if not section:
        await query.edit_message_text(get_text('section_not_found', language))
        return
    
    title = Section.get_text_by_language(section, 'title_json', language)
    text = format_text('confirm_delete_section', language, title=title)
    
    keyboard = [
        [InlineKeyboardButton(
            get_text('yes', language),
            callback_data=f"admin_confirm_delete_section_{section_id}"
        )],
        [InlineKeyboardButton(
            get_text('no', language),
            callback_data=f"admin_section_detail_{section_id}"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)


async def admin_confirm_delete_section_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirm delete section callback."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    section_id = int(query.data.split('_')[-1])
    
    Section.delete(section_id)
    
    await safe_answer_callback(query, get_text('section_deleted', language))
    
    # Return to sections list
    await admin_section_list_callback(update, context)


async def admin_add_lesson_to_section_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show sections to select for adding lesson."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    
    sections = Section.get_all_active()
    
    if not sections:
        text = get_text('no_sections_available', language)
        keyboard = [[InlineKeyboardButton(
            get_text('back', language),
            callback_data="admin_manage_sections"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        return
    
    text = get_text('select_section_for_lesson', language)
    keyboard = []
    
    for section in sections:
        title = Section.get_text_by_language(section, 'title_json', language)
        keyboard.append([InlineKeyboardButton(
            title,
            callback_data=f"admin_add_lesson_section_{section['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        get_text('back', language),
        callback_data="admin_manage_sections"
    )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)


async def admin_add_lesson_section_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show steps to select for adding as lesson to section."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    section_id = int(query.data.split('_')[-1])
    
    context.user_data['adding_lesson_section_id'] = section_id
    
    section = Section.get_by_id(section_id)
    if not section:
        await query.edit_message_text(get_text('section_not_found', language))
        return
    
    # Get all active steps
    steps = Step.get_all_active()
    
    if not steps:
        text = get_text('no_steps_available', language)
        keyboard = [[InlineKeyboardButton(
            get_text('back', language),
            callback_data="admin_add_lesson_to_section"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        return
    
    # Get existing lessons for this section to exclude already added steps
    existing_lessons = Lesson.get_by_section_id(section_id)
    existing_step_ids = {lesson['step_id'] for lesson in existing_lessons}
    
    # Filter out steps that are already in this section
    available_steps = [step for step in steps if step['id'] not in existing_step_ids]
    
    if not available_steps:
        text = get_text('all_steps_added', language)
        keyboard = [[InlineKeyboardButton(
            get_text('back', language),
            callback_data="admin_section_detail_{}".format(section_id)
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        return
    
    section_title = Section.get_text_by_language(section, 'title_json', language)
    text = format_text('select_step_for_lesson', language, section_title=section_title)
    
    keyboard = []
    for step in available_steps[:20]:  # Limit to 20 steps per page
        step_title = Step.get_text_by_language(step, 'title_json', language)
        keyboard.append([InlineKeyboardButton(
            step_title,
            callback_data=f"admin_confirm_add_lesson_{step['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        get_text('back', language),
        callback_data=f"admin_section_detail_{section_id}"
    )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)


async def admin_confirm_add_lesson_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and add lesson to section."""
    query = update.callback_query
    await safe_answer_callback(query)
    
    telegram_id = query.from_user.id
    if not is_admin(telegram_id):
        return
    
    language = get_user_language(telegram_id)
    step_id = int(query.data.split('_')[-1])
    section_id = context.user_data.get('adding_lesson_section_id')
    
    if not section_id:
        await query.edit_message_text(get_text('error_occurred', language))
        return
    
    # Check if lesson already exists
    existing_lessons = Lesson.get_by_section_id(section_id)
    if any(lesson['step_id'] == step_id for lesson in existing_lessons):
        text = get_text('lesson_already_exists', language)
        keyboard = [[InlineKeyboardButton(
            get_text('back', language),
            callback_data=f"admin_section_detail_{section_id}"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        return
    
    # Create lesson
    Lesson.create(section_id=section_id, step_id=step_id)
    
    # Clear temp data
    context.user_data.pop('adding_lesson_section_id', None)
    
    text = get_text('lesson_added', language)
    keyboard = [
        [InlineKeyboardButton(
            get_text('add_another_lesson', language),
            callback_data=f"admin_add_lesson_section_{section_id}"
        )],
        [InlineKeyboardButton(
            get_text('back', language),
            callback_data=f"admin_section_detail_{section_id}"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)
