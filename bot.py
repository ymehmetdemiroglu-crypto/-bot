import os
import json
import logging
import re
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "8459047761:AAEv-RrhZQnngpD1iO47pwgB2_t7wnqLhrE"

class FileBot:
    def __init__(self):
        self.files_db = self.load_files_database()
        
    def load_files_database(self) -> Dict:
        """Load the files database from JSON file"""
        try:
            with open('files_database.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default database structure
            default_db = {
                "English Books": [
                    {
                        "title": "Sample Book",
                        "link": "https://drive.google.com/file/d/sample_id/view?usp=drive_link"
                    }
                ]
            }
            self.save_files_database(default_db)
            return default_db
    
    def save_files_database(self, database: Dict):
        """Save the files database to JSON file"""
        with open('files_database.json', 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
    
    def get_all_books(self) -> List[Dict]:
        """Get all books from all categories"""
        all_books = []
        for category, books in self.files_db.items():
            for book in books:
                book_with_category = book.copy()
                book_with_category['category'] = category
                all_books.append(book_with_category)
        return all_books
    
    def search_books(self, query: str) -> List[Dict]:
        """Search for books containing the query"""
        query = query.lower()
        matching_books = []
        
        for category, books in self.files_db.items():
            for book in books:
                if query in book['title'].lower():
                    book_with_category = book.copy()
                    book_with_category['category'] = category
                    matching_books.append(book_with_category)
        
        return matching_books[:10]  # Limit to 10 results
    
    def get_direct_download_link(self, google_drive_link: str) -> str:
        """Convert Google Drive sharing link to direct download link"""
        # Extract file ID from Google Drive link
        file_id_match = re.search(r'/file/d/([a-zA-Z0-9-_]+)', google_drive_link)
        if file_id_match:
            file_id = file_id_match.group(1)
            # Convert to direct download link
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        return google_drive_link
    
    def validate_google_drive_link(self, link: str) -> bool:
        """Validate if the link is a proper Google Drive link"""
        return "drive.google.com" in link and "/file/d/" in link

# Initialize bot instance
file_bot = FileBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton("📂 Browse Books", callback_data="view_books")],
        [InlineKeyboardButton("🔎 Search Books", callback_data="search_books")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = """
📚 **Welcome to the Book Library Bot!**

Choose an option from the menu below:

📂 **Browse Books** - Browse books by category
🔎 **Search Books** - Search for specific books
❓ **Help** - Learn how to use this bot

Use /start anytime to return to this main menu.
    """
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show book categories"""
    keyboard = []
    
    # Add category buttons with appropriate emojis
    category_emojis = {
        "English Books": "🇺🇸",
        "Turkish Books": "🇹🇷", 
        "Arabic Books": "🇸🇦",
        "Training & Exam Files": "📋"
    }
    
    for category in file_bot.files_db.keys():
        emoji = category_emojis.get(category, "📚")
        book_count = len(file_bot.files_db[category])
        keyboard.append([InlineKeyboardButton(f"{emoji} {category} ({book_count})", callback_data=f"category_{category}")])
    
    # Add back button
    keyboard.append([InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "📂 **Select a category:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_books_in_category(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    """Show books in a specific category"""
    books = file_bot.files_db.get(category, [])
    
    if not books:
        await update.callback_query.edit_message_text(
            f"❌ No books found in {category}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="view_books")]])
        )
        return
    
    keyboard = []
    
    # Add book buttons (limit to 8 books per page to avoid Telegram limits)
    for book in books[:8]:
        # Truncate long titles
        display_title = book['title'][:35] + "..." if len(book['title']) > 35 else book['title']
        keyboard.append([InlineKeyboardButton(f"📖 {display_title}", callback_data=f"book_{book['title']}_{category}")])
    
    # Add navigation buttons
    keyboard.append([InlineKeyboardButton("⬅️ Back to Categories", callback_data="view_books")])
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"📂 **{category}**\n\nSelect a book to get the download link:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def send_book_link(update: Update, context: ContextTypes.DEFAULT_TYPE, book_title: str, category: str):
    """Send a book's Google Drive link to the user"""
    books = file_bot.files_db.get(category, [])
    book = None
    
    # Find the book by title
    for b in books:
        if b['title'] == book_title:
            book = b
            break
    
    if not book:
        await update.callback_query.answer("❌ Book not found!", show_alert=True)
        return
    
    # Validate the Google Drive link
    if not file_bot.validate_google_drive_link(book['link']):
        await update.callback_query.answer("❌ Invalid Google Drive link!", show_alert=True)
        return
    
    # Get direct download link
    direct_link = file_bot.get_direct_download_link(book['link'])
    
    # Create keyboard with both original and direct download links
    keyboard = [
        [InlineKeyboardButton("🔗 Open in Google Drive", url=book['link'])],
        [InlineKeyboardButton("⬇️ Direct Download", url=direct_link)],
        [InlineKeyboardButton("⬅️ Back to Category", callback_data=f"category_{category}")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = f"""
📖 **{book['title']}**

**Category:** {category}

Choose how you want to access the book:

🔗 **Open in Google Drive** - View the book in your browser
⬇️ **Direct Download** - Download the file directly

*Note: Make sure the Google Drive file is set to "Anyone with the link can view" for the direct download to work.*
    """
    
    await update.callback_query.edit_message_text(
        message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    await update.callback_query.answer("✅ Book link sent!")

async def show_search_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show search menu"""
    keyboard = [
        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    search_message = """
🔎 **Search Books**

Type a keyword to search for books. The bot will find books containing your search term.

**Examples:**
• `biochemistry` - finds biochemistry books
• `medicine` - finds medicine books
• `pharmacy` - finds pharmacy-related books

Type your search term now:
    """
    
    await update.callback_query.edit_message_text(
        search_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search queries"""
    query = update.message.text.strip()
    
    if not query:
        await update.message.reply_text("Please enter a search term.")
        return
    
    results = file_bot.search_books(query)
    
    if not results:
        await update.message.reply_text(
            f"❌ No books found for '{query}'\n\nTry a different search term or use /start to browse categories.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])
        )
        return
    
    # Create keyboard with search results
    keyboard = []
    for book in results[:8]:  # Limit to 8 results
        display_title = book['title'][:30] + "..." if len(book['title']) > 30 else book['title']
        keyboard.append([InlineKeyboardButton(f"📖 {display_title}", callback_data=f"book_{book['title']}_{book['category']}")])
    
    keyboard.append([InlineKeyboardButton("🔎 New Search", callback_data="search_books")])
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🔎 **Search results for '{query}':**\n\nFound {len(results)} book(s):",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help menu"""
    keyboard = [
        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    help_message = """
❓ **How to use this bot:**

**📂 Browse Books**
• Browse books organized by categories
• Click on a category to see available books
• Click on a book to get download links

**🔎 Search Books**
• Type keywords to find specific books
• The bot will suggest matching books
• Click on a book to get download links

**📱 Navigation**
• Use the buttons to navigate through menus
• Use /start to return to the main menu anytime
• All books are stored on Google Drive

**🔗 Download Options**
• **Open in Google Drive** - View the book in your browser
• **Direct Download** - Download the file directly

**💡 Tips:**
• Books are organized by language and subject categories
• Search is case-insensitive
• You can search for partial book titles
• Make sure Google Drive files are set to "Anyone with the link can view"
    """
    
    await update.callback_query.edit_message_text(
        help_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "main_menu":
        # Return to main menu
        keyboard = [
            [InlineKeyboardButton("📂 Browse Books", callback_data="view_books")],
            [InlineKeyboardButton("🔎 Search Books", callback_data="search_books")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📚 **Main Menu**\n\nChoose an option:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "view_books":
        await show_categories(update, context)
    
    elif data == "search_books":
        await show_search_menu(update, context)
    
    elif data == "help":
        await show_help(update, context)
    
    elif data.startswith("category_"):
        category = data.replace("category_", "")
        await show_books_in_category(update, context, category)
    
    elif data.startswith("book_"):
        # Extract book title and category from callback data
        parts = data.replace("book_", "").split("_", 1)
        if len(parts) >= 2:
            book_title = parts[0]
            category = parts[1]
            await send_book_link(update, context, book_title, category)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("🤖 Book Library Bot is starting...")
    print("📋 Make sure to:")
    print("   1. Replace BOT_TOKEN with your actual bot token")
    print("   2. Update files_database.json with your book structure")
    print("   3. Ensure Google Drive files are set to 'Anyone with the link can view'")
    print("   4. Test the bot with /start command")
    
    application.run_polling()

if __name__ == '__main__':
    main()