import os
from openai import AzureOpenAI, AsyncAzureOpenAI
from typing import List, Union, Callable, Optional, Any, Dict, TypeVar, Type
import asyncio
from src.runnables import Runnable
from src.settings import settings
from src.text_splitter import CRecursiveTextSplitter
from src.document import Document
from src.cosine_sim import cosine_similarity
import torch

VDB = TypeVar("VDB", bound="VectorDatabase")

class VectorDatabase(Runnable):
    def __init__(self, texts: Optional[List[Document]]=None, k: Optional[int]=5) -> None:
        super().__init__()
        self.texts = texts
        self.k = k
        #self.async_client = AsyncAzureOpenAI(api_key=settings.AZURE_OPENAI_API_KEY, api_version=settings.AZURE_OPENAI_API_VERSION, azure_endpoint=settings.AZURE_OPENAI_ENDPOINT)
        #self.client = AzureOpenAI(api_key=settings.AZURE_OPENAI_API_KEY, api_version=settings.AZURE_OPENAI_API_VERSION, azure_endpoint=settings.AZURE_OPENAI_ENDPOINT)
        
    def acreate_embeddings(self, text: Union[str, List[str]], embedding_model_name: str="text-embedding-ada-002") -> Union[List[float], List[List[float]]]:
        if (settings.AZURE_OPENAI_API_KEY is None or settings.AZURE_OPENAI_API_VERSION is None or settings.AZURE_OPENAI_ENDPOINT is None):
            raise ValueError(
                "Some of them are missing or set wrong: api_key, api_version, azure_endpoint"
            )
        async_client = AzureOpenAI(api_key=settings.AZURE_OPENAI_API_KEY, api_version=settings.AZURE_OPENAI_API_VERSION, azure_endpoint=settings.AZURE_OPENAI_ENDPOINT)
        if isinstance(text, str):
            embeddings = async_client.embeddings.create(input=text, model=embedding_model_name)
            return torch.Tensor(embeddings.data[0].embedding)
        elif isinstance(text, list) and all(isinstance(item, str) for item in text):
            list_of_embeddings = async_client.embeddings.create(input=text, model=embedding_model_name)
            return [torch.Tensor(embeddings.embedding) for embeddings in list_of_embeddings.data]
        raise ValueError(
            "Type of the input is not supported. It must be string or list of strings."
        )
        
    @classmethod
    async def afrom_documents(cls: Type[VDB], documents: List[Document], embedding_model_name: str="text-embedding-ada-002", splitter: Optional[CRecursiveTextSplitter] = None) -> VDB:
        
        texts = [d.page_content for d in documents]
        metadatas = [d.metadata for d in documents]


        return await cls.afrom_text(
            texts=texts,
            metadatas=metadatas,
            embedding_model_name=embedding_model_name,
            splitter=splitter
        )
    
    @classmethod
    async def afrom_text(cls: Type[VDB], texts: List[str], embeddig_func: Callable=acreate_embeddings, metadatas: Dict[str, Any]={}, embedding_model_name: str="text-embedding-ada-002", splitter: Optional[CRecursiveTextSplitter] = None) -> VDB:

        if splitter is None:
            splitter = CRecursiveTextSplitter(chunk_size=200, chunk_overlap=0)
        
        docs_list = []
        for id, (text, metadata) in enumerate(zip(texts, metadatas), start=0):
            chunks = splitter.split_text(text=text)
            for chunk in chunks:
                embedding = embeddig_func(chunk, embedding_model_name)
                doc = Document(page_content=chunk, id=id, metadata=metadata, embeddings=torch.tensor(embedding))
                docs_list.append(doc)
        
        return cls(
            texts=docs_list
        )
    
    def as_retriever(self, k=5):
        return VectorDatabase(
            texts = self.texts,
            k = k
        )

    
    def process(self, question, *args, **kwargs):
        """
        Find the closest Document using its embedding to the question based on cosine similarity.

        
        Args:
            question (string): Question for vector database to be queried.
        
            
        Returns:
                
        """
        similarities = []
        question_embedding = self.acreate_embeddings(question)


        for doc in self.texts:
            similarity = cosine_similarity(question_embedding, doc.embeddings)
            similarities.append((doc, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)

        final_context = "\n\n".join(doc[0].page_content for doc in similarities)
        return "\n\n".join(doc[0].page_content for doc in similarities)


if __name__ == "__main__":
    embedding_model = VectorDatabase()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        print(loop.run_until_complete(embedding_model.acreate_embeddings("Hello, world!")))
        print(
            loop.run_until_complete(
                embedding_model.acreate_embeddings(["Hello, world!", "Goodbye, world!"])
            )
        )
    finally:
        loop.close()