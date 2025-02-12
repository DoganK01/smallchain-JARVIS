
# smallchain - JARVIS

![image](https://github.com/user-attachments/assets/e508c596-1405-4046-881a-9d3424743752)


## Project Demo

Click on the image to watch the video on YouTube

[![Watch the video](https://img.youtube.com/vi/U6dkOt4xzGk/0.jpg)](https://www.youtube.com/watch?v=U6dkOt4xzGk)


## JARVIS
Introducing the ultimate all-in-one AI-powered assistant, designed to revolutionize the way you manage your day-to-day life and tasks. Powered by GPT-4, this intelligent system goes beyond basic commands—it's a highly responsive, conversational companion that truly understands your needs and anticipates your next move.

Imagine having the power of Text-to-Speech (TTS) and Speech-to-Text (STT), allowing you to interact hands-free, whether you're on the go or relaxing at home. The assistant effortlessly transcribes your spoken words and responds in natural, human-like language, giving you the freedom to multitask while staying connected.

Need to know if you should carry an umbrella? This custom weather tool delivers real-time, hyper-local forecasts to ensure you're always prepared for whatever nature throws at you. Plus, it integrates with Google Maps to offer an interactive, step-by-step roadmap tool, guiding you through every twist and turn of your journey, whether you're driving, walking, or taking public transit.

Communication has never been easier with Google Gmail integration. You can read, compose, and send emails instantly, without needing to open multiple apps or tabs. Stay on top of your inbox, no matter where you are, with just a voice command or a simple click.

Your calendar just became smarter too. With Google Calendar integration, you can effortlessly view your upcoming events, insert new ones, and manage your schedule with ease. Never miss a meeting, appointment, or personal event again as this assistant keeps you in sync with your most important dates.

This project isn't just about technology; it's about transforming how you interact with your world. It's a sleek, dynamic fusion of voice interaction, AI intelligence, and cutting-edge tools that make your life more efficient, organized, and fun. Whether you’re managing your day, navigating through the city, or staying in touch with friends and colleagues, this assistant is your ultimate sidekick. It’s not just smart—it's an extension of you, working seamlessly in the background to make life easier and cooler.

## smallchain
Introducing a lightweight library inspired by Langchain, designed to bring the power of Retrieval Augmented Generation (RAG) to your applications. This simple yet effective framework integrates external knowledge sources into your AI’s response generation, making it smarter and more contextually aware. It’s ideal for building chatbots, virtual assistants, or other NLP applications, offering easy integration and scalability. With this tool, you can enhance your AI models with real-time data retrieval, enabling them to generate more relevant and accurate outputs. It’s a practical, efficient solution for developers looking to implement RAG without the complexity.


## Configurations:

**Azure Openai** API Key: GPT-4o API Key Deployed on Azure

**Azure Openai** API Version: API Version for GPT-4o Deployed on Azure

**Azure Openai** Endpoint: Endpoint for GPT-4o Deployed on Azure

**Weather API Key**: API Key for OpenWeatherMap. You can get an OpenWeatherMap API Key by signing up on the OpenWeatherMap website, creating an account, navigating to the "API Keys" section, and generating a new key.

**Google Credentials Path**:  JSON file that contains authentication details, such as client ID, client secret, and access tokens, allowing applications to authenticate and interact with Google Cloud services securely.
You can get it by creating a service account in the Google Cloud Console, assigning necessary roles, generating a JSON key, and downloading it from the "Keys" section under "Service Accounts."

**Google Maps API Key**: The Google Maps API Key is a unique identifier that authenticates requests to Google Maps services, enabling access to features like geocoding, directions, and places. 
You can get a Google Maps API Key by creating a project in the Google Cloud Console, enabling the required Maps APIs, generating an API key under "Credentials," and restricting it for security.

**Azure Openai TTS Endpoint**: Endpoint for TTS-1 Deployed on Azure

**Azure Openai TTS API Key**: TTS-1 API Key Deployed on Azure

**Azure Openai TTS API Version**: API Version for TTS-1 Deployed on Azure

**Azure Openai Whisper Endpoint**: Endpoint for Whisper-1 Deployed on Azure

**Azure Openai Whisper API Key**: Whisper API Key Deployed on Azure

**Azure Openai Whisper API Version**: API Version for Whisper Deployed on Azure

And then create a .env file. You can see an example as ".env.copy" in the repository. Popule the file.

## Installation and Running the code

1. To install the project dependencies using Poetry, run the following command:
```bash
poetry install
```
2. Run the app_tools.py or app_rag.py (app_tolls.py for JARVIS and app_rag.py file for simple RAG)
```bash
poetry run python app_tools.py
```
## TO-DO:

- [ ] Combine RAG from smallchain and custom tools to enhance JARVIS capability
