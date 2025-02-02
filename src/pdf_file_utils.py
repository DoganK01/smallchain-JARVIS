from abc import ABC
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import os
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import pdfplumber
import base64
from io import BytesIO

import os
import sys

# Set the working directory to the project root (adjust this path to your needs)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(project_root)

# Add 'src' directory to sys.path explicitly
sys.path.append(os.path.join(project_root, 'src'))

from src.document import Document



class PDFDocumentLoader:

    def __init__(self, file_path: str):
        """
        Setting self.file_path to file_path variable.

        :param file_path: The path to the PDF file.
        :return: Nothing.
        """
        self.file_path = file_path


    def load(self) -> list[Document]:
        """
        Load a PDF file and create a Document object from its content, metadata, images, tables, and annotations.

        :return: A Document object containing the text, metadata, images, tables, and annotations.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"The file '{self.file_path }' does not exist.")
        
        metadata = {}

        page_content = self.extract_text(self.file_path )
        
        metadata = self.extract_metadata(self.file_path )

        images = self.extract_images(self.file_path )
        metadata["images"] = images if images else []

        tables = self.extract_tables(self.file_path )
        metadata["tables"] = tables if tables else []

        annotations = self.extract_annotations(self.file_path )
        metadata["annotations"] = annotations if annotations else []
        return [Document(
            page_content=page_content,
            metadata=metadata
        )]

    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extract text from the PDF. Raise an error if text is not found.
        """
        reader = PdfReader(file_path)
        page_content = "\n".join(page.extract_text() for page in reader.pages)
        
        if not page_content.strip():
            raise ValueError("No text content found in the PDF.")
        
        return page_content

    @staticmethod
    def extract_metadata(file_path: str) -> dict:
        """
        Extract metadata from the PDF and return it as a dictionary.
        """
        reader = PdfReader(file_path)
        metadata = reader.metadata

        if not metadata:
            raise ValueError("No metadata found in the PDF.")

        metadata_info = {key: value for key, value in metadata.items()}

        metadata_info["file_name"] = os.path.basename(file_path)
        metadata_info["num_pages"] = len(reader.pages)

        return metadata_info

    @staticmethod
    def extract_images(file_path: str) -> list:
        """
        Extract images from the PDF. Return an empty list if no images are found.
        """
        doc = fitz.open(file_path)
        images = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                img_ext = base_image["ext"]

                img_base64 = base64.b64encode(image_bytes).decode("utf-8")
                images.append({
                    "image_base64": img_base64,
                    "image_format": img_ext,
                    "page": page_num + 1
                })

        return images

    @staticmethod
    def extract_tables(file_path: str) -> list:
        """
        Extract tables from the PDF. Return an empty list if no tables are found.
        """
        tables = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                for table in page_tables:
                    tables.append(table)

        return tables

    @staticmethod
    def extract_annotations(file_path: str) -> list:
        """
        Extract annotations from the PDF. Return an empty list if no annotations are found.
        """
        doc = fitz.open(file_path)
        annotations = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            for annot in page.annots():
                annot_data = annot.info
                annotations.append({
                    "author": annot_data.get("title", ""),
                    "date": annot_data.get("modDate", ""),
                    "type": annot_data.get("subtype", ""),
                    "contents": annot_data.get("contents", ""),
                    "page": page_num + 1
                })

        return annotations
    


if __name__ == "__main__":
    loader = PDFDocumentLoader(file_path=r"C:\Users\Nazlı\Desktop\smallchain\Soru Bankası.pdf"
                            )
    document = loader.load()


    # Access the content and metadata from the loaded document
    #print(document[0].page_content)
    print(type(document[0].metadata))

    #print(document)