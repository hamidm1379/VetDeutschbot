# i18n Architecture Documentation

The bot has been refactored to support an i18n-ready architecture, making it easy to add new languages without code changes.

## Architecture Overview

### 1. Translation System (`utils/i18n.py`)

- **JSON-based translations**: Each language has its own JSON file in `locales/`
- **Dynamic language loading**: Languages are automatically discovered from JSON files
- **Fallback mechanism**: Falls back to default language (English) if translation missing
- **Caching**: Uses LRU cache for performance

### 2. Database Schema (`schema_i18n.sql`)

- **JSON columns**: Uses JSON columns for multilingual content
  - `steps.title_json`: `{"fa": "...", "de": "...", "en": "..."}`
  - `steps.description_json`: `{"fa": "...", "de": "...", "en": "..."}`
  - `questions.question_json`: `{"fa": "...", "de": "...", "en": "..."}`
- **No schema changes needed**: Add new languages by just adding translations to JSON

### 3. Models (`models.py`)

- **Helper methods**: `get_text_by_language()` methods extract text by language code
- **Automatic fallback**: Falls back to default language if requested language not available
- **JSON handling**: Automatically parses JSON fields from database

## Adding a New Language

### Step 1: Create Translation File

Create a new JSON file in `locales/` directory:

```json
{
  "meta": {
    "name": "Spanish",
    "native_name": "Español",
    "code": "es",
    "rtl": false
  },
  "select_language": "🌐 Por favor seleccione su idioma",
  "language_selected": "✅ ¡Su idioma ha sido configurado con éxito!",
  ...
}
```

### Step 2: That's It!

The bot will automatically:
- Detect the new language file
- Add it to language selection menu
- Support it in all handlers
- Store content in database JSON fields

No code changes needed!

## Language File Structure

Each language file must have:

1. **meta section** (required):
   - `name`: English name
   - `native_name`: Native name
   - `code`: ISO language code (2-10 chars)
   - `rtl`: Boolean for right-to-left languages

2. **Translation keys**: All keys from `en.json` must be present

## Current Languages

- **fa** (Persian/Farsi) - RTL
- **de** (German/Deutsch) - LTR
- **en** (English) - LTR (default)

## Migration from Old Schema

If you have existing data with the old schema (separate columns for each language), use the migration script in `schema_i18n.sql`:

```sql
-- Convert old schema to new i18n schema
ALTER TABLE steps 
    ADD COLUMN title_json JSON,
    ADD COLUMN description_json JSON;

UPDATE steps SET 
    title_json = JSON_OBJECT('fa', title_fa, 'de', title_de),
    description_json = JSON_OBJECT('fa', description_fa, 'de', description_de);

ALTER TABLE steps 
    DROP COLUMN title_fa,
    DROP COLUMN title_de,
    DROP COLUMN description_fa,
    DROP COLUMN description_de;
```

## Benefits

1. **No code changes**: Add languages by adding JSON files
2. **Scalable**: Support unlimited languages
3. **Maintainable**: All translations in one place per language
4. **Type-safe**: JSON structure ensures consistency
5. **Performance**: Caching and efficient lookups

## Usage Examples

### In Handlers

```python
from utils.i18n import get_text, format_text

# Get text in user's language
text = get_text('welcome', language='fa')

# Format with parameters
text = format_text('step_title', language='de', step_num=1, total_steps=5)
```

### In Models

```python
from models import Step

# Get step title in specific language
step = Step.get_by_id(1)
title = Step.get_text_by_language(step, 'title_json', 'es')
```

## Best Practices

1. **Always provide English translations**: English is the default fallback
2. **Use descriptive keys**: Make translation keys self-documenting
3. **Keep JSON files in sync**: When adding new keys, add to all language files
4. **Test RTL languages**: Ensure UI works correctly for RTL languages
5. **Validate JSON**: Use JSON validators before committing
