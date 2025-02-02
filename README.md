# Telegram RAG Bot

A Telegram bot that processes PDF and Word documents (DOC/DOCX) and answers questions about their content using GPT-4 and vector similarity search.

## Features

- 📄 Document Processing:
  - Supports PDF, DOC, and DOCX files
  - Converts documents to markdown format
  - Preserves text formatting where possible
  - Shows progress bar for large documents

- 🔍 RAG (Retrieval-Augmented Generation):
  - Chunks documents into manageable segments
  - Uses OpenAI's ada-002 for embeddings
  - Stores vectors in ChromaDB
  - Retrieves relevant context for questions

- 🤖 GPT Integration:
  - Uses GPT-4o-mini for responses
  - Provides markdown-formatted answers
  - Context-aware responses based on document content

- 📱 Telegram Interface:
  - Simple upload and query workflow
  - Supports multiple users
  - Provides clear error messages
  - Shows processing status updates

## Setup

1. Install dependencies:
2. Create a `.env` file with your API keys:
3. Run the bot:

## Usage

1. Start the bot in Telegram with `/start`
2. Upload a PDF or Word document
3. Wait for processing confirmation
4. Ask questions about the document content

## Current Constraints

- File Types: Only PDF, DOC, and DOCX supported
- File Size: Limited by Telegram's file size restrictions (50MB)
- Context Window: Maximum of 500 tokens per chunk with 50-token overlap
- Single Document: Currently processes one document at a time per user
- Storage: Local ChromaDB storage (not cloud-based)
- Language: Primarily optimized for English content

## Technical Stack

- **Bot Framework**: python-telegram-bot 20.8
- **Document Processing**: 
  - PyMuPDF 1.23.8 (PDF)
  - python-docx 0.8.11 (DOC/DOCX)
  - docx2txt 0.8 (DOC/DOCX)
- **Vector Store**: ChromaDB 0.4.22
- **Embeddings**: OpenAI text-embedding-ada-002
- **LLM**: GPT-4o-mini
- **Additional Tools**:
  - tiktoken: Token counting
  - tqdm: Progress bars
  - python-dotenv: Environment management

## Logging

The bot includes comprehensive logging:
- Console output for development
- File logging in `bot.log`
- Includes timestamps and log levels
- Tracks:
  - Document uploads and processing
  - Query processing
  - Error handling
  - User interactions

## Future Improvements

- Multi-document support per user
- Cloud storage integration
- Additional file format support (epub, txt)
- Improved text formatting preservation
- Multi-language optimization
- Document metadata extraction
- User document management commands