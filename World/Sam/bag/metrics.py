"""
Performance metrics for Sam's operational cycles.
"""
from dataclasses import dataclass, field
from typing import Dict
import time
import json
from pathlib import Path

@dataclass
class PhaseMetrics:
    phase: str
    duration_seconds: float
    api_calls: int
    tokens_used: int = 0

class CycleMetrics:
    def __init__(self, log_path: Path = None):
        self.phases: Dict[str, PhaseMetrics] = {}
        self.cycle_start = time.time()
        self.log_path = log_path
        self.current_phase_start = None
        self.current_phase_name = None
        self.api_calls_in_phase = 0

    def start_phase(self, name: str):
        self.current_phase_name = name
        self.current_phase_start = time.time()
        self.api_calls_in_phase = 0

    def end_phase(self):
        if self.current_phase_name:
            duration = time.time() - self.current_phase_start
            self.phases[self.current_phase_name] = PhaseMetrics(
                self.current_phase_name, duration, self.api_calls_in_phase
            )
            self.current_phase_name = None

    def record_api_call(self):
        self.api_calls_in_phase += 1

    def summary(self) -> dict:
        total_duration = time.time() - self.cycle_start
        total_calls = sum(p.api_calls for p in self.phases.values())

        summ = {
            'total_duration_seconds': round(total_duration, 2),
            'total_api_calls': total_calls,
            'phases': {p: vars(m) for p, m in self.phases.items()},
        }

        if self.log_path:
            try:
                with open(self.log_path, 'a') as f:
                    f.write(json.dumps(summ) + "\n")
            except Exception as e:
                pass
        return summ

