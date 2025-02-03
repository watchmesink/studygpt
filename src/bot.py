import os
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ContextTypes, MessageHandler, CommandHandler, CallbackQueryHandler, filters
import sys
import logging
import mimetypes
from datetime import datetime
from typing import List, Dict

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from .document_processor import DocumentProcessor
from .vector_store import VectorStore, Document
from .query_engine import QueryEngine

logger = logging.getLogger(__name__)

class UserSession:
    def __init__(self):
        self.active_document_id: str = None
        self.in_chat: bool = False

class TelegramBot:
    def __init__(self):
        logger.info("Initializing TelegramBot")
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.query_engine = QueryEngine()
        self.SUPPORTED_MIMES = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        self.user_sessions: Dict[str, UserSession] = {}
        logger.info("TelegramBot initialized successfully")
    
    def get_user_session(self, user_id: str) -> UserSession:
        """Get or create user session."""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = UserSession()
        return self.user_sessions[user_id]
    
    def get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename."""
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    
    def format_document_list(self, documents: List[Document]) -> str:
        """Format document list for display."""
        if not documents:
            return "No documents uploaded yet."
        
        result = "Your documents:\n\n"
        for doc in documents:
            upload_time = doc.upload_time.strftime("%Y-%m-%d %H:%M")
            result += f"📄 {doc.name}\n"
            result += f"   ID: {doc.doc_id}\n"
            result += f"   Uploaded: {upload_time}\n\n"
        return result
    
    def create_document_keyboard(self, documents: List[Document]) -> InlineKeyboardMarkup:
        """Create inline keyboard for document selection."""
        keyboard = []
        for doc in documents:
            keyboard.append([InlineKeyboardButton(
                f"📄 {doc.name}",
                callback_data=f"select_doc_{doc.doc_id}"
            )])
        return InlineKeyboardMarkup(keyboard)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message when /start is issued."""
        user_id = str(update.effective_user.id)
        logger.info(f"Start command received from user {user_id}")
        
        welcome_message = (
            "👋 Welcome to the PDF RAG Bot!\n\n"
            "You can:\n"
            "1. Send me PDF or Word documents (DOC/DOCX)\n"
            "2. Select a document to chat about\n"
            "3. Ask questions about the selected document\n\n"
            "Available commands:\n"
            "/list - Show your documents\n"
            "/finish - End chat session\n"
            "/help - Show all commands\n\n"
            "Try sending a document to get started!"
        )
        await update.message.reply_text(welcome_message)
        
        # Show existing documents if any
        documents = self.vector_store.get_user_documents(user_id)
        if documents:
            await update.message.reply_text(
                "Your available documents:",
                reply_markup=self.create_document_keyboard(documents)
            )
    
    async def list_documents(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list_documents command."""
        user_id = str(update.effective_user.id)
        documents = self.vector_store.get_user_documents(user_id)
        
        if not documents:
            await update.message.reply_text("No documents uploaded yet.")
            return
        
        await update.message.reply_text(
            "Select a document to chat about:",
            reply_markup=self.create_document_keyboard(documents)
        )
    
    async def handle_document_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle document selection via inline keyboard."""
        query = update.callback_query
        user_id = str(query.from_user.id)
        doc_id = query.data.replace("select_doc_", "")
        
        session = self.get_user_session(user_id)
        session.active_document_id = doc_id
        session.in_chat = True
        
        document = self.vector_store.get_document(doc_id)
        
        # Create custom keyboard with "Finish Chat" button
        keyboard = ReplyKeyboardMarkup([["✅ Finish Chat"]], resize_keyboard=True)
        
        await query.message.reply_text(
            f"You are now chatting with: 📄 {document.name}\n"
            "Send your queries below or click 'Finish Chat' when done.",
            reply_markup=keyboard
        )
        await query.answer()
    
    async def finish_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle finish chat request."""
        user_id = str(update.effective_user.id)
        session = self.get_user_session(user_id)
        
        session.active_document_id = None
        session.in_chat = False
        
        documents = self.vector_store.get_user_documents(user_id)
        
        await update.message.reply_text(
            "Chat session ended. Select a document to continue or upload a new one:",
            reply_markup=ReplyKeyboardRemove()
        )
        
        if documents:
            await update.message.reply_text(
                self.format_document_list(documents),
                reply_markup=self.create_document_keyboard(documents)
            )
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle document uploads."""
        user_id = str(update.effective_user.id)
        try:
            logger.info(f"Received document from user {user_id}")
            
            # Check MIME type before downloading
            file_name = update.message.document.file_name
            mime_type = self.get_mime_type(file_name)
            
            if mime_type not in self.SUPPORTED_MIMES:
                logger.warning(f"User {user_id} tried to upload unsupported MIME type: {mime_type}")
                await update.message.reply_text(
                    "❌ Unsupported file type. Please send a PDF or Word document (DOC/DOCX)."
                )
                return
            
            # Download the file
            file_id = update.message.document.file_id
            document_id = str(uuid.uuid4())
            file = await context.bot.get_file(file_id)
            
            # Create user directory if it doesn't exist
            user_dir = os.path.join(Config.UPLOAD_DIR, user_id)
            os.makedirs(user_dir, exist_ok=True)
            
            # Keep original extension
            original_extension = os.path.splitext(file_name)[1]
            file_path = os.path.join(user_dir, f"{document_id}{original_extension}")
            await file.download_to_drive(file_path)
            
            logger.info(f"Downloaded document for user {user_id} to {file_path}")
            
            # Process the document
            await update.message.reply_text("📄 Processing your document...")
            chunks = self.document_processor.process_document(file_path)
            logger.info(f"Processed document into {len(chunks)} chunks")
            
            # Store in vector database
            self.vector_store.add_chunks(chunks, user_id, document_id)
            # Add document metadata
            self.vector_store.add_document(document_id, file_name, user_id)
            logger.info("Stored document in vector database")
            
            # Get updated document list
            documents = self.vector_store.get_user_documents(user_id)
            
            await update.message.reply_text(
                "✅ Document processed successfully!\n"
                "Select a document to start chatting:",
                reply_markup=self.create_document_keyboard(documents)
            )
            
        except Exception as e:
            logger.error(f"Error processing document for user {user_id}: {str(e)}")
            await update.message.reply_text(
                f"❌ Error processing document: {str(e)}"
            )
    
    async def handle_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user questions."""
        user_id = str(update.effective_user.id)
        session = self.get_user_session(user_id)
        
        try:
            # Check if user is in chat session
            if not session.in_chat or not session.active_document_id:
                documents = self.vector_store.get_user_documents(user_id)
                await update.message.reply_text(
                    "Please select a document to chat about:",
                    reply_markup=self.create_document_keyboard(documents)
                )
                return
            
            # Handle "Finish Chat" command
            if update.message.text == "✅ Finish Chat":
                await self.finish_chat(update, context)
                return
            
            query = update.message.text
            logger.info(f"Received query from user {user_id}: {query}")
            
            # Send "thinking" message
            thinking_message = await update.message.reply_text(
                "🤔 Generating response..."
            )
            
            # Get relevant chunks from vector store for the active document
            context_chunks = self.vector_store.query(
                query, user_id, session.active_document_id
            )
            
            if not context_chunks:
                await thinking_message.delete()
                logger.warning(f"No relevant chunks found for user {user_id}")
                await update.message.reply_text(
                    "❌ No relevant information found in the selected document."
                )
                return
            
            # Generate response
            logger.info("Generating response with GPT")
            response = self.query_engine.generate_response(query, context_chunks)
            
            # Delete thinking message and send response
            await thinking_message.delete()
            await update.message.reply_text(
                response,
                parse_mode='Markdown'
            )
            logger.info("Response sent successfully")
            
        except Exception as e:
            logger.error(f"Error processing query for user {user_id}: {str(e)}")
            # Try to delete thinking message if it exists
            try:
                await thinking_message.delete()
            except:
                pass
            await update.message.reply_text(
                f"❌ Error processing query: {str(e)}"
            )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show available commands."""
        help_text = (
            "Available commands:\n\n"
            "/start - Start the bot\n"
            "/list - Show your documents\n"
            "/finish - End current chat session\n"
            "/help - Show this help message\n\n"
            "You can also:\n"
            "• Send PDF or DOC/DOCX files to process\n"
            "• Use buttons to select documents\n"
            "• Ask questions about selected document"
        )
        await update.message.reply_text(help_text)

    async def finish_chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command version of finish chat."""
        await self.finish_chat(update, context)

    def run(self):
        """Run the bot."""
        logger.info("Starting the bot")
        app = Application.builder().token(Config.TELEGRAM_TOKEN).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help))
        app.add_handler(CommandHandler("list", self.list_documents))  # Shorter alias for list_documents
        app.add_handler(CommandHandler("finish", self.finish_chat_command))
        app.add_handler(CallbackQueryHandler(self.handle_document_selection))
        app.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_query))
        
        # Start the bot
        logger.info("Bot is running...")
        app.run_polling() 