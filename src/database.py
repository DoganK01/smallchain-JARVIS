import os
from openai import AzureOpenAI, AsyncAzureOpenAI
from typing import List, Union, Callable, Optional, Any, Dict
import asyncio
from src.settings import settings
from src.text_splitter import CRecursiveTextSplitter
from src.document import Document
import torch

class VectorDatabase:
    def __init__(self, texts: Optional[List[Document]]=None) -> None:
        if (settings.AZURE_OPENAI_API_KEY is None or settings.AZURE_OPENAI_API_VERSION is None or settings.AZURE_OPENAI_ENDPOINT is None):
            raise ValueError(
                "Some of them are missing or set wrong: api_key, api_version, azure_endpoint"
            )
        self.texts = texts
        self.async_client = AsyncAzureOpenAI(api_key=settings.AZURE_OPENAI_API_KEY, api_version=settings.AZURE_OPENAI_API_VERSION, azure_endpoint=settings.AZURE_OPENAI_ENDPOINT)
        self.client = AzureOpenAI(api_key=settings.AZURE_OPENAI_API_KEY, api_version=settings.AZURE_OPENAI_API_VERSION, azure_endpoint=settings.AZURE_OPENAI_ENDPOINT)
        
    async def acreate_embeddings(self, text: Union[str, List[str]], embedding_model_name: str="text-embedding-ada-002") -> Union[List[float], List[List[float]]]:
        if isinstance(text, str):
            embeddings = await self.async_client.embeddings.create(input=text, model=embedding_model_name)
            return embeddings.data[0].embedding
        elif isinstance(text, list) and all(isinstance(item, str) for item in text):
            list_of_embeddings = await self.async_client.embeddings.create(input=text, model=embedding_model_name)
            return [embeddings.embedding for embeddings in list_of_embeddings.data]
        raise ValueError(
            "Type of the input is not supported. It must be string or list of strings."
        )
        
    @classmethod
    async def afrom_documents(cls, documents: List[Document], embedding_model_name: str="text-embedding-ada-002", splitter: CRecursiveTextSplitter=CRecursiveTextSplitter):
        
        texts = [d.page_content for d in documents]
        metadatas = [d.metadata for d in documents]


        return await cls.afrom_text(
            texts=texts,
            metadatas=metadatas,
            embedding_model_name=embedding_model_name,
            splitter=splitter
        )
    
    @classmethod
    async def afrom_text(cls, texts: List[str], embeddig_func: Callable=acreate_embeddings, metadatas: Dict[str, Any]={}, embedding_model_name: str="text-embedding-ada-002", splitter: CRecursiveTextSplitter=CRecursiveTextSplitter):
        docs_list = []
        for id, text in enumerate(texts, start=0):
            chunks = splitter.split_text(text=text)
            embedding = await embeddig_func(text, embedding_model_name)
            doc = Document(page_content=chunks, id=id, metadata=metadatas, embeddings=torch.tensor(embedding))
            docs_list.extend(doc)
        
        return cls(
            texts=docs_list
        )
    
    def process(self, func: Callable = acreate_embeddings):
        pass


if __name__ == "__main__":
    embedding_model = VectorDatabase()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        print(len(loop.run_until_complete(embedding_model.acreate_embeddings("Hello, world!"))))
        print(
            loop.run_until_complete(
                embedding_model.acreate_embeddings(["Hello, world!", "Goodbye, world!"])
            )
        )
    finally:
        loop.close()