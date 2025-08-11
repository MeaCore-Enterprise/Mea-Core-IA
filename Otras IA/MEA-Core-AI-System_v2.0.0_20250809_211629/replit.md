# Overview

MEA-Core is an advanced local AI assistant system inspired by Jarvis, operating entirely offline with custom-built neural networks and machine learning algorithms. The system features a complete information retrieval pipeline, intelligent document classification, semantic analysis, intent recognition, and personalized learning capabilities. It provides a sophisticated web-based interface with multimodal interaction support (text, voice, gestures) and real-time AI analysis.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Information Retrieval Engine
The system implements a custom BM25 (Best Matching 25) ranking algorithm for document scoring and retrieval. The retrieval pipeline consists of:

- **Custom Tokenization**: Simple regex-based tokenizer optimized for Spanish and English text
- **Document Chunking**: Overlapping text segmentation with configurable chunk sizes and overlap ratios
- **BM25 Indexing**: Full implementation of the BM25 ranking function with inverted index and term frequency statistics
- **Query Learning**: Rocchio feedback algorithm for query expansion and pseudo-relevance feedback

## Data Storage Architecture
The system uses a file-based storage approach with JSONL (JSON Lines) format:

- **documents.jsonl**: Document metadata and content storage
- **chunks.jsonl**: Processed text chunks with indexing metadata
- **index.json**: Serialized BM25 index with vocabulary and posting lists
- **feedback.json**: User feedback signals for continuous learning

This design choice prioritizes simplicity and transparency over performance, making the system easily debuggable and portable.

## Web Interface
Flask-based web application with:

- **Single-page application**: HTML/CSS/JavaScript frontend with real-time chat interface
- **RESTful API**: JSON endpoints for document upload, search, and system status
- **Progress tracking**: Real-time processing status for document ingestion
- **Responsive design**: Jarvis-inspired dark theme with cyan accent colors

## Document Processing Pipeline
Multi-format document ingestion with:

- **PDF extraction**: Uses pdfminer.six for text extraction from PDF files
- **Text preprocessing**: Sentence splitting and overlap-based chunking
- **Incremental indexing**: Documents are processed and indexed individually
- **Background processing**: Threading support for non-blocking document processing

## Advanced AI Capabilities

### Neural Network System
- **Intent Classification**: Custom neural network for understanding query intentions (question, request, command, analysis)
- **Incremental Learning**: Real-time adaptation to user preferences and feedback patterns
- **Personality Engine**: Customizable AI personality traits (helpfulness, formality, creativity, technical depth)
- **Learning System**: Continuous improvement from user interactions and feedback signals

### Document Intelligence
- **Smart Classification**: Automatic categorization of documents (legal, medical, technical, financial, educational)
- **Semantic Analysis**: Entity extraction, relationship detection, and key phrase identification
- **Intelligent Grouping**: Dynamic result organization based on content similarity and context

### Advanced Interactions
- **Voice Processing**: Speech-to-text and text-to-speech capabilities with voice command recognition
- **Gesture Recognition**: Support for gesture-based navigation and interaction
- **HUD Display**: Holographic-style heads-up display mode for immersive interaction
- **Multimodal Interface**: Seamless integration of text, voice, and gesture inputs

## Query Processing and Response Generation
The system implements advanced query processing with personalized ranking:

- **Query expansion**: Automatic query enhancement using pseudo-relevance feedback
- **Intent recognition**: Neural classification of query types and user intentions
- **Personalized ranking**: BM25 scoring enhanced with user preference learning
- **Semantic enhancement**: Entity extraction and key phrase identification
- **Enhanced summarization**: Context-aware response generation with personality formatting
- **Relevance feedback**: Multi-signal learning from explicit and implicit user feedback

# External Dependencies

## Python Libraries
- **Flask 3.0.3**: Web framework for API and frontend serving
- **pdfminer.six 20231228**: PDF text extraction library

## Frontend Assets
- **Font Awesome 6.4.0**: Icon library for UI elements
- **Google Fonts**: Orbitron, Rajdhani, and Roboto Mono for typography

## Runtime Requirements
- **Python 3.7+**: Core runtime environment
- **File system access**: Local storage for data persistence
- **Web browser**: Modern browser with JavaScript support for frontend

The system is designed to be completely self-contained with minimal external dependencies, ensuring it can run offline without internet connectivity or cloud services.