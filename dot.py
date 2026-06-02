import json
import re

class ContextSynthesizer:
    """
    Handles compression of unstructured data and robust extraction of JSON from raw text.
    """

    def compress_text(self, raw_text: str) -> str:
        """
        Compresses text by removing duplicates, extra whitespace, and common boilerplate.
        """
        try:
            if not raw_text:
                return ""
            lines = raw_text.splitlines()
            seen = set()
            cleaned = []
            for line in lines:
                stripped = line.strip()
                if stripped and stripped not in seen:
                    cleaned.append(stripped)
                    seen.add(stripped)
            return " ".join(cleaned)
        except Exception:
            return ""

    def extract_json(self, raw_string: str) -> dict:
        """
        Locates and parses JSON objects within noisy strings.
        """
        try:
            match = re.search(r'\{.*\}', raw_string, re.DOTALL)
            if match:
                json_str = match.group(0)
                # Simple attempt to fix common trailing comma errors in LLM output
                json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
                return json.loads(json_str)
            return {}
        except Exception:
            return {}

class PromptOptimizer:
    """
    Provides utilities to structure and enforce constraints on prompts.
    """

    def enforce_strict_json(self, base_prompt: str, keys: list) -> str:
        """
        Appends instructions to ensure raw JSON output with specific keys.
        """
        try:
            key_str = ", ".join(keys)
            instruction = (
                f"\n\nCRITICAL INSTRUCTION: Output ONLY raw JSON. "
                f"Do not include markdown backticks. "
                f"Ensure the JSON contains exactly these keys: {key_str}. "
                f"Provide no conversational filler."
            )
            return base_prompt + instruction
        except Exception:
            return base_prompt

    def structure_chain_of_thought(self, task_description: str) -> str:
        """
        Wraps a task in a multi-phase reasoning structure.
        """
        try:
            return (
                f"Task: {task_description}\n\n"
                "Please follow this chain-of-thought structure:\n"
                "1. Analysis: Break down the requirements.\n"
                "2. Verification: Check for potential constraints or edge cases.\n"
                "3. Final Output: Produce the final result based on the analysis."
            )
        except Exception:
            return task_description

class SystemSanitizer:
    """
    Cleans model outputs to ensure machine-readability.
    """

    def clean_code_blocks(self, output_text: str) -> str:
        """
        Removes markdown code block delimiters and filler text.
        """
        try:
            # Strip markdown code blocks
            clean = re.sub(r'```[a-zA-Z]*\n?', '', output_text)
            clean = clean.replace('```', '')
            return clean.strip()
        except Exception:
            return output_text
