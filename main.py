from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import medical_documents_generator, query, chat, db_structure, rag_query, web_search, transcribe_pdf, transcribe_image, rag_query_v2, health_report
from config import ORIGINS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router)
app.include_router(chat.router)
app.include_router(db_structure.router)
app.include_router(rag_query.router)
app.include_router(web_search.router)
app.include_router(transcribe_pdf.router)
app.include_router(transcribe_image.router)
app.include_router(rag_query_v2.router)
app.include_router(health_report.router)
app.include_router(medical_documents_generator.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)