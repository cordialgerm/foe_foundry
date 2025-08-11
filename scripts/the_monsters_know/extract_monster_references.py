#!/usr/bin/env python3
"""
Extract monster references from The Monsters Know blog posts.

This script analyzes blog posts to identify mentions of D&D monsters by comparing
against a comprehensive index of known monster names and variations.
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

from foe_foundry_search.documents import load_monster_document_metas


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

    def extract_monsters_from_text(self, text: str) -> Dict[str, List[Tuple[str, int]]]:
        """
        Extract monster references from text.

        Args:
            text: Text to analyze

        Returns:
            Dict mapping monster keys to list of (matched_text, position) tuples
        """
        results = defaultdict(list)
        text_lower = text.lower()

        # Use compiled patterns for efficient matching
        for pattern_name, pattern in self.compiled_patterns.items():
            for match in pattern.finditer(text_lower):
                matched_text = match.group()
                position = match.start()

                # Look up which monsters this match corresponds to
                if matched_text in self.monster_index:
                    for monster_key in self.monster_index[matched_text]:
                        results[monster_key].append((matched_text, position))

        return results

    def extract_monsters_from_file(
        self, file_path: Path
    ) -> Dict[str, List[Tuple[str, int]]]:
        """
        Extract monster references from a markdown file.

        Args:
            file_path: Path to the markdown file

        Returns:
            Dict mapping monster keys to list of (matched_text, position) tuples
        """
        try:
            text = file_path.read_text(encoding="utf-8")
            return self.extract_monsters_from_text(text)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return {}

    def analyze_blog_posts(
        self, blog_dir: Path
    ) -> Dict[str, Dict[str, List[Tuple[str, int]]]]:
        """
        Analyze all blog posts in a directory.

        Args:
            blog_dir: Directory containing blog post markdown files

        Returns:
            Dict mapping post filenames to monster extraction results
        """
        results = {}

        for post_file in blog_dir.glob("post-*.md"):
            print(f"Analyzing {post_file.name}...")
            monster_refs = self.extract_monsters_from_file(post_file)
            if monster_refs:
                results[post_file.name] = monster_refs

        return results

    def generate_report(
        self, results: Dict[str, Dict[str, List[Tuple[str, int]]]]
    ) -> str:
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
            set().union(*[refs.keys() for refs in results.values()])
        )
        total_references = sum(
            len(refs) for post_refs in results.values() for refs in post_refs.values()
        )

        report_lines.append("**Summary:**")
        report_lines.append(f"- Total posts analyzed: {total_posts}")
        report_lines.append(f"- Unique monsters referenced: {total_unique_monsters}")
        report_lines.append(f"- Total monster references: {total_references}")
        report_lines.append("")

        # Monster frequency analysis
        monster_counts = defaultdict(int)
        for post_refs in results.values():
            for monster_key, refs in post_refs.items():
                monster_counts[monster_key] += len(refs)

        # Top referenced monsters
        top_monsters = sorted(monster_counts.items(), key=lambda x: x[1], reverse=True)[
            :20
        ]
        report_lines.append("## Most Referenced Monsters")
        for monster_key, count in top_monsters:
            monster_meta = self.monster_metas.get(monster_key)
            monster_name = monster_meta.name if monster_meta else monster_key
            report_lines.append(
                f"- **{monster_name}** ({monster_key}): {count} references"
            )
        report_lines.append("")

        # Post-by-post breakdown
        report_lines.append("## Post-by-Post Breakdown")
        for post_name in sorted(results.keys()):
            post_refs = results[post_name]
            if not post_refs:
                continue

            report_lines.append(f"### {post_name}")
            for monster_key, refs in sorted(post_refs.items()):
                monster_meta = self.monster_metas.get(monster_key)
                monster_name = monster_meta.name if monster_meta else monster_key
                matched_texts = [ref[0] for ref in refs]
                unique_matches = list(set(matched_texts))
                report_lines.append(
                    f"- **{monster_name}** ({len(refs)} refs): {', '.join(unique_matches)}"
                )
            report_lines.append("")

        return "\n".join(report_lines)


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
    report_path = (
        Path.cwd() / "scripts" / "the_monsters_know" / "monster_references_report.md"
    )
    report_path.write_text(report, encoding="utf-8")

    print(f"Report saved to: {report_path}")
    print(f"Found monster references in {len(results)} posts")


if __name__ == "__main__":
    main()
