import sys
import json
import time
from pathlib import Path

PERF_FILE = Path(__file__).parent / "performance.json"

class SamProfiler:
    def __init__(self):
        self.stats = {"ask_gemini_calls": 0, "total_time": 0.0}
        try:
            self.monitor = sys.monitoring.use_tool_id(sys.monitoring.DEBUGGER_ID, "SamProfiler")
        except AttributeError:
            self.monitor = None

    def log_call(self, duration: float):
        self.stats["ask_gemini_calls"] += 1
        self.stats["total_time"] += duration
        
    def save(self):
        PERF_FILE.write_text(json.dumps(self.stats))