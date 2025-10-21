# 📚 Telegram Book Library Bot with Google Drive Integration

A Telegram bot that provides easy access to books and documents through Google Drive links. Users can browse books by category or search for specific titles through an intuitive menu system.

## ✨ Features

- **📂 Category-based browsing** - Books organized by language and subject categories
- **🔎 Smart search** - Find books by typing keywords
- **📱 Intuitive menu system** - Easy navigation with inline keyboards
- **🔗 Google Drive integration** - Direct access to books stored on Google Drive
- **⬇️ Multiple download options** - View in browser or direct download
- **🔄 Flexible database** - Easy to add new books and categories

## 🚀 Setup Instructions

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy your bot token

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Bot

1. Open `bot.py`
2. Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token:
   ```python
   BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
   ```

### 4. Set Up Google Drive Files

1. Upload your books/documents to Google Drive
2. Set sharing permissions to "Anyone with the link can view"
3. Copy the sharing links
4. Update `files_database.json` with your book structure:

```json
{
  "Your Category": [
    {
      "title": "Your Book Title",
      "link": "https://drive.google.com/file/d/YOUR_FILE_ID/view?usp=drive_link"
    }
  ]
}
```

### 5. Run the Bot

```bash
python bot.py
```

## 📁 File Structure

```
bot.py/
├── bot.py                 # Main bot code
├── files_database.json    # Book categories and Google Drive links
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🎯 How to Use

### For Users

1. Start the bot with `/start`
2. Choose from the main menu:
   - **📂 Browse Books** - Browse by category
   - **🔎 Search Books** - Search for specific books
   - **❓ Help** - Get help and instructions

### For Administrators

#### Adding New Books

1. Upload the book to Google Drive
2. Set sharing to "Anyone with the link can view"
3. Update `files_database.json`:

```json
{
  "Medicine Books": [
    {
      "title": "Existing Book",
      "link": "https://drive.google.com/file/d/existing_id/view?usp=drive_link"
    },
    {
      "title": "New Book Title",
      "link": "https://drive.google.com/file/d/new_file_id/view?usp=drive_link"
    }
  ]
}
```

#### Adding New Categories

```json
{
  "New Category": [
    {
      "title": "Book Title 1",
      "link": "https://drive.google.com/file/d/file_id1/view?usp=drive_link"
    },
    {
      "title": "Book Title 2", 
      "link": "https://drive.google.com/file/d/file_id2/view?usp=drive_link"
    }
  ]
}
```

## 🔧 Customization

### Customizing Categories

The bot automatically detects categories from `files_database.json`. You can customize the emojis in the `show_categories` function:

```python
category_emojis = {
    "English Books": "🇺🇸",
    "Turkish Books": "🇹🇷", 
    "Arabic Books": "🇸🇦",
    "Medicine Books": "🏥",
    "Your Category": "📚"
}
```

### Adding More Categories

The bot automatically detects categories from `files_database.json`. Just add new categories with their books.

## 🛠️ Technical Details

- **Framework**: python-telegram-bot v20.7
- **Database**: JSON file (easily replaceable with SQLite)
- **Storage**: Google Drive integration
- **File Support**: Any file type supported by Google Drive
- **Search**: Case-insensitive partial matching
- **Link Processing**: Automatic Google Drive link conversion

## 📝 Example Usage Flow

1. User sends `/start`
2. Bot shows main menu with 3 options
3. User clicks "📂 Browse Books"
4. Bot shows categories (English Books, Turkish Books, etc.)
5. User clicks a category
6. Bot shows books in that category
7. User clicks a book
8. Bot provides Google Drive link and direct download option

## 🔍 Search Example

1. User clicks "🔎 Search Books"
2. Bot asks for search term
3. User types "biochemistry"
4. Bot shows all books containing "biochemistry"
5. User clicks desired book
6. Bot provides Google Drive link and direct download option

## ⚠️ Important Notes

- Make sure your bot token is kept secure
- Google Drive files must be set to "Anyone with the link can view"
- Book titles in the database must match exactly with the titles you want to display
- Google Drive links must be in the correct format
- No local file storage required - everything is on Google Drive

## 🆘 Troubleshooting

### Bot doesn't respond
- Check if the bot token is correct
- Ensure the bot is running without errors
- Check the console for error messages

### Books not found
- Verify Google Drive links are correct and accessible
- Check that files are set to "Anyone with the link can view"
- Ensure book titles in the database match exactly

### Search not working
- Check if books are properly added to the database
- Verify search terms are spelled correctly
- Check console for any error messages

### Google Drive links not working
- Ensure files are set to "Anyone with the link can view"
- Check that the Google Drive link format is correct
- Verify the file ID in the URL is valid

## 📞 Support

If you encounter any issues, check the console output for error messages and ensure all setup steps are completed correctly.
