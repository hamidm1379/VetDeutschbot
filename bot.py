"""
Main bot entry point.
Production-ready Telegram bot for language learning.
"""
import asyncio
import logging
from telegram import Update
from telegram.error import NetworkError
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
from config import Config
from handlers import user_handlers, admin_handlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Start the bot."""
    # Validate configuration
    if not Config.validate():
        logger.error("BOT_TOKEN not found in environment variables!")
        logger.error("Please check your .env file and ensure BOT_TOKEN is set.")
        return
    
    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # User handlers
    # Language selection conversation
    language_conv = ConversationHandler(
        entry_points=[CommandHandler('start', user_handlers.start_command)],
        states={
            user_handlers.SELECTING_LANGUAGE: [
                CallbackQueryHandler(
                    user_handlers.language_callback,
                    pattern='^lang_[a-z]{2,10}$'  # Dynamic language codes
                )
            ]
        },
        fallbacks=[],
        name="language_selection"
    )
    
    # User callbacks
    user_callbacks = [
        CallbackQueryHandler(
            user_handlers.start_learning_callback,
            pattern='^start_learning$'
        ),
        CallbackQueryHandler(
            user_handlers.my_profile_callback,
            pattern='^my_profile$'
        ),
        CallbackQueryHandler(
            user_handlers.change_language_callback,
            pattern='^change_language$'
        ),
        CallbackQueryHandler(
            user_handlers.language_callback,
            pattern='^lang_[a-z]{2,10}$'  # Dynamic language codes (for change language menu)
        ),
        CallbackQueryHandler(
            user_handlers.show_step_callback,
            pattern=r'^show_step_\d+$'
        ),
        CallbackQueryHandler(
            user_handlers.show_section_callback,
            pattern=r'^show_section_\d+$'
        ),
        CallbackQueryHandler(
            user_handlers.show_lesson_callback,
            pattern=r'^show_lesson_\d+$'
        ),
        CallbackQueryHandler(
            user_handlers.section_locked_callback,
            pattern=r'^section_locked_\d+$'
        ),
        CallbackQueryHandler(
            user_handlers.lesson_locked_callback,
            pattern=r'^lesson_locked_\d+$'
        ),
        CallbackQueryHandler(
            user_handlers.start_exam_callback,
            pattern=r'^start_exam_\d+$'
        ),
        CallbackQueryHandler(
            user_handlers.exam_answer_callback,
            pattern=r'^exam_answer_\d+_\d+$'
        ),
        CallbackQueryHandler(
            user_handlers.cancel_exam_callback,
            pattern='^cancel_exam$'
        ),
        CallbackQueryHandler(
            user_handlers.main_menu_callback,
            pattern='^main_menu$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_panel_callback,
            pattern='^admin_panel$'
        )
    ]
    
    # Admin handlers
    # Admin conversation for step management
    admin_step_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                admin_handlers.admin_add_step_callback,
                pattern='^admin_add_step$'
            ),
            CallbackQueryHandler(
                admin_handlers.admin_add_another_step_callback,
                pattern='^admin_add_another_step$'
            ),
            CallbackQueryHandler(
                admin_handlers.admin_edit_step_callback,
                pattern=r'^admin_edit_step_\d+$'
            )
        ],
        states={
            admin_handlers.ADD_STEP_TITLE_FA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_add_step_title_fa)
            ],
            admin_handlers.ADD_STEP_TITLE_DE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_add_step_title_de)
            ],
            admin_handlers.ADD_STEP_DESC_FA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_add_step_desc_fa)
            ],
            admin_handlers.ADD_STEP_DESC_DE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_add_step_desc_de)
            ],
            admin_handlers.ADD_STEP_FILE: [
                MessageHandler(
                    filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.VOICE,
                    admin_handlers.admin_add_step_file
                )
            ],
            admin_handlers.EDIT_STEP_TITLE_FA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_edit_step_title_fa)
            ],
            admin_handlers.EDIT_STEP_TITLE_DE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_edit_step_title_de)
            ],
            admin_handlers.EDIT_STEP_DESC_FA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_edit_step_desc_fa)
            ],
            admin_handlers.EDIT_STEP_DESC_DE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_edit_step_desc_de)
            ],
            admin_handlers.EDIT_STEP_FILE: [
                MessageHandler(
                    filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.VOICE | filters.TEXT & ~filters.COMMAND,
                    admin_handlers.admin_edit_step_file
                )
            ],
        },
        fallbacks=[
            CallbackQueryHandler(admin_handlers.admin_menu_callback, pattern='^admin_menu$'),
            CallbackQueryHandler(admin_handlers.admin_cancel_edit_step_callback, pattern=r'^cancel_edit_step_\d+$')
        ],
        name="admin_step_management"
    )
    
    # Admin conversation for exam/question management
    admin_exam_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                admin_handlers.admin_add_question_callback,
                pattern='^admin_add_question$'
            ),
            CallbackQueryHandler(
                admin_handlers.admin_edit_question_callback,
                pattern=r'^admin_edit_question_\d+$'
            )
        ],
        states={
            admin_handlers.ADD_QUESTION_FA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_add_question_fa)
            ],
            admin_handlers.ADD_QUESTION_DE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_add_question_de)
            ],
            admin_handlers.ADD_QUESTION_OPTIONS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_add_question_options)
            ],
            admin_handlers.ADD_QUESTION_CORRECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_add_question_correct)
            ],
            admin_handlers.EDIT_QUESTION_FA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_edit_question_fa)
            ],
            admin_handlers.EDIT_QUESTION_DE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_edit_question_de)
            ],
            admin_handlers.EDIT_QUESTION_OPTIONS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_edit_question_options)
            ],
            admin_handlers.EDIT_QUESTION_CORRECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_edit_question_correct)
            ],
        },
        fallbacks=[
            CallbackQueryHandler(admin_handlers.admin_menu_callback, pattern='^admin_menu$'),
            CallbackQueryHandler(admin_handlers.admin_cancel_edit_question_callback, pattern=r'^cancel_edit_question_\d+$'),
            CallbackQueryHandler(admin_handlers.admin_cancel_add_question_callback, pattern='^cancel_add_question$')
        ],
        name="admin_exam_management"
    )
    
    # Admin conversation for user management
    admin_user_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                admin_handlers.admin_edit_user_name_callback,
                pattern=r'^admin_edit_user_name_\d+$'
            ),
            CallbackQueryHandler(
                admin_handlers.admin_edit_user_mobile_callback,
                pattern=r'^admin_edit_user_mobile_\d+$'
            )
        ],
        states={
            admin_handlers.EDIT_USER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_save_user_name)
            ],
            admin_handlers.EDIT_USER_MOBILE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_save_user_mobile)
            ],
        },
        fallbacks=[CallbackQueryHandler(admin_handlers.admin_menu_callback, pattern='^admin_menu$')],
        name="admin_user_management"
    )
    
    # Admin conversation for section management
    admin_section_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                admin_handlers.admin_add_section_callback,
                pattern='^admin_add_section$'
            ),
            CallbackQueryHandler(
                admin_handlers.admin_add_another_section_callback,
                pattern='^admin_add_another_section$'
            ),
            CallbackQueryHandler(
                admin_handlers.admin_edit_section_callback,
                pattern=r'^admin_edit_section_\d+$'
            )
        ],
        states={
            admin_handlers.ADD_SECTION_TITLE_FA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_add_section_title_fa)
            ],
            admin_handlers.ADD_SECTION_TITLE_DE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_add_section_title_de)
            ],
            admin_handlers.ADD_SECTION_DESC_FA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_add_section_desc_fa)
            ],
            admin_handlers.ADD_SECTION_DESC_DE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_add_section_desc_de)
            ],
            admin_handlers.EDIT_SECTION_TITLE_FA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_edit_section_title_fa)
            ],
            admin_handlers.EDIT_SECTION_TITLE_DE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_edit_section_title_de)
            ],
            admin_handlers.EDIT_SECTION_DESC_FA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_edit_section_desc_fa)
            ],
            admin_handlers.EDIT_SECTION_DESC_DE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_edit_section_desc_de)
            ],
        },
        fallbacks=[
            CallbackQueryHandler(admin_handlers.admin_menu_callback, pattern='^admin_menu$'),
            CallbackQueryHandler(admin_handlers.admin_cancel_edit_section_callback, pattern=r'^cancel_edit_section_\d+$')
        ],
        name="admin_section_management"
    )
    
    # Admin callbacks
    admin_callbacks = [
        CallbackQueryHandler(
            admin_handlers.admin_manage_steps_callback,
            pattern='^admin_manage_steps$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_step_list_callback,
            pattern='^admin_step_list$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_step_detail_callback,
            pattern=r'^admin_step_detail_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_toggle_step_callback,
            pattern=r'^admin_toggle_step_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_delete_step_callback,
            pattern=r'^admin_delete_step_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_cancel_edit_step_callback,
            pattern=r'^cancel_edit_step_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_confirm_delete_step_callback,
            pattern=r'^admin_confirm_delete_step_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_manage_exams_callback,
            pattern='^admin_manage_exams$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_exam_step_callback,
            pattern=r'^admin_exam_step_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_question_list_callback,
            pattern='^admin_question_list$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_question_detail_callback,
            pattern=r'^admin_question_detail_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_delete_question_callback,
            pattern=r'^admin_delete_question_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_confirm_delete_question_callback,
            pattern=r'^admin_confirm_delete_question_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_cancel_edit_question_callback,
            pattern=r'^cancel_edit_question_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_cancel_add_question_callback,
            pattern='^cancel_add_question$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_statistics_callback,
            pattern='^admin_statistics$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_manage_users_callback,
            pattern='^admin_manage_users$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_user_detail_callback,
            pattern=r'^admin_user_detail_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_edit_user_callback,
            pattern=r'^admin_edit_user_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_delete_user_callback,
            pattern=r'^admin_delete_user_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_confirm_delete_user_callback,
            pattern=r'^admin_confirm_delete_user_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_menu_callback,
            pattern='^admin_menu$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_manage_sections_callback,
            pattern='^admin_manage_sections$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_section_list_callback,
            pattern='^admin_section_list$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_section_detail_callback,
            pattern=r'^admin_section_detail_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_delete_section_callback,
            pattern=r'^admin_delete_section_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_confirm_delete_section_callback,
            pattern=r'^admin_confirm_delete_section_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_cancel_edit_section_callback,
            pattern=r'^cancel_edit_section_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_add_lesson_to_section_callback,
            pattern='^admin_add_lesson_to_section$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_add_lesson_section_callback,
            pattern=r'^admin_add_lesson_section_\d+$'
        ),
        CallbackQueryHandler(
            admin_handlers.admin_confirm_add_lesson_callback,
            pattern=r'^admin_confirm_add_lesson_\d+$'
        )
    ]
    
    # Add handlers to application
    application.add_handler(language_conv)
    application.add_handler(CommandHandler('start', user_handlers.start_command))
    application.add_handler(CommandHandler('admin', admin_handlers.admin_command))
    
    # Add user callbacks
    for handler in user_callbacks:
        application.add_handler(handler)
    
    # Add admin conversations
    application.add_handler(admin_step_conv)
    application.add_handler(admin_exam_conv)
    application.add_handler(admin_user_conv)
    application.add_handler(admin_section_conv)
    
    # Add admin callbacks
    for handler in admin_callbacks:
        application.add_handler(handler)
    
    # Error handler
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors with better network error handling."""
        error = context.error
        
        # Check if it's a network error (expected and handled by library)
        if isinstance(error, NetworkError):
            error_str = str(error).lower()
            # These are common network errors that are usually transient
            if any(keyword in error_str for keyword in ['connect', 'timeout', 'disconnected', 'remote']):
                logger.warning(f"Network error (will retry): {type(error).__name__}: {error}")
                return  # Don't log full traceback for expected network errors
        
        # Log other errors with full traceback
        logger.error(f"Exception while handling an update: {error}", exc_info=error)
    
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting bot...")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}", exc_info=True)
    finally:
        logger.info("Bot shutdown complete")


if __name__ == '__main__':
    main()
