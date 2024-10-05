from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import query, chat, db_structure, rag_query
from config import ORIGINS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router)
app.include_router(chat.router)
app.include_router(db_structure.router)
app.include_router(rag_query.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)