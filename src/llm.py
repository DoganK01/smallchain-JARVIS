import os
from openai import AzureOpenAI, AsyncAzureOpenAI
from typing import List, Union, Callable, Optional, Any, Dict, TypeVar, Type, AnyStr
import asyncio
from src.runnables import Runnable
from src.settings import settings
from src.prompts import SYSTEM_PROMPT

class AzureChatOpenAI(Runnable):
    def __init__(self, api_key: Optional[str]=settings.AZURE_OPENAI_GPT_API_KEY, 
                 api_version: Optional[str]=settings.AZURE_OPENAI_GPT_API_VERSION,
                 endpoint: Optional[str]=settings.AZURE_OPENAI_GPT_ENDPOINT):
        
        super().__init__()
        
        self._client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )

    def process(self, data):
        return self.chat.completions.create(model="gpt-4o-attention-project",
                                            messages=[{"role":"system", "content":"You are a helpful assistant",
                                                      "role":"user", "content":data}]).choices[0].message.content

    def __getattr__(self, name):
        """
        Delegate attribute access to the internal AsyncAzureOpenAI client.

        Args:
            name (str): The name of the attribute.

        Returns:
            Any: The value of the attribute.
        """
        return getattr(self._client, name)
    
    def __repr__(self):
        return repr(self.client)
    
if __name__ == "__main__":
    llm = AzureChatOpenAI()
    response= llm.chat.completions.create(model="gpt-4o-attention-project",
                                    messages=[{"role":"system", "content":"You are a helpful assistant."},
                                                {"role":"user", "content":"How far away is the moon from the earth?"}])

    #print(response)

    print(response.choices[0].message.content)

