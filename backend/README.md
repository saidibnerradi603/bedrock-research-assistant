# Research Paper Analysis System - Backend

## Overview

A comprehensive AI-powered backend system for analyzing research papers using **AWS Bedrock**, **Retrieval-Augmented Generation (RAG)**, and **LangGraph** for autonomous research. The system processes PDF documents, extracts content using OCR, generates embeddings, stores vectors in Pinecone, and provides intelligent chat capabilities with research papers.

## Architecture

![alt text](../frontend/assets/Architecture_Diagram.png)

## AWS Services Integration

### 1. AWS Bedrock (Primary AI Engine)

The system leverages AWS Bedrock for all AI-powered operations:

#### Models Used:

**Amazon Nova Premier v1** (`us.amazon.nova-pro-v1:0`)
- Purpose: Primary LLM for chat, analysis, and document generation
- Use Cases:
  - Research paper summarization
  - Quiz question generation
  - Mind map creation
  - RAG-based Q&A
  - LangGraph research agent reasoning
- Configuration: `backend/config/settings.py`

**Amazon Titan Embeddings v2** (`amazon.titan-embed-text-v2:0`)
- Purpose: Generate vector embeddings for semantic search
- Dimensions: 1024
- Use Cases:
  - Converting text chunks to vectors
  - Semantic similarity search
  - RAG retrieval
- Configuration: `backend/config/settings.py`

#### Implementation Details:

**LLM Service** (`backend/services/llm_service.py`):
Uses `ChatBedrockConverse` from `langchain_aws` for chat completions with Nova Premier model.

**Embedding Service** (`backend/services/embedding_service.py`):
Uses `BedrockEmbeddings` from `langchain_aws` for generating 1024-dimensional vectors with Titan Embeddings v2.

#### Key Features:
- Structured Output: Uses Bedrock's structured output capabilities for JSON responses
- Streaming Support: Ready for streaming responses (can be enabled)
- LangChain Integration: Seamless integration with LangChain ecosystem
- Region Configuration: Configurable AWS region (default: `us-east-1`)

### 2. AWS S3 (Document Storage)

S3 serves as the primary storage layer for all document-related data.

#### Bucket Structure:
```
research-paper-analysis/
├── raw_pdfs/
│   └── {paper_id}/
│       └── {filename}.pdf
├── parsed_markdown/
│   └── {paper_id}/
│       └── paper.md
└── hash_index/
    └── {file_hash}.txt
```

#### S3 Client Implementation (`backend/utils/s3_client.py`):
Boto3-based client with automatic bucket creation and comprehensive file operations.

#### Operations:
- Upload: Store raw PDFs and parsed markdown
- Download: Retrieve documents for processing
- Presigned URLs: Generate temporary URLs for OCR processing
- Duplicate Detection: Hash-based indexing to prevent reprocessing
- Auto-creation: Automatically creates bucket if it doesn't exist

#### Use Cases:
1. Raw PDF Storage: Original uploaded files
2. Markdown Storage: OCR-processed content
3. Hash Index: SHA256 hashes for duplicate detection
4. Presigned URLs: Secure temporary access for Mistral OCR

### 3. AWS Credentials Configuration

#### Environment Variables (.env):
```bash
ACCESS_KEY_ID="your-aws-access-key-id"
SECRET_ACCESS_KEY="your-aws-secret-access-key"
AWS_DEFAULT_REGION="us-east-1"
```

#### Required IAM Permissions:
- Bedrock: InvokeModel, InvokeModelWithResponseStream
- S3: PutObject, GetObject, DeleteObject, ListBucket, CreateBucket, HeadBucket, HeadObject

## System Components

### Core Services

#### 1. Paper Service (`backend/services/paper_service.py`)
- Purpose: Handle PDF upload, processing, and duplicate detection
- AWS Integration: S3 for storage, presigned URLs for OCR
- Features:
  - SHA256 hash-based duplicate detection
  - Mistral OCR integration via presigned URLs
  - Automatic markdown extraction and storage
  - Paper status tracking

