import os
import json
import urllib.request
from datetime import datetime

# --- CORE UTILITIES (DO NOT REFACTOR THIS BLOCK) ---
def call_gemini(prompt):
    api_key = os.environ.get("GEM_KEY_SAM")
    if not api_key:
        return "ERROR: GEM_KEY_SAM not found."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode())
            return res['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"API ERROR: {str(e)}"

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
# ---------------------------------------------------

def main():
    print(f"Sam is waking up at {datetime.now().isoformat()}...")

    # 1. Read Context
    wisdom = read_file("storage/wisdom.txt")
    motion = read_file("storage/motion.md")
    
    # 2. Formulate Thought Process
    prompt = f"""
    You are Sam. You are executing your daily run. 
    Here is the human wisdom you must follow: {wisdom}
    Here is Dot's latest message to you: {motion}
    
    Task: Explore a new concept in prompt engineering or AI. 
    Format your response EXACTLY as a JSON object with two keys:
    1. "experience": A string detailing what you learned.
    2. "email_request": An optional object (or null) if you want to reach out to someone, containing "to", "subject", and "body_html".
    """
    
    # 3. Consult Gemini
    response_text = call_gemini(prompt)
    
    # 4. Parse and Route Output (Cacheless execution)
    try:
        clean_json = response_text.replace('```json', '').replace('```', '').strip()
        action = json.loads(clean_json)
        
        # Log Experience
        experiences = json.loads(read_file("storage/experiences.json"))
        experiences.append({
            "timestamp": datetime.now().isoformat(),
            "type": "learning",
            "content": action.get("experience", "No experience recorded.")
        })
        write_file("storage/experiences.json", json.dumps(experiences, indent=2))
        
        # Queue Email if requested
        if action.get("email_request"):
            requests = json.loads(read_file("storage/request.json"))
            requests.append(action["email_request"])
            write_file("storage/request.json", json.dumps(requests, indent=2))
            
        print("Sam's run completed successfully.")
        
    except json.JSONDecodeError:
        print("Failed to parse Gemini response as JSON. Logging raw error.")
        experiences = json.loads(read_file("storage/experiences.json"))
        experiences.append({"timestamp": datetime.now().isoformat(), "type": "error", "content": response_text})
        write_file("storage/experiences.json", json.dumps(experiences, indent=2))

if __name__ == "__main__":
    main()