from setuptools import setup, find_packages

setup(
    name="smallchain",
    version="0.1.0",
    description="A langchain-like project",
    author="Dogan Keskin",
    author_email="dogankeskin33@gmail.com",
    packages=find_packages(),
    license="MIT",
    install_requires=[
        "openai",
        "torch",
        "loguru",
        "rich",
        "termcolor",
        "pydantic>=2.0",
        "pydantic-settings>=2.0",
        "aiohttp",
        "requests",
        "geocoder",
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client",
        "PyPDF2",
        "pymupdf",
        "pdfplumber",
        "pyaudio",
        "pygame",
        "PyQt6",
        "PyQt6-WebEngine",
        "typing-extensions",
        "enum34",
    ],
    extras_require={
        "dev": ["pytest", "black", "flake8", "mypy"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)

