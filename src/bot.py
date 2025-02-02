import os
import uuid
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, CommandHandler, filters
import sys
import logging
import mimetypes

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from .document_processor import DocumentProcessor
from .vector_store import VectorStore
from .query_engine import QueryEngine

logger = logging.getLogger(__name__)

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
        logger.info("TelegramBot initialized successfully")
    
    def get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename."""
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message when /start is issued."""
        user_id = update.effective_user.id
        logger.info(f"Start command received from user {user_id}")
        welcome_message = (
            "👋 Welcome to the PDF RAG Bot!\n\n"
            "You can:\n"
            "1. Send me a PDF file to process\n"
            "2. Ask questions about your uploaded documents\n\n"
            "Try sending a PDF to get started!"
        )
        await update.message.reply_text(welcome_message)
    
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
            logger.info("Stored chunks in vector database")
            
            await update.message.reply_text(
                "✅ Document processed successfully!\n"
                "You can now ask questions about it."
            )
            
        except Exception as e:
            logger.error(f"Error processing document for user {user_id}: {str(e)}")
            await update.message.reply_text(
                f"❌ Error processing document: {str(e)}"
            )
    
    async def handle_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user questions."""
        user_id = str(update.effective_user.id)
        try:
            query = update.message.text
            logger.info(f"Received query from user {user_id}: {query}")
            
            # Get relevant chunks from vector store
            context_chunks = self.vector_store.query(query, user_id)
            
            if not context_chunks:
                logger.warning(f"No relevant chunks found for user {user_id}")
                await update.message.reply_text(
                    "❌ No relevant information found. Have you uploaded a PDF?"
                )
                return
            
            # Generate response
            logger.info("Generating response with GPT")
            response = self.query_engine.generate_response(query, context_chunks)
            
            # Send response
            await update.message.reply_text(
                response,
                parse_mode='Markdown'
            )
            logger.info("Response sent successfully")
            
        except Exception as e:
            logger.error(f"Error processing query for user {user_id}: {str(e)}")
            await update.message.reply_text(
                f"❌ Error processing query: {str(e)}"
            )
    
    def run(self):
        """Run the bot."""
        logger.info("Starting the bot")
        app = Application.builder().token(Config.TELEGRAM_TOKEN).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_query))
        
        # Start the bot
        logger.info("Bot is running...")
        app.run_polling() 