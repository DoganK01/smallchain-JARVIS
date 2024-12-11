from src.pdf_file_utils import PDFDocumentLoader
from src.database import VectorDatabase
from src.prompt import ChatPromptTemplate
from src.runnables import DictTransformer, RunnablePassthrough

import asyncio

async def main():
    file_path = r"C:\Users\Nazlı\Desktop\smallchain\deneme.pdf"
    loader = PDFDocumentLoader(file_path)
    
    docs = loader.load() 

    vectorstore = await VectorDatabase.afrom_documents(docs)

    retriever = vectorstore.as_retriever()

    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    retrieval_chain = DictTransformer({"context": retriever, "question": RunnablePassthrough()}) | prompt
    

    result = retrieval_chain.invoke("where did harrison work?")
    print(result)

if __name__ == "__main__":
    asyncio.run(main()) 