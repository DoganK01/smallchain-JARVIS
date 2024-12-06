from abc import ABC, abstractmethod

class Runnable(ABC):
    def __init__(self, next=None):
        self.next = next

    @abstractmethod
    def process(self, data):
        """
        This method must be implemented by subclasses to define
        data processing behavior.
        """
        pass

    def invoke(self, data):
        processed_data = self.process(data)
        if self.next is not None:
            return self.next.invoke(processed_data)
        return processed_data

    def __or__(self, other):
        return RunnableSequence(self, other)

class RunnableSequence(Runnable):
    def __init__(self, first, second):
        super().__init__()
        self.first = first
        self.second = second

    def process(self, data):
        return data

    def invoke(self, data):
        first_result = self.first.invoke(data)
        return self.second.invoke(first_result)
    

class DictTransformer(Runnable):
    def __init__(self, mapping):
        super().__init__()
        self.mapping = mapping

    def process(self, data):
        result = {}
        for key, runnable in self.mapping.items():
            result[key] = runnable.invoke(data)
        return result

class RunnablePassthrough(Runnable):
    def process(self, data):
        return data