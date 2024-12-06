from setuptools import setup, find_packages

setup(
    name="smallchain",
    version="0.1",
    packages=find_packages(),
    install_requires=[
    "torch",
    "openai",
    "pydantic",
    "PyPDF2",
    "PyMuPDF",
    "pdfplumber",
    "pydantic-settings",
    ],
)
