import json

transcript_path = r"C:\Users\praka\.gemini\antigravity\brain\cd0f4294-89eb-4004-b03e-0d17c3678e9b\.system_generated\logs\transcript_full.jsonl"

with open(transcript_path, encoding='utf-8') as f:
    for i, line in enumerate(f):
        try:
            data = json.loads(line)
            if data.get('type') == 'USER_INPUT':
                content = data.get('content', '')
                print(f"Line {i} USER: {content}")
        except Exception:
            pass
