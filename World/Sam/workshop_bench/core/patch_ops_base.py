

from abc import ABC, abstractmethod

class PatchOperation(ABC):
    @abstractmethod
    def apply(self, content: str) -> str: pass
    @abstractmethod
    def verify(self, content: str) -> bool: pass
    @abstractmethod
    def rollback(self, content: str) -> str: pass

class ReplaceOp(PatchOperation):
    def __init__(self, old: str, new: str):
        self.old = old
        self.new = new
    def execute(self, content: str) -> str:
        return content.replace(self.old, self.new)

class DeleteOp(PatchOperation):
    def __init__(self, old: str):
        self.old = old
    def execute(self, content: str) -> str:
        return content.replace(self.old, "")

class InsertOp(PatchOperation):
    def __init__(self, anchor: str, new: str):
        self.anchor = anchor
        self.new = new
    def execute(self, content: str) -> str:
        return content.replace(self.anchor, self.anchor + self.new)