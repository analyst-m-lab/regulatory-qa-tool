from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

from api.routes import router
from rag.chain import RAGChain

@asynccontextmanager
async def lifespan(app: FastAPI):
    # スタートアップ
    api_key = os.getenv("ANTHROPIC_API_KEY")
    data_folder = os.getenv("DATA_FOLDER", "../data")
    embedding_model = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")

    print(f"初期化開始...")
    print(f"   API Key: {'設定済み' if api_key else '未設定'}")
    print(f"   Data folder: {data_folder}")

    rag_chain = RAGChain(
        data_folder=data_folder,
        embedding_model=embedding_model,
        api_key=api_key
    )
    await rag_chain.initialize()
    app.state.rag_chain = rag_chain

    yield

    print("サーバー停止")

app = FastAPI(
    title="OTC Regulatory AI Backend",
    description="本格RAG・ベクター検索対応",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "OTC Regulatory AI Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
