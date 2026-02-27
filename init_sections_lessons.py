"""
Script to initialize sections and lessons structure.
This script creates 5 sections with 4 lessons each.
Each lesson needs to be linked to an existing step.
"""
import sys
import io
from db import db
from models import Section, Lesson, Step
import json

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def create_default_sections():
    """Create 5 default sections with Persian and German titles."""
    sections_data = [
        {
            'title': {
                'fa': 'بخش ۱: مقدمات',
                'de': 'Abschnitt 1: Grundlagen',
                'en': 'Section 1: Basics'
            },
            'description': {
                'fa': 'شروع یادگیری با اصول اولیه',
                'de': 'Beginnen Sie mit den Grundlagen',
                'en': 'Start learning with the basics'
            }
        },
        {
            'title': {
                'fa': 'بخش ۲: مکالمه روزمره',
                'de': 'Abschnitt 2: Alltagsgespräche',
                'en': 'Section 2: Daily Conversation'
            },
            'description': {
                'fa': 'یادگیری مکالمات روزمره',
                'de': 'Alltagsgespräche lernen',
                'en': 'Learn daily conversations'
            }
        },
        {
            'title': {
                'fa': 'بخش ۳: دستور زبان',
                'de': 'Abschnitt 3: Grammatik',
                'en': 'Section 3: Grammar'
            },
            'description': {
                'fa': 'یادگیری قواعد دستور زبان',
                'de': 'Grammatikregeln lernen',
                'en': 'Learn grammar rules'
            }
        },
        {
            'title': {
                'fa': 'بخش ۴: واژگان پیشرفته',
                'de': 'Abschnitt 4: Erweiterter Wortschatz',
                'en': 'Section 4: Advanced Vocabulary'
            },
            'description': {
                'fa': 'یادگیری واژگان پیشرفته',
                'de': 'Erweiterten Wortschatz lernen',
                'en': 'Learn advanced vocabulary'
            }
        },
        {
            'title': {
                'fa': 'بخش ۵: مهارت‌های پیشرفته',
                'de': 'Abschnitt 5: Fortgeschrittene Fähigkeiten',
                'en': 'Section 5: Advanced Skills'
            },
            'description': {
                'fa': 'تقویت مهارت‌های پیشرفته',
                'de': 'Fortgeschrittene Fähigkeiten stärken',
                'en': 'Strengthen advanced skills'
            }
        }
    ]
    
    created_sections = []
    for i, section_data in enumerate(sections_data, start=1):
        section_id = Section.create(
            title_json=section_data['title'],
            description_json=section_data['description'],
            order_number=i
        )
        created_sections.append(section_id)
        print(f"[OK] Created section {i}: {section_data['title']['fa']}")
    
    return created_sections


def link_steps_to_lessons(section_ids):
    """Link existing steps to lessons in sections."""
    # Get all active steps
    active_steps = Step.get_all_active()
    
    if not active_steps:
        print("[WARNING] No active steps found. Please create steps first using the admin panel.")
        return
    
    print(f"\n[INFO] Found {len(active_steps)} active steps")
    
    # Distribute steps across sections (4 lessons per section)
    lessons_per_section = 4
    total_lessons_needed = len(section_ids) * lessons_per_section
    
    if len(active_steps) < total_lessons_needed:
        print(f"[WARNING] You have {len(active_steps)} steps but need {total_lessons_needed} lessons.")
        print(f"   Only {len(active_steps)} lessons will be created.")
    
    step_index = 0
    for section_index, section_id in enumerate(section_ids):
        print(f"\n[INFO] Creating lessons for section {section_index + 1}...")
        
        for lesson_num in range(1, lessons_per_section + 1):
            if step_index >= len(active_steps):
                print(f"   [WARNING] No more steps available. Stopping at lesson {lesson_num - 1}")
                break
            
            step = active_steps[step_index]
            lesson_id = Lesson.create(
                section_id=section_id,
                step_id=step['id'],
                order_number=lesson_num
            )
            
            step_title = Step.get_text_by_language(step, 'title_json', 'fa')
            print(f"   [OK] Created lesson {lesson_num}: {step_title}")
            step_index += 1


def main():
    """Main function to initialize sections and lessons."""
    print("[INFO] Initializing sections and lessons structure...\n")
    
    # Check if sections already exist
    existing_sections = Section.get_all_active()
    if existing_sections:
        print(f"[INFO] Found {len(existing_sections)} existing sections.")
        print("[INFO] Skipping section creation. If you want to create new sections,")
        print("       please delete existing ones first or modify this script.")
        # Check if lessons exist
        all_lessons = []
        for section in existing_sections:
            lessons = Lesson.get_by_section_id(section['id'])
            all_lessons.extend(lessons)
        
        if not all_lessons:
            print("[INFO] No lessons found. Creating lessons for existing sections...")
            link_steps_to_lessons([s['id'] for s in existing_sections])
        else:
            print(f"[INFO] Found {len(all_lessons)} existing lessons.")
        return
    
    # Create sections
    section_ids = create_default_sections()
    
    # Link steps to lessons
    print("\n" + "="*50)
    link_steps_to_lessons(section_ids)
    
    print("\n" + "="*50)
    print("[SUCCESS] Initialization complete!")
    print(f"[INFO] Created {len(section_ids)} sections")
    print("\n[INFO] Note: The first section and first 2 lessons are unlocked automatically")
    print("   when users first access the learning menu.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n[ERROR] Cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
