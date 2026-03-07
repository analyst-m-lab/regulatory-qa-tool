import traceback
from pathlib import Path
from langchain_anthropic import ChatAnthropic
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi


class BM25Retriever:
    """オフライン対応のBM25キーワード検索リトリーバー"""

    def __init__(self, documents: list, k: int = 5):
        self.documents = documents
        self.k = k
        tokenized = [doc.page_content.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)

    async def ainvoke(self, query: str) -> list:
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:self.k]
        return [self.documents[i] for i in top_indices]


class RAGChain:
    def __init__(self, data_folder: str, embedding_model: str, api_key: str):
        self.data_folder = data_folder
        self.api_key = api_key
        self.retriever = None
        self.llm = None

    async def initialize(self):
        """BM25リトリーバーとLLMの初期化"""
        try:
            documents = self._load_documents()
            print(f"ロードしたドキュメント数: {len(documents)}")

            if len(documents) == 0:
                print("ドキュメントが見つかりません")
                return

            self.retriever = BM25Retriever(documents, k=5)

            self.llm = ChatAnthropic(
                api_key=self.api_key,
                model="claude-sonnet-4-6",
                temperature=0.7
            )

            print("RAGチェーン初期化完了")

        except Exception as e:
            print(f"初期化エラー: {e}")
            traceback.print_exc()

    def _load_documents(self):
        """dataフォルダからテキストファイルをロード"""
        documents = []
        data_path = Path(self.data_folder)

        if not data_path.exists():
            print(f"{self.data_folder} が見つかりません")
            return documents

        for file_path in data_path.glob("**/*.txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                documents.append(
                    Document(
                        page_content=content,
                        metadata={"source": str(file_path), "filename": file_path.name}
                    )
                )
                print(f"ロード: {file_path.name}")
            except Exception as e:
                print(f"読み込みエラー {file_path}: {e}")

        return documents

    async def query(self, question: str) -> dict:
        """RAGによる質問応答"""
        if not self.retriever or not self.llm:
            return {
                "answer": "RAGチェーンが初期化されていません。",
                "sources": [],
                "success": False
            }

        try:
            docs = await self.retriever.ainvoke(question)

            context = "\n\n".join([doc.page_content for doc in docs])

            prompt = f"""以下の参考資料に基づいて、質問に答えてください。

参考資料:
{context}

質問: {question}

回答:"""

            result = await self.llm.ainvoke(prompt)

            return {
                "answer": result.content,
                "sources": [doc.metadata for doc in docs],
                "success": True
            }
        except Exception as e:
            return {
                "answer": f"エラーが発生しました: {str(e)}",
                "sources": [],
                "success": False,
                "error": str(e)
            }
