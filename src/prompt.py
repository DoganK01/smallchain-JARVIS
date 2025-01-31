from src.runnables import Runnable
from string import Formatter


class BasePromptTemplate(Runnable):

    def __init__(self, template=None, next=None):
        super().__init__(next=next)
        self.template = template

    @staticmethod
    def from_template(template):
        return BasePromptTemplate(template)
    
    def _format_prompt(self, **kwargs):
        return self.template.format(**kwargs)
    
    def process(self, data):
        #print("FROM PROMPT CLASS:      ", self._format_prompt(**data))
        return self._format_prompt(**data)
    
    def get_template_variables(self, ):
        return sorted({
            v for _, v, _, _ in Formatter().parse(self.template) if v is not None
        })


class ChatPromptTemplate(BasePromptTemplate):
    def __init__(self, template, next=None):
        super().__init__(template=template, next=next)


    @staticmethod
    def from_template(template):
        return ChatPromptTemplate(template)




if __name__ == "__main__":
    # Define a template string for ChatPromptTemplate
    chat_template_str = "Chat with {username}: {message}"

    # Create an instance of ChatPromptTemplate using from_template
    chat_template = ChatPromptTemplate.from_template(chat_template_str)
    print(chat_template.template)
    # Now, you can process some data through the template
    chat_data = {"username": "Alice", "message": "Hello there!"}
    chat_result = chat_template.process(chat_data)

    
