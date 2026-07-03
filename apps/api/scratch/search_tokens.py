import os


def search_files(directory, query):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                path = os.path.join(root, file)
                try:
                    with open(path, encoding='utf-8') as f:
                        content = f.read()
                        if query in content:
                            print(f"Found '{query}' in: {path}")
                except Exception:
                    pass

search_files('c:\\Users\\praka\\OneDrive\\Documents\\My dashboard\\apps\\web\\src', 'localStorage')
search_files('c:\\Users\\praka\\OneDrive\\Documents\\My dashboard\\apps\\web\\src', 'token')
