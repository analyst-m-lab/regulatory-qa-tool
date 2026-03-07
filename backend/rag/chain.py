from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

class RAGChain:
    def __init__(self, data_folder: str, embedding_model: str, api_key: str):
        self.data_folder = data_folder
        self.api_key = api_key
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.vector_store = None
        self.retriever = None
        self.llm = None
    
    async def initialize(self):
        """ベクターストアの初期化"""
        try:
            # 1. データロード
            documents = self._load_documents()
            print(f"📄 ロードしたドキュメント数: {len(documents)}")
            
            if len(documents) == 0:
                print("⚠️ ドキュメントが見つかりません")
                return
            
            # 2. テキスト分割
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", "。", "、", " ", ""]
            )
            splits = text_splitter.split_documents(documents)
            print(f"✂️ 分割したチャンク数: {len(splits)}")
            
            # 3. ベクター化＆ストア作成
            self.vector_store = FAISS.from_documents(splits, self.embeddings)
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
            
            # 4. LLM初期化
            self.llm = ChatAnthropic(
                api_key=self.api_key,
                model="claude-sonnet-4-6",
                temperature=0.7
            )
            
            print("✅ RAGチェーン初期化完了")
            
        except Exception as e:
            print(f"❌ 初期化エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_documents(self):
        """dataフォルダからテキストファイルをロード"""
        documents = []
        data_path = Path(self.data_folder)
        
        if not data_path.exists():
            print(f"⚠️ {self.data_folder} が見つかりません")
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
                print(f"✓ {file_path.name} をロード")
            except Exception as e:
                print(f"⚠️ {file_path} の読み込みエラー: {e}")
        
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
            # 関連ドキュメントを検索
            docs = self.retriever.invoke(question)
            
            # コンテキスト作成
            context = "\n".join([doc.page_content for doc in docs])
            
            # プロンプト作成
            prompt = f"""以下の参考資料に基づいて、質問に答えてください。

参考資料:
{context}

質問: {question}

回答:"""
            
            # LLMで回答生成
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