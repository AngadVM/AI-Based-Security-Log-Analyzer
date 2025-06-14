from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def parse(self, line: str) -> dict:
        pass

