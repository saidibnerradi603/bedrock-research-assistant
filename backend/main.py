
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import all routes normally
from routes import paper_routes, embed_store_route, chat_routes, ai_analysis_routes,research_route

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Research Paper Analysis System",
    description="AI-powered system for analyzing research papers using RAG (Retrieval-Augmented Generation)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(paper_routes.router)
app.include_router(embed_store_route.router)
app.include_router(chat_routes.router)
app.include_router(ai_analysis_routes.router)
app.include_router(research_route.router)

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Research Paper Analysis System API",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Research Paper Analysis System...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