#### 2. Embedding Service (`backend/services/embedding_service.py`)
- Purpose: Generate vector embeddings using AWS Bedrock
- Model: Amazon Titan Embeddings v2
- Output: 1024-dimensional vectors
- Integration: LangChain BedrockEmbeddings wrapper

#### 3. LLM Service (`backend/services/llm_service.py`)
- Purpose: Provide access to AWS Bedrock chat models
- Model: Amazon Nova Premier v1
- Features:
  - Standard chat completion
  - Structured output support
  - Streaming capability (optional)

#### 4. Vector Store Service (`backend/services/vector_store_service.py`)
- Purpose: Manage Pinecone vector database
- Features:
  - Auto-create index with AWS region specification
  - Batch document insertion
  - Duplicate paper detection
  - Metadata filtering for paper-specific queries

#### 5. Chat Service (`backend/services/chat_service.py`)
- Purpose: RAG-based Q&A system
- AWS Integration: Bedrock for LLM, Titan for embeddings
- Features:
  - Paper-specific queries
  - Cross-paper search
  - Context-aware responses with citations
  - Configurable retrieval (top_k)

#### 6. AI Analysis Service (`backend/services/ai_analysis_service.py`)
- Purpose: Advanced paper analysis using Bedrock
- Features:
  - Comprehensive Summaries: 9-field structured analysis
  - Quiz Generation: MCQ with explanations
  - Mind Maps: Interactive Markmap visualizations
- AWS Integration: Nova Premier for all analysis tasks

### LangGraph Research Agent

#### Architecture (`backend/agent/`)

The system includes an autonomous research agent built with LangGraph:

**Graph Structure** (`backend/agent/graph.py`):
```
START → Planning → Reasoning → [Search/Analysis/Generate] → END
                      ↑              ↓
                      └──────────────┘
```

**Nodes**:
- Planning: Create research strategy
- Reasoning: Analyze progress and decide next action
- Search: Query Tavily/Perplexity APIs
- Analysis: Extract evidence from results
- Document Generation: Create final report using Bedrock

**AWS Bedrock Integration**:
- Uses Nova Premier for all reasoning and generation tasks
- Structured prompts for ReAct-style reasoning
- Autonomous decision-making for research flow

#### Key Features:
- Autonomous multi-step research
- Web search integration (Tavily + Perplexity)
- Evidence collection and synthesis
- Professional markdown report generation
- Configurable iteration limits and quality thresholds

### Synchronous Embedding Processing

Embedding generation is now handled synchronously through the API:
- Direct processing without background workers
- Immediate response with results
- Simplified deployment (no Redis/Celery required)

## API Endpoints

### Paper Management
- `POST /api/papers/upload-and-process`: Upload PDF and extract content
- `GET /api/papers/{paper_id}/status`: Check paper processing status
- `POST /api/papers/embed-store`: Generate embeddings and store in vector database

### AI Analysis
- `GET /api/papers/{paper_id}/summary`: Generate comprehensive summary
- `GET /api/papers/{paper_id}/quiz`: Generate quiz questions
- `GET /api/papers/{paper_id}/mindmap`: Generate interactive mind map

### Chat & QA
- `POST /api/chat/query`: RAG-based Q&A (paper-specific or all papers)
- `POST /api/chat/query-paper/{paper_id}`: Query specific paper

### Research Agent
- `POST /api/research/query`: Autonomous web research with report generation

## Data Flow

### 1. Paper Upload & Processing
```
PDF Upload → S3 (raw_pdfs) → Presigned URL → Mistral OCR → 
Markdown → S3 (parsed_markdown) → Hash Index → Response
```

### 2. Embedding Generation (Synchronous)
```
Paper ID → Download Markdown → Chunk Text → 
AWS Bedrock (Titan Embeddings) → Pinecone Storage → Complete
```

