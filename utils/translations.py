"""
Translation system for multi-language support (FA/DE).
All bot messages are stored here.
"""
from typing import Dict

# Translation dictionary: {key: {lang: text}}
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Language selection
    'select_language': {
        'fa': '🌐 لطفاً زبان خود را انتخاب کنید\n\nPlease select your language',
        'de': '🌐 Bitte wählen Sie Ihre Sprache\n\nPlease select your language'
    },
    'language_selected': {
        'fa': '✅ زبان شما با موفقیت تنظیم شد!',
        'de': '✅ Ihre Sprache wurde erfolgreich festgelegt!'
    },
    
    # Main menu
    'welcome': {
        'fa': '👋 به ربات یادگیری زبان خوش آمدید!\n\nبه منوی اصلی بروید:',
        'de': '👋 Willkommen beim Sprachlernbot!\n\nGehen Sie zum Hauptmenü:'
    },
    'main_menu': {
        'fa': '📚 منوی اصلی',
        'de': '📚 Hauptmenü'
    },
    'start_learning': {
        'fa': '📖 شروع یادگیری',
        'de': '📖 Lernen beginnen'
    },
    'my_progress': {
        'fa': '📊 پیشرفت من',
        'de': '📊 Mein Fortschritt'
    },
    
    # Steps
    'step_title': {
        'fa': '📝 مرحله {step_num} از {total_steps}',
        'de': '📝 Schritt {step_num} von {total_steps}'
    },
    'step_description': {
        'fa': '📄 توضیحات:\n{description}',
        'de': '📄 Beschreibung:\n{description}'
    },
    'start_exam': {
        'fa': '✅ شروع آزمون این مرحله',
        'de': '✅ Prüfung für diesen Schritt starten'
    },
    'next_step': {
        'fa': '➡️ مرحله بعدی',
        'de': '➡️ Nächster Schritt'
    },
    'back_to_menu': {
        'fa': '🔙 بازگشت به منو',
        'de': '🔙 Zurück zum Menü'
    },
    'no_more_steps': {
        'fa': '🎉 تبریک! شما تمام مراحل را به پایان رساندید!',
        'de': '🎉 Glückwunsch! Sie haben alle Schritte abgeschlossen!'
    },
    'step_locked': {
        'fa': '🔒 این مرحله قفل است. لطفاً ابتدا آزمون مرحله قبلی را پاس کنید.',
        'de': '🔒 Dieser Schritt ist gesperrt. Bitte bestehen Sie zuerst die Prüfung des vorherigen Schritts.'
    },
    
    # Exams
    'exam_start': {
        'fa': '📝 آزمون مرحله {step_num}\n\nلطفاً به سوالات پاسخ دهید:',
        'de': '📝 Prüfung Schritt {step_num}\n\nBitte beantworten Sie die Fragen:'
    },
    'question_num': {
        'fa': '❓ سوال {current} از {total}',
        'de': '❓ Frage {current} von {total}'
    },
    'select_answer': {
        'fa': 'لطفاً یک گزینه را انتخاب کنید:',
        'de': 'Bitte wählen Sie eine Option:'
    },
    'exam_completed': {
        'fa': '✅ آزمون به پایان رسید!',
        'de': '✅ Prüfung abgeschlossen!'
    },
    'exam_score': {
        'fa': '📊 نمره شما: {score}%',
        'de': '📊 Ihre Punktzahl: {score}%'
    },
    'exam_passed': {
        'fa': '🎉 تبریک! شما این آزمون را با موفقیت پاس کردید!\n\nمرحله بعدی برای شما باز شد.',
        'de': '🎉 Glückwunsch! Sie haben diese Prüfung bestanden!\n\nDer nächste Schritt wurde für Sie freigeschaltet.'
    },
    'exam_failed': {
        'fa': '❌ متأسفانه شما این آزمون را پاس نکردید.\n\nلطفاً دوباره تلاش کنید.',
        'de': '❌ Leider haben Sie diese Prüfung nicht bestanden.\n\nBitte versuchen Sie es erneut.'
    },
    'exam_results_title': {
        'fa': '📋 نتایج سوالات:',
        'de': '📋 Frageergebnisse:'
    },
    'question_result_correct': {
        'fa': '✅ سوال {num}: درست',
        'de': '✅ Frage {num}: Richtig'
    },
    'question_result_incorrect': {
        'fa': '❌ سوال {num}: غلط (پاسخ شما: {user_answer})',
        'de': '❌ Frage {num}: Falsch (Ihre Antwort: {user_answer}, Richtige Antwort: {correct_answer})'
    },
    'no_answer': {
        'fa': 'پاسخ داده نشده',
        'de': 'Nicht beantwortet'
    },
    'passing_score': {
        'fa': 'حداقل نمره قبولی: 80%',
        'de': 'Mindestpunktzahl zum Bestehen: 80%'
    },
    'no_exam': {
        'fa': '⚠️ برای این مرحله آزمونی تعریف نشده است.',
        'de': '⚠️ Für diesen Schritt ist keine Prüfung definiert.'
    },
    'exam_already_passed': {
        'fa': '✅ شما آزمون این مرحله را داده‌اید.',
        'de': '✅ Sie haben die Prüfung für diesen Schritt bereits abgelegt.'
    },
    
    # Progress
    'progress_info': {
        'fa': '📊 اطلاعات پیشرفت شما:\n\nمرحله فعلی: {current_step}/{total_steps}',
        'de': '📊 Ihre Fortschrittsinformationen:\n\nAktueller Schritt: {current_step}/{total_steps}'
    },
    
    # Admin panel
    'admin_menu': {
        'fa': '⚙️ پنل مدیریت',
        'de': '⚙️ Admin-Panel'
    },
    'admin_only': {
        'fa': '⚠️ این دستور فقط برای مدیران است.',
        'de': '⚠️ Dieser Befehl ist nur für Administratoren.'
    },
    'manage_steps': {
        'fa': '📝 مدیریت مراحل',
        'de': '📝 Schritte verwalten'
    },
    'manage_exams': {
        'fa': '📋 مدیریت آزمون‌ها',
        'de': '📋 Prüfungen verwalten'
    },
    'view_statistics': {
        'fa': '📊 آمار کاربران',
        'de': '📊 Benutzerstatistiken'
    },
    'add_step': {
        'fa': '➕ افزودن مرحله جدید',
        'de': '➕ Neuen Schritt hinzufügen'
    },
    'edit_step': {
        'fa': '✏️ ویرایش مرحله',
        'de': '✏️ Schritt bearbeiten'
    },
    'delete_step': {
        'fa': '🗑️ حذف مرحله',
        'de': '🗑️ Schritt löschen'
    },
    'toggle_step': {
        'fa': '🔄 فعال/غیرفعال کردن مرحله',
        'de': '🔄 Schritt aktivieren/deaktivieren'
    },
    'step_list': {
        'fa': '📋 لیست مراحل',
        'de': '📋 Schrittanleiste'
    },
    'step_details': {
        'fa': '📝 جزئیات مرحله {step_id}',
        'de': '📝 Schrittdetails {step_id}'
    },
    'enter_title_fa': {
        'fa': 'لطفاً عنوان فارسی را وارد کنید:',
        'de': 'Bitte geben Sie den persischen Titel ein:'
    },
    'enter_title_de': {
        'fa': 'لطفاً عنوان آلمانی را وارد کنید:',
        'de': 'Bitte geben Sie den deutschen Titel ein:'
    },
    'enter_description_fa': {
        'fa': 'لطفاً توضیحات فارسی را وارد کنید:',
        'de': 'Bitte geben Sie die persische Beschreibung ein:'
    },
    'enter_description_de': {
        'fa': 'لطفاً توضیحات آلمانی را وارد کنید:',
        'de': 'Bitte geben Sie die deutsche Beschreibung ein:'
    },
    'upload_file': {
        'fa': 'لطفاً فایل را آپلود کنید (ویدیو، صدا، PDF یا تصویر):',
        'de': 'Bitte laden Sie die Datei hoch (Video, Audio, PDF oder Bild):'
    },
    'step_created': {
        'fa': '✅ مرحله با موفقیت ایجاد شد!',
        'de': '✅ Schritt wurde erfolgreich erstellt!'
    },
    'step_updated': {
        'fa': '✅ مرحله با موفقیت به‌روزرسانی شد!',
        'de': '✅ Schritt wurde erfolgreich aktualisiert!'
    },
    'step_deleted': {
        'fa': '✅ مرحله با موفقیت حذف شد!',
        'de': '✅ Schritt wurde erfolgreich gelöscht!'
    },
    'step_toggled': {
        'fa': '✅ وضعیت مرحله تغییر کرد!',
        'de': '✅ Schrittstatus wurde geändert!'
    },
    'select_step_for_exam': {
        'fa': 'لطفاً مرحله‌ای را برای مدیریت آزمون انتخاب کنید:',
        'de': 'Bitte wählen Sie einen Schritt zur Prüfungsverwaltung:'
    },
    'exam_management': {
        'fa': '📋 مدیریت آزمون مرحله {step_id}',
        'de': '📋 Prüfungsverwaltung Schritt {step_id}'
    },
    'add_question': {
        'fa': '➕ افزودن سوال',
        'de': '➕ Frage hinzufügen'
    },
    'edit_question': {
        'fa': '✏️ ویرایش سوال',
        'de': '✏️ Frage bearbeiten'
    },
    'delete_question': {
        'fa': '🗑️ حذف سوال',
        'de': '🗑️ Frage löschen'
    },
    'question_list': {
        'fa': '📋 لیست سوالات',
        'de': '📋 Fragenliste'
    },
    'enter_question_fa': {
        'fa': 'لطفاً متن سوال به فارسی را وارد کنید:',
        'de': 'Bitte geben Sie die Frage auf Persisch ein:'
    },
    'enter_question_de': {
        'fa': 'لطفاً متن سوال به آلمانی را وارد کنید:',
        'de': 'Bitte geben Sie die Frage auf Deutsch ein:'
    },
    'enter_options': {
        'fa': 'لطفاً گزینه‌ها را به صورت خط به خط وارد کنید (حداقل 2 گزینه):',
        'de': 'Bitte geben Sie die Optionen zeilenweise ein (mindestens 2 Optionen):'
    },
    'enter_correct_option': {
        'fa': 'لطفاً شماره گزینه صحیح را وارد کنید (شماره از 1 شروع می‌شود):',
        'de': 'Bitte geben Sie die Nummer der richtigen Option ein (Nummerierung beginnt bei 1):'
    },
    'question_created': {
        'fa': '✅ سوال با موفقیت ایجاد شد!',
        'de': '✅ Frage wurde erfolgreich erstellt!'
    },
    'question_updated': {
        'fa': '✅ سوال با موفقیت به‌روزرسانی شد!',
        'de': '✅ Frage wurde erfolgreich aktualisiert!'
    },
    'question_deleted': {
        'fa': '✅ سوال با موفقیت حذف شد!',
        'de': '✅ Frage wurde erfolgreich gelöscht!'
    },
    'confirm_delete_question': {
        'fa': '⚠️ آیا مطمئن هستید که می‌خواهید این سوال را حذف کنید؟',
        'de': '⚠️ Sind Sie sicher, dass Sie diese Frage löschen möchten?'
    },
    'yes': {
        'fa': '✅ بله',
        'de': '✅ Ja'
    },
    'no': {
        'fa': '❌ خیر',
        'de': '❌ Nein'
    },
    'statistics': {
        'fa': '📊 آمار کاربران:\n\n',
        'de': '📊 Benutzerstatistiken:\n\n'
    },
    'step_users_count': {
        'fa': 'مرحله {step_id}: {count} کاربر',
        'de': 'Schritt {step_id}: {count} Benutzer'
    },
    
    # Errors
    'error_occurred': {
        'fa': '❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.',
        'de': '❌ Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.'
    },
    'invalid_input': {
        'fa': '⚠️ ورودی نامعتبر است. لطفاً دوباره تلاش کنید.',
        'de': '⚠️ Ungültige Eingabe. Bitte versuchen Sie es erneut.'
    },
    'cancel': {
        'fa': '❌ لغو',
        'de': '❌ Abbrechen'
    },
    'back': {
        'fa': '🔙 بازگشت',
        'de': '🔙 Zurück'
    }
}


def get_text(key: str, language: str = 'fa') -> str:
    """
    Get translated text by key and language.
    
    Args:
        key: Translation key
        language: Language code ('fa' or 'de')
    
    Returns:
        Translated text or key if not found
    """
    if key not in TRANSLATIONS:
        return key
    
    translations = TRANSLATIONS[key]
    return translations.get(language, translations.get('fa', key))


def format_text(key: str, language: str = 'fa', **kwargs) -> str:
    """
    Get translated text and format it with provided arguments.
    
    Args:
        key: Translation key
        language: Language code ('fa' or 'de')
        **kwargs: Format arguments
    
    Returns:
        Formatted translated text
    """
    text = get_text(key, language)
    try:
        return text.format(**kwargs)
    except KeyError:
        return text
