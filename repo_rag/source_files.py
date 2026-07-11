import os

DIR_BLACKLIST = {
    ".git", "node_modules", "venv", ".venv", "__pycache__",
    "dist", "build", "coverage", ".next", "target", ".storybook",
    ".vscode", ".github", "site-packages", "egg-info", "instance",
}

FILE_BLACKLIST = {
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", ".DS_Store",
}

CODE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".rb", ".php",
    ".rs", ".c", ".cpp", ".h", ".hpp", ".cs", ".svelte", ".vue",
    ".sql", ".sh", ".md", ".ipynb",
}

MAX_FILE_SIZE = 1_000_000  # 1MB

def find_source_files(repo_path):
    results = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in DIR_BLACKLIST]
        for fname in files:
            if fname in FILE_BLACKLIST:
                continue
            ext = os.path.splitext(fname)[1]
            if ext not in CODE_EXTENSIONS:
                continue
            fpath = os.path.join(root, fname)
            try:
                if os.path.getsize(fpath) > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue
            results.append(fpath)
    return results