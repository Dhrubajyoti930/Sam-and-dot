import json
import re

class ContextSynthesizer:
    """
    Handles compression of unstructured data and robust extraction of JSON from raw text.
    """

    def compress_text(self, raw_text: str) -> str:
        """
        Compresses large streams of text by removing duplicate lines, 
        excessive whitespaces, and common boilerplate patterns.
        
        Args:
            raw_text: The noisy text to compress.
        Returns:
            A cleaned, dense string or an empty string on failure.
        """
        try:
            if not isinstance(raw_text, str) or not raw_text.strip():
                return ""
            
            lines = raw_text.splitlines()
            seen = set()
            cleaned = []
            
            for line in lines:
                # Remove excessive whitespace
                stripped = " ".join(line.split())
                if stripped and stripped not in seen:
                    cleaned.append(stripped)
                    seen.add(stripped)
            
            return " ".join(cleaned)
        except Exception:
            return ""

    def extract_json(self, raw_string: str) -> dict:
        """
        Locates, extracts, and parses JSON objects within noisy strings.
        Handles leading/trailing noise, markdown blocks, and trailing commas.
        
        Args:
            raw_string: The string containing hidden JSON.
        Returns:
            A parsed dictionary or an empty dict on failure.
        """
        try:
            if not isinstance(raw_string, str) or not raw_string:
                return {}
            
            # Find the boundaries of the JSON object
            start = raw_string.find('{')
            end = raw_string.rfind('}')
            
            if start == -1 or end == -1 or start >= end:
                return {}
            
            json_str = raw_string[start:end+1]
            
            # Remove common trailing commas that violate standard JSON
            json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
            
            return json.loads(json_str)
        except Exception:
            return {}

class PromptOptimizer:
    """
    Provides utilities to structure and enforce constraints on prompts for LLMs.
    """

    def enforce_strict_json(self, base_prompt: str, keys: list) -> str:
        """
        Appends explicit system instructions to force raw JSON output 
        without markdown wrapping or conversational filler.
        
        Args:
            base_prompt: The initial prompt.
            keys: A list of keys required in the JSON object.
        Returns:
            The augmented prompt string.
        """
        try:
            key_str = ", ".join(keys)
            instruction = (
                f"\n\nSTRICT OUTPUT FORMAT:\n"
                f"You must return ONLY a raw JSON object containing exactly these keys: {key_str}.\n"
                f"Do not use markdown code blocks (e.g., no ```json). "
                f"Do not provide any preamble, explanation, or conversational filler. "
                f"Output strictly the JSON object."
            )
            return f"{base_prompt}{instruction}"
        except Exception:
            return base_prompt

    def structure_chain_of_thought(self, task_description: str) -> str:
        """
        Transforms a simple task string into a structured multi-phase 
        prompt layout (Analysis -> Verification -> Final Output).
        
        Args:
            task_description: The core task to be performed.
        Returns:
            A structured prompt layout.
        """
        try:
            return (
                f"TASK: {task_description}\n\n"
                "To ensure the highest accuracy, follow this reasoning process:\n"
                "1. ANALYSIS: Deconstruct the task requirements, context, and identify critical constraints.\n"
                "2. VERIFICATION: Critically review the logic for potential errors, omissions, or edge cases.\n"
                "3. FINAL OUTPUT: Provide the definitive result based on the verified logic."
            )
        except Exception:
            return task_description

class SystemSanitizer:
    """
    Cleans model outputs to ensure machine-readability by removing artifacts.
    """

    def clean_code_blocks(self, output_text: str) -> str:
        """
        Detects and strips out backticks, language markers (e.g., ```python), 
        and trailing conversational filler.
        
        Args:
            output_text: The raw output from the model.
        Returns:
            A clean string containing only the target text.
        """
        try:
            if not isinstance(output_text, str) or not output_text:
                return ""
            
            # Remove markdown code block markers and optional language specifiers
            # Handles ```json, ```python, ```, etc.
            clean = re.sub(r'```[a-zA-Z]*\n?', '', output_text)
            clean = clean.replace('```', '')
            
            return clean.strip()
        except Exception:
            return str(output_text) if output_text else ""
