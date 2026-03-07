from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(tags=["regulatory-qa"])

class QueryRequest(BaseModel):
    question: str
    lang: str = "ja"

@router.post("/query")
async def query_document(req: QueryRequest, request: Request):
    """ナレッジベースから検索して回答"""
    rag_chain = request.app.state.rag_chain

    if not rag_chain:
        raise HTTPException(status_code=503, detail="RAGチェーン未初期化")

    result = await rag_chain.query(req.question)
    return result

@router.get("/status")
async def status(request: Request):
    """サーバーステータス確認"""
    rag_chain = request.app.state.rag_chain

    return {
        "status": "ok",
        "rag_initialized": rag_chain is not None and rag_chain.retriever is not None and rag_chain.llm is not None
    }
