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

def log_entry(entry: ScratchpadEntry):
    with open("scratchpad.tmp", "w") as f:
        json.dump(entry.dict(), f)
    os.replace("scratchpad.tmp", "scratchpad.json")