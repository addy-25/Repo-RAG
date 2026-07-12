import os
import json
from dataclasses import dataclass
from tree_sitter_languages import get_parser

EXTENSION_TO_LANG = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".go": "go",
    ".java": "java",
    ".rb": "ruby",
    ".rs": "rust",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "c_sharp",
    ".sh": "bash",
}


CHUNK_NODE_TYPES = {
    "python": {"function_definition"},
    "javascript": {"function_declaration", "method_definition"},
    "typescript": {"function_declaration", "method_definition"},
    "tsx": {"function_declaration", "method_definition"},
    "go": {"function_declaration", "method_declaration"},
    "java": {"method_declaration"},
    "ruby": {"method"},
    "rust": {"function_item"},
    "c": {"function_definition"},
    "cpp": {"function_definition"},
    "c_sharp": {"method_declaration"},
    "bash": {"function_definition"},
}

NAME_NODE_TYPES = {"identifier", "name", "property_identifier", "field_identifier", "type_identifier"}

WINDOW_SIZE = 50
WINDOW_OVERLAP = 10

_parser_cache = {}

def get_cached_parser(language):
    if language not in _parser_cache:
        _parser_cache[language] = get_parser(language)
    return _parser_cache[language]


@dataclass
class Chunk:
    repo: str
    file_path: str
    language: str
    chunk_type: str
    name: str
    start_line: int
    end_line: int
    code: str
    commit_sha: str


def extract_name(node, source_bytes):
    for child in node.children:
        if child.type in NAME_NODE_TYPES:
            return source_bytes[child.start_byte:child.end_byte].decode("utf-8", errors="replace")
    return None


def treesitter_chunks(text, repo, file_path, language, commit_sha):
    parser = get_cached_parser(language)
    source_bytes = text.encode("utf-8")
    tree = parser.parse(source_bytes)
    boundary_types = CHUNK_NODE_TYPES.get(language, set())
    chunks = []

    def walk(node):
        if node.type in boundary_types:
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            code = source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")
            name = extract_name(node, source_bytes) or f"{node.type}@{start_line}"
            chunks.append(Chunk(
                repo=repo, file_path=file_path, language=language,
                chunk_type=node.type, name=name,
                start_line=start_line, end_line=end_line,
                code=code, commit_sha=commit_sha,
            ))
            return  
        for child in node.children:
            walk(child)

    walk(tree.root_node)
    return chunks


def sliding_window_chunks(text, repo, file_path, language, commit_sha):
    lines = text.splitlines()
    n = len(lines)
    if n == 0:
        return []
    chunks = []
    step = WINDOW_SIZE - WINDOW_OVERLAP
    i = 0
    idx = 0
    while i < n:
        window = lines[i:i + WINDOW_SIZE]
        chunks.append(Chunk(
            repo=repo, file_path=file_path, language=language,
            chunk_type="window", name=f"{os.path.basename(file_path)}#{idx}",
            start_line=i + 1, end_line=min(i + WINDOW_SIZE, n),
            code="\n".join(window), commit_sha=commit_sha,
        ))
        idx += 1
        if i + WINDOW_SIZE >= n:
            break
        i += step
    return chunks


def chunk_file(file_path, repo_name, repo_root, commit_sha):
    ext = os.path.splitext(file_path)[1]
    rel_path = os.path.relpath(file_path, repo_root)

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return []

    language = EXTENSION_TO_LANG.get(ext)

    if language:
        try:
            chunks = treesitter_chunks(text, repo_name, rel_path, language, commit_sha)
            if chunks:
                return chunks
        except Exception:
            pass  

    fallback_language = language or ext.lstrip(".")
    return sliding_window_chunks(text, repo_name, rel_path, fallback_language, commit_sha)