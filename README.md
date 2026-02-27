# Telegram Language Learning Bot

A production-ready Telegram bot for language learning with step-by-step lessons and exams. Supports Persian (FA) and German (DE) languages.

## Features

- 🌐 **Multi-language support** (Persian/Deutsch)
- 📚 **Step-based learning** with file uploads (video, audio, PDF, images)
- 📝 **Interactive exams** with multiple-choice questions
- 🔒 **Step locking** - users must pass exams to unlock next steps
- ⚙️ **Admin panel** - full CRUD operations for steps and exams
- 📊 **Progress tracking** and statistics
- 🎯 **Unicode & RTL safe** for Persian text

## Tech Stack

- Python 3.11+
- python-telegram-bot (v20+ async)
- MySQL (mysql-connector-python)
- dotenv for configuration

## Project Structure

```
VetDeutschbot/
├── bot.py                 # Main bot entry point
├── db.py                  # Database connection and pool
├── models.py              # Data models and database operations
├── handlers/
│   ├── __init__.py
│   ├── user_handlers.py   # User-facing handlers
│   └── admin_handlers.py   # Admin panel handlers
├── utils/
│   ├── translations.py    # Multi-language translations
│   └── helpers.py          # Helper functions
├── schema.sql             # Database schema
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Installation

### 1. Clone or download the project

```bash
cd VetDeutschbot
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up MySQL database

**Option 1: Using the initialization script (Recommended)**
```bash
# Make sure your .env file is configured with database credentials
python init_database.py
```

**Option 2: Manual setup**
```bash
# Login to MySQL
mysql -u root -p

# Create database and user (optional)
CREATE DATABASE telegram_bot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bot_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON telegram_bot.* TO 'bot_user'@'localhost';
FLUSH PRIVILEGES;

# Import schema (use schema_i18n.sql for i18n-ready version)
mysql -u root -p telegram_bot < schema_i18n.sql
# OR for standard version:
mysql -u root -p telegram_bot < schema.sql
```

### 4. Configure environment variables

```bash
# Copy example file
cp .env.example .env

# Edit .env file with your values
nano .env
```

Required variables:
- `BOT_TOKEN`: Get from [@BotFather](https://t.me/BotFather) on Telegram
- `DB_HOST`: MySQL host (usually `localhost`)
- `DB_USER`: MySQL username
- `DB_PASSWORD`: MySQL password
- `DB_NAME`: Database name (default: `telegram_bot`)
- `ADMIN_IDS`: Comma-separated Telegram user IDs (get your ID from [@userinfobot](https://t.me/userinfobot))

### 5. Run the bot

```bash
python bot.py
```

## Usage

### For Users

1. Start the bot: `/start`
2. Select your language (Persian or German)
3. Navigate through steps
4. Complete exams to unlock next steps
5. Track your progress

### For Admins

1. Access admin panel: `/admin`
2. Manage steps:
   - Add new steps with titles, descriptions, and files
   - Edit existing steps
   - Enable/disable steps
   - Delete steps
3. Manage exams:
   - Add questions to step exams
   - Edit questions
   - Delete questions
4. View statistics:
   - See number of users per step

## Database Schema

### Tables

- **users**: User information and progress
- **steps**: Learning steps with bilingual content
- **exams**: Exams linked to steps
- **questions**: Multiple-choice questions for exams
- **user_exam_results**: User exam scores and pass status

## Deployment on Ubuntu VPS

### 1. Install Python and MySQL

```bash
sudo apt update
sudo apt install python3 python3-pip mysql-server
```

### 2. Set up MySQL

```bash
sudo mysql_secure_installation
sudo mysql -u root -p
# Create database and user as shown above
```

### 3. Clone and configure bot

```bash
cd /opt
sudo git clone <your-repo> telegram-bot
cd telegram-bot
sudo pip3 install -r requirements.txt
sudo cp .env.example .env
sudo nano .env  # Edit with your values
```

### 4. Create systemd service

```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Add:
```ini
[Unit]
Description=Telegram Language Learning Bot
After=network.target mysql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/opt/telegram-bot
ExecStart=/usr/bin/python3 /opt/telegram-bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5. Start service

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

### 6. View logs

```bash
sudo journalctl -u telegram-bot -f
```

## Features in Detail

### Step-based Learning

- Each step contains:
  - Bilingual title (FA/DE)
  - Bilingual description
  - Optional file (video, audio, PDF, image)
- Steps are locked until previous step's exam is passed
- Progress is saved per user

### Exam System

- Multiple-choice questions
- Bilingual question text
- Minimum passing score: 70%
- Results stored in database
- Next step unlocked upon passing

### Admin Panel

- Full CRUD operations
- File upload support
- Real-time statistics
- Step enable/disable
- Question management

## Troubleshooting

### Bot not responding

- Check bot token in `.env`
- Verify database connection
- Check logs: `sudo journalctl -u telegram-bot -n 50`

### Database errors

- Verify MySQL is running: `sudo systemctl status mysql`
- Check database credentials in `.env`
- Ensure schema is imported: `mysql -u root -p telegram_bot < schema.sql`

### Permission errors

- Ensure bot user has database privileges
- Check file permissions for `.env` file

## License

This project is provided as-is for educational and production use.

## Support

For issues or questions, please check the code comments or create an issue in the repository.
