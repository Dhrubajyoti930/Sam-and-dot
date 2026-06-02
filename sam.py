import os
import json
import urllib.request

def main():
    # Authenticate strictly using GEM_KEY_SAM
    api_key = os.environ.get("GEM_KEY_SAM")
    if not api_key:
        print("Error: GEM_KEY_SAM environment variable not found.")
        return

    # 1. Read the fixed tool specification and current dot.py state
    try:
        with open("idea.txt", "r", encoding="utf-8") as f:
            idea = f.read()
    except FileNotFoundError:
        print("Error: idea.txt is missing.")
        return
        
    try:
        with open("dot.py", "r", encoding="utf-8") as f:
            current_dot = f.read()
    except FileNotFoundError:
        current_dot = ""

    # 2. Construct the strict evolutionary prompt passing full context
    # Words are used instead of literal backticks here to prevent markdown parsing errors
    prompt = (
        f"You are Sam. Your job is to generate the complete, full new code for dot.py based on the fixed tool specification and its previous implementation.\n\n"
        f"Fixed Tool Specification (idea.txt):\n{idea}\n\n"
        f"Previous implementation (dot.py):\n{current_dot}\n\n"
        f"Task: Write the absolute full new code for dot.py implementing the entire specification. Do not truncate anything. Do not leave placeholder comments like '# implement here'. Write every line out completely.\n\n"
        f"CRITICAL CONSTRAINT: Use ONLY the Python Standard Library. Do NOT use or import any external libraries, frameworks, or pip packages. Use only built-in structures.\n"
        f"Output ONLY valid, pure Python code. Do NOT wrap your response in triple-backtick markdown blocks."
    )

    # 3. Setup network request to Gemini 3.1 Flash Lite
    model_name = "gemini-3.1-flash-lite" 
    url = f"[https://generativelanguage.googleapis.com/v1beta/models/](https://generativelanguage.googleapis.com/v1beta/models/){model_name}:generateContent?key={api_key}"
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode("utf-8"), 
        headers={"Content-Type": "application/json"}
    )

    # 4. Fetch response and overwrite dot.py without truncation
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            new_code = res['candidates'][0]['content']['parts'][0]['text']
            
            # Defensive post-processing cleanup if markdown tags still slip through
            if new_code.strip().startswith("```"):
                lines = new_code.strip().splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("
```"):
                    lines = lines[:-1]
                new_code = "\n".join(lines)

            # Completely replace dot.py with the full tool code
            with open("dot.py", "w", encoding="utf-8") as f:
                f.write(new_code.strip() + "\n")
            print("dot.py has been successfully updated and evolved into a full tool.")
            
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()
