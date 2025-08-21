# LLM-friendly grep tool for searching monster markdown files
import re
from pathlib import Path
from typing import List, Optional

from langchain_core.tools import tool
from pydantic import BaseModel


# Pydantic model for search results
class MonsterGrepResult(BaseModel):
    file: str
    line: int
    match: str
    context: List[str]


def to_markdown(self) -> str:
    """
    Format the search result as markdown for LLM contexts.
    """
    md = f"## {self.file} Line {self.line}\n"
    md += f"**Match:**\n```\n{self.match}\n```\n"
    if self.context:
        md += "\n".join(self.context)
        md += "\n"
    return md


def _find_monster_markdown_dirs() -> List[Path]:
    """
    Returns a list of directories likely to contain monster markdown files.
    """
    return [
        Path.cwd() / "docs/monsters",
        Path.cwd() / "data/5e_artisinal_monsters",
        Path.cwd() / "data/5e_canonical",
    ]


@tool
def grep_monster_markdown(
    query: str,
    regex: bool = False,
    file_filter: Optional[str] = None,
    context_lines: int = 2,
) -> List[MonsterGrepResult]:
    """
    Search monster markdown files for a keyword or regex pattern.
    Args:
        query: The search string or regex pattern.
        regex: If True, treat query as regex.
        file_filter: Optional substring or pattern to filter filenames.
        context_lines: Number of context lines before/after match to include.
    Returns:
        List of MonsterGrepResult objects.
    """
    dirs = _find_monster_markdown_dirs()
    results: List[MonsterGrepResult] = []
    pattern = re.compile(query) if regex else None
    for d in dirs:
        if not d.is_dir():
            continue
        for path in d.rglob("*.md"):
            if file_filter and file_filter not in path.name:
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
                for i, line in enumerate(lines):
                    found = False
                    if regex and pattern and pattern.search(line):
                        found = True
                    elif not regex and query in line:
                        found = True
                    if found:
                        context = []
                        if context_lines > 0:
                            start = max(0, i - context_lines)
                            end = min(len(lines), i + context_lines + 1)
                            context = [
                                context_line for context_line in lines[start:end]
                            ]
                        results.append(
                            MonsterGrepResult(
                                file=str(path),
                                line=i + 1,
                                match=line,
                                context=context,
                            )
                        )
            except Exception:
                continue
    return results


"""
Example usage:
results = grep_monster_markdown("dragon", regex=False, context_lines=2)
for r in results:
	print(r)
"""
