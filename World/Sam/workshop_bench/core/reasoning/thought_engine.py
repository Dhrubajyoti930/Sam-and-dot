from pydantic import BaseModel
from enum import Enum
import json

"""
Problem: Transient reasoning state.
Solution: Persistent JSON scratchpad via Pydantic.
Cleanup: Archive to history/ directory upon task completion.
"""
import os

class Status(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"

class ScratchpadEntry(BaseModel):
    timestamp: str
    task_id: str
    action: str
    status: Status
    reasoning_summary: str

    def __format__(self, format_spec: str) -> str:
        try:
            if format_spec == "summary":
                return f"{self.task_id}: {self.status.value}"
            if format_spec == "full":
                return self.json()
            return str(self)
        except Exception:
            return object.__format__(self, format_spec)

def log_entry(entry: ScratchpadEntry):
    with open("scratchpad.tmp", "w") as f:
        json.dump(entry.dict(), f)
    os.replace("scratchpad.tmp", "scratchpad.json")