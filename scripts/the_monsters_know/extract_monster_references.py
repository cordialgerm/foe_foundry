#!/usr/bin/env python3
"""
Extract monster references from The Monsters Know blog posts.

This script analyzes blog posts to identify mentions of D&D monsters by comparing
against a comprehensive index of known monster names and variations.
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, NamedTuple, Set, Tuple

from foe_foundry_search.documents import load_monster_document_metas


class MonsterMatch(NamedTuple):
    """Represents a monster match with context."""

    matched_text: str
    position: int
    context_type: str  # 'header' or 'body'
    header_level: int = 0  # For header matches, the level (1-6)


class PostAnalysisResult(NamedTuple):
    """Results for a single post analysis."""

    title: str
    monster_matches: Dict[str, List[MonsterMatch]]


class MonsterExtractor:
    """Extract monster references from text using an optimized monster index."""

    def __init__(self):
        """Initialize the extractor with monster metadata."""
        self.monster_metas = load_monster_document_metas()
        self.monster_index = self._build_monster_index()
        self.compiled_patterns = self._compile_patterns()

    def _build_monster_index(self) -> Dict[str, Set[str]]:
        """
        Build a comprehensive index of monster names and variations.

        Returns:
            Dict mapping normalized names to set of monster keys that match
        """
        index = defaultdict(set)

        for key, meta in self.monster_metas.items():
            # Add the main name
            main_name = meta.name.lower()
            index[main_name].add(key)

            # Add variations
            variations = self._generate_name_variations(meta.name)
            for variation in variations:
                index[variation.lower()].add(key)

        return index

    def _generate_name_variations(self, name: str) -> List[str]:
        """
        Generate common variations of a monster name.

        Args:
            name: Original monster name

        Returns:
            List of name variations
        """
        variations = []
        # Plural forms
        variations.append(self._pluralize(name))

        # Remove duplicates and empty strings
        return [v for v in set(variations) if v and v != name]

    def _pluralize(self, word: str) -> str:
        """Simple pluralization for monster names."""
        word = word.lower()
        if word.endswith("s"):
            return word
        elif word.endswith("y"):
            return word[:-1] + "ies"
        elif word.endswith(("ch", "sh", "x", "z")):
            return word + "es"
        else:
            return word + "s"

    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """
        Compile regex patterns for efficient matching.

        Returns:
            Dict mapping pattern names to compiled regex objects
        """
        patterns = {}

        # Create word boundary patterns for each monster name
        monster_names = list(self.monster_index.keys())

        # Sort by length (longest first) to avoid partial matches
        monster_names.sort(key=len, reverse=True)

        # Group patterns by length for optimization
        short_names = [name for name in monster_names if len(name) <= 10]
        long_names = [name for name in monster_names if len(name) > 10]

        if short_names:
            short_pattern = (
                r"\b(?:" + "|".join(re.escape(name) for name in short_names) + r")\b"
            )
            patterns["short"] = re.compile(short_pattern, re.IGNORECASE)

        if long_names:
            long_pattern = (
                r"\b(?:" + "|".join(re.escape(name) for name in long_names) + r")\b"
            )
            patterns["long"] = re.compile(long_pattern, re.IGNORECASE)

        return patterns

    def extract_monsters_from_text(
        self, text: str
    ) -> Tuple[str, Dict[str, List[MonsterMatch]]]:
        """
        Extract monster references from text, including header analysis.

        Args:
            text: Text to analyze

        Returns:
            Tuple of (title, Dict mapping monster keys to list of MonsterMatch objects)
        """
        results = defaultdict(list)

        # Extract title (first header)
        title_match = re.search(r"^#{1,6}\s+(.+)$", text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Unknown Title"

        # Split text into lines for header analysis
        lines = text.split("\n")
        current_position = 0

        for line_num, line in enumerate(lines):
            # Check if this is a header line
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if header_match:
                header_level = len(header_match.group(1))
                header_text = header_match.group(2).strip()

                # Check for monster matches in header
                self._find_monsters_in_text(
                    header_text,
                    current_position,
                    results,
                    context_type="header",
                    header_level=header_level,
                )
            else:
                # Check for monster matches in body text
                self._find_monsters_in_text(
                    line, current_position, results, context_type="body"
                )

            current_position += len(line) + 1  # +1 for newline

        return title, results

    def _find_monsters_in_text(
        self,
        text: str,
        base_position: int,
        results: Dict[str, List[MonsterMatch]],
        context_type: str = "body",
        header_level: int = 0,
    ):
        """Find monster matches in a piece of text and add to results."""
        text_lower = text.lower()

        # Use compiled patterns for efficient matching
        for pattern_name, pattern in self.compiled_patterns.items():
            for match in pattern.finditer(text_lower):
                matched_text = match.group()
                position = base_position + match.start()

                # Look up which monsters this match corresponds to
                if matched_text in self.monster_index:
                    for monster_key in self.monster_index[matched_text]:
                        monster_match = MonsterMatch(
                            matched_text=matched_text,
                            position=position,
                            context_type=context_type,
                            header_level=header_level,
                        )
                        results[monster_key].append(monster_match)

    def extract_monsters_from_file(
        self, file_path: Path
    ) -> Tuple[str, Dict[str, List[MonsterMatch]]]:
        """
        Extract monster references from a markdown file.

        Args:
            file_path: Path to the markdown file

        Returns:
            Tuple of (title, Dict mapping monster keys to list of MonsterMatch objects)
        """
        try:
            text = file_path.read_text(encoding="utf-8")
            return self.extract_monsters_from_text(text)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return "Unknown Title", {}

    def analyze_blog_posts(self, blog_dir: Path) -> Dict[str, PostAnalysisResult]:
        """
        Analyze all blog posts in a directory.

        Args:
            blog_dir: Directory containing blog post markdown files

        Returns:
            Dict mapping post filenames to PostAnalysisResult objects
        """
        results = {}

        for post_file in blog_dir.glob("post-*.md"):
            print(f"Analyzing {post_file.name}...")
            title, monster_refs = self.extract_monsters_from_file(post_file)
            if monster_refs:
                results[post_file.name] = PostAnalysisResult(
                    title=title, monster_matches=monster_refs
                )

        return results

    def generate_report(self, results: Dict[str, PostAnalysisResult]) -> str:
        """
        Generate a comprehensive report of monster references.

        Args:
            results: Results from analyze_blog_posts

        Returns:
            Formatted report string
        """
        report_lines = []
        report_lines.append("# Monster References in The Monsters Know Blog Posts\n")

        # Summary statistics
        total_posts = len(results)
        total_unique_monsters = len(
            set().union(*[result.monster_matches.keys() for result in results.values()])
        )
        total_references = sum(
            len(matches)
            for result in results.values()
            for matches in result.monster_matches.values()
        )
        total_header_matches = sum(
            len([m for m in matches if m.context_type == "header"])
            for result in results.values()
            for matches in result.monster_matches.values()
        )

        report_lines.append("**Summary:**")
        report_lines.append(f"- Total posts analyzed: {total_posts}")
        report_lines.append(f"- Unique monsters referenced: {total_unique_monsters}")
        report_lines.append(f"- Total monster references: {total_references}")
        report_lines.append(
            f"- Header references (high quality): {total_header_matches}"
        )
        report_lines.append("")

        # Monster frequency analysis
        monster_counts = defaultdict(int)
        monster_header_counts = defaultdict(int)
        for result in results.values():
            for monster_key, matches in result.monster_matches.items():
                monster_counts[monster_key] += len(matches)
                header_matches = [m for m in matches if m.context_type == "header"]
                monster_header_counts[monster_key] += len(header_matches)

        # Top referenced monsters
        top_monsters = sorted(monster_counts.items(), key=lambda x: x[1], reverse=True)[
            :20
        ]
        report_lines.append("## Most Referenced Monsters")
        for monster_key, count in top_monsters:
            monster_meta = self.monster_metas.get(monster_key)
            monster_name = monster_meta.name if monster_meta else monster_key
            header_count = monster_header_counts[monster_key]
            header_indicator = " 🎯" if header_count > 0 else ""
            report_lines.append(
                f"- **{monster_name}** ({monster_key}): {count} references"
                f" ({header_count} in headers){header_indicator}"
            )
        report_lines.append("")

        # Post-by-post breakdown
        report_lines.append("## Post-by-Post Breakdown")
        for post_name in sorted(results.keys()):
            result = results[post_name]
            if not result.monster_matches:
                continue

            report_lines.append(f"### {post_name}")
            report_lines.append(f"**Title:** {result.title}")

            for monster_key, matches in sorted(result.monster_matches.items()):
                monster_meta = self.monster_metas.get(monster_key)
                monster_name = monster_meta.name if monster_meta else monster_key

                # Separate header and body matches
                header_matches = [m for m in matches if m.context_type == "header"]
                body_matches = [m for m in matches if m.context_type == "body"]

                # Build match description
                match_parts = []
                if header_matches:
                    header_texts = [m.matched_text for m in header_matches]
                    unique_header_texts = list(set(header_texts))
                    match_parts.append(f"**Headers: {', '.join(unique_header_texts)}**")

                if body_matches:
                    body_texts = [m.matched_text for m in body_matches]
                    unique_body_texts = list(set(body_texts))
                    match_parts.append(f"Body: {', '.join(unique_body_texts)}")

                total_refs = len(matches)
                header_indicator = " 🎯" if header_matches else ""

                report_lines.append(
                    f"- **{monster_name}** ({total_refs} refs): {'; '.join(match_parts)}{header_indicator}"
                )
            report_lines.append("")

        return "\n".join(report_lines)

    def generate_filtered_references_json(
        self, results: Dict[str, PostAnalysisResult]
    ) -> Dict[str, List[str]]:
        """
        Generate filtered monster references for JSON export.

        Criteria for inclusion:
        - At least 4 references in the source doc AND reference is in top 5 for the post
        - OR the reference is in a header

        Args:
            results: Results from analyze_blog_posts

        Returns:
            Dict mapping post filenames to list of monster keys
        """
        filtered_references = {}

        for post_name, result in results.items():
            if not result.monster_matches:
                continue

            included_monsters = set()

            # Get reference counts for this post
            monster_ref_counts = {
                monster_key: len(matches)
                for monster_key, matches in result.monster_matches.items()
            }

            # Get top 5 most referenced monsters in this post
            top_5_monsters = set(
                monster_key
                for monster_key, _ in sorted(
                    monster_ref_counts.items(), key=lambda x: x[1], reverse=True
                )[:5]
            )

            for monster_key, matches in result.monster_matches.items():
                ref_count = len(matches)
                header_matches = [m for m in matches if m.context_type == "header"]

                # Include if has header match
                if header_matches:
                    included_monsters.add(monster_key)
                # Include if has at least 4 references AND is in top 5 for this post
                elif ref_count >= 4 and monster_key in top_5_monsters:
                    included_monsters.add(monster_key)

            if included_monsters:
                # Convert to monster names for better readability
                monster_names = []
                for monster_key in included_monsters:
                    monster_meta = self.monster_metas.get(monster_key)
                    monster_name = monster_meta.name if monster_meta else monster_key
                    monster_names.append(monster_name)

                filtered_references[post_name] = sorted(monster_names)

        return filtered_references


def main():
    """Main function to run the monster extraction analysis."""
    blog_dir = Path.cwd() / "data" / "the_monsters_know"

    if not blog_dir.exists():
        print(f"Blog directory not found: {blog_dir}")
        return

    print("Initializing monster extractor...")
    extractor = MonsterExtractor()

    print(f"Built index with {len(extractor.monster_index)} monster name variations")
    print(f"Covering {len(extractor.monster_metas)} unique monsters")

    print(f"Analyzing blog posts in {blog_dir}...")
    results = extractor.analyze_blog_posts(blog_dir)

    if not results:
        print("No monster references found in any posts.")
        return

    print("Generating report...")
    report = extractor.generate_report(results)

    # Save report
    report_path = Path.cwd() / "data" / "the_monsters_know" / "_REFERENCES.md"
    report_path.write_text(report, encoding="utf-8")

    print("Generating filtered JSON references...")
    filtered_references = extractor.generate_filtered_references_json(results)

    # Save JSON file
    json_path = Path.cwd() / "data" / "the_monsters_know" / "references.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(filtered_references, f, indent=2, ensure_ascii=False)

    print(f"Report saved to: {report_path}")
    print(f"JSON references saved to: {json_path}")
    print(f"Found monster references in {len(results)} posts")
    print(
        f"Filtered references for {len(filtered_references)} posts with high-quality monster matches"
    )


if __name__ == "__main__":
    main()