### 3. RAG Query
```
User Question → AWS Bedrock (Titan Embeddings) → Pinecone Search → 
Retrieve Chunks → AWS Bedrock (Nova Premier) → Answer + Citations
```

### 4. AI Analysis
```
Paper ID → S3 Download → AWS Bedrock (Nova Premier) → 
Structured Output → Summary/Quiz/Mindmap → Response
```

### 5. Research Agent
```
Query → Planning (Bedrock) → Search (Tavily/Perplexity) → 
Analysis (Bedrock) → Evidence Collection → 
Document Generation (Bedrock) → Markdown Report
```

## Configuration

### Settings (`backend/config/settings.py`)

**AWS Configuration**:
- `access_key_id`: AWS access key 
- `secret_access_key`: AWS secret key 
- `aws_default_region`: AWS region (default: us-east-1)
- `bedrock_chat_model`: Nova Premier model ID
- `bedrock_embedding_model`: Titan Embeddings model ID
- `embedding_dimension`: 1024

**S3 Configuration**:
- `s3_bucket_name`: research-paper-analysis
- `s3_raw_pdf_prefix`: raw_pdfs
- `s3_parsed_markdown_prefix`: parsed_markdown
- `s3_hash_index_prefix`: hash_index

**Chunking Configuration**:
- `chunk_size`: 1500 characters
- `chunk_overlap`: 200 characters

**Pinecone Configuration**:
- `pinecone_api_key`: Pinecone API key
- `pinecone_index_name`: aws-pdf-index



## Dependencies

### Core Frameworks:
- FastAPI: Web framework
- LangChain: LLM orchestration
- LangGraph: Agent workflow

### AWS Integration:
- boto3: AWS SDK
- langchain-aws: Bedrock integration

### Vector Database:
- pinecone: Vector storage
- langchain-pinecone: Pinecone integration

### External Services:
- mistralai: OCR processing
- tavily-python: Web search
- perplexityai: AI search

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Start FastAPI server:
```bash
python main.py
```

## AWS Bedrock Best Practices

### 1. Model Selection
- Use Nova Premier for complex reasoning and analysis
- Use Titan Embeddings v2 for consistent vector generation
- Consider model costs and latency for your use case

### 2. Error Handling
- Implement retry logic for transient failures
- Handle rate limiting gracefully
- Log all Bedrock API calls for debugging

### 3. Cost Optimization
- Cache embeddings to avoid regeneration
- Use duplicate detection to prevent reprocessing
- Batch operations when possible
- Monitor token usage

### 4. Security
- Use IAM roles instead of access keys in production
- Implement least privilege access
- Rotate credentials regularly
- Use VPC endpoints for private connectivity

### 5. Performance
- Use async processing for embedding generation
- Implement connection pooling
- Cache frequently accessed data
- Monitor Bedrock quotas and limits

## Monitoring & Logging

All services include comprehensive logging:
- Paper processing status
- Embedding generation progress
- Bedrock API calls
- S3 operations
- Error tracking

Logs include:
- Timestamps
- Service names
- Log levels (INFO, WARNING, ERROR)
- Detailed error messages

## Troubleshooting

### Common Issues:

**Bedrock Access Denied**:
- Verify IAM permissions
- Check model availability in your region
- Ensure credentials are correct

**S3 Bucket Not Found**:
- System auto-creates bucket
- Verify S3 permissions
- Check bucket name configuration

**Embedding Generation Fails**:
- Check Pinecone API key
- Verify AWS Bedrock access
- Check markdown file exists in S3

**RAG Queries Return No Results**:
- Verify paper is embedded
- Check Pinecone index exists
- Verify paper_id is correct

## Future Enhancements

- Multi-region Bedrock deployment
- S3 lifecycle policies for cost optimization
- CloudWatch integration for monitoring
- AWS Lambda for serverless processing
- Amazon Kendra integration for enterprise search
- Bedrock Agents for advanced workflows
