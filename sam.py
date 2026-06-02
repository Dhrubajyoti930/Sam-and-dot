import os
import json
import urllib.request

def main():
    # Authenticate strictly using GEM_KEY_SAM
    api_key = os.environ.get("GEM_KEY_SAM")
    if not api_key:
        print("Error: GEM_KEY_SAM environment variable not found.")
        return

    # 1. Read the fixed tool specification (remains unchanging throughout the run)
    try:
        with open("idea.txt", "r", encoding="utf-8") as f:
            idea = f.read()
    except FileNotFoundError:
        print("Error: idea.txt is missing.")
        return

    model_name = "gemini-3.1-flash-lite" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    # 2. Execute exactly 10 evolutionary cycles sequentially
    for cycle in range(1, 11):
        print(f"--- Starting Gemini Call Cycle {cycle}/10 ---")
        
        # Read the current state of dot.py at the beginning of this specific cycle
        try:
            with open("dot.py", "r", encoding="utf-8") as f:
                current_dot = f.read()
        except FileNotFoundError:
            current_dot = ""

        # Construct the strict prompt using the latest code state
        prompt = (
            f"You are Sam. Your job is to generate the complete, full new code for dot.py based on the fixed tool specification and its previous implementation.\n\n"
            f"Fixed Tool Specification (idea.txt):\n{idea}\n\n"
            f"Previous implementation (dot.py):\n{current_dot}\n\n"
            f"Task: Write the absolute full new code for dot.py implementing the entire specification. Do not truncate anything. Do not leave placeholder comments like '# implement here'. Write every line out completely.\n\n"
            f"CRITICAL CONSTRAINT: Use ONLY the Python Standard Library. Do NOT use or import any external libraries, frameworks, or pip packages. Use only built-in structures.\n"
            f"Output ONLY valid, pure Python code. Do NOT wrap your response in triple-backtick markdown blocks."
        )

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

        # Fetch, process, and immediately save the result for the next loop iteration
        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode("utf-8"))
                new_code = res['candidates'][0]['content']['parts'][0]['text']
                
                # Dynamic backtick cleanup to prevent code block parsing bugs
                triple_backtick = chr(96) * 3
                if new_code.strip().startswith(triple_backtick):
                    lines = new_code.strip().splitlines()
                    if lines[0].startswith(triple_backtick):
                        lines = lines[1:]
                    if lines and lines[-1].startswith(triple_backtick):
                        lines = lines[:-1]
                    new_code = "\n".join(lines)

                # Overwrite dot.py so the next iteration reads this exact output
                with open("dot.py", "w", encoding="utf-8") as f:
                    f.write(new_code.strip() + "\n")
                print(f"Cycle {cycle}/10 complete: dot.py successfully advanced.")
                
        except Exception as e:
            print(f"Error during cycle {cycle}: {e}")
            # Stop the run early if an API call fails to prevent clearing out code blindly
            return

    print("All 10 cycles finished successfully. Ready for commit.")

if __name__ == "__main__":
    main()
