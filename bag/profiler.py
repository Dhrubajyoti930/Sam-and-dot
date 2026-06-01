        self.stats["ask_gemini_calls"] += 1
        self.stats["total_time"] += duration
        self.stats["avg_latency"] = self.stats["total_time"] / self.stats["ask_gemini_calls"]