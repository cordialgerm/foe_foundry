import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List

import mkdocs_gen_files

from .families import generate_families_content, generate_families_index
from .monsters import (
    generate_monsters_with_no_lore,
    generate_monsters_with_no_lore_content,
)
from .powers import generate_all_powers, generate_all_powers_content
from .topics import generate_topics_content, generate_topics_index
from .types import FilesToGenerate


def write_content_results(results: List[FilesToGenerate]):
    """Write content results that were generated in worker processes."""
    for result in results:
        for filename, content in result.files.items():
            with mkdocs_gen_files.open(filename, "w") as f:
                f.write(content)
            print(f"Wrote {filename} from multiprocessing result {result.name}")


def generate_pages():
    dev_mode = int(os.environ.get("DEV_MODE", 0))
    if dev_mode:
        print("Dev mode is on, skipping dynamic page generation.")
        return

    # Performance optimization: Skip expensive page generation in fast builds
    fast_build = os.environ.get("FAST_BUILD", "false").lower() == "true"
    skip_generation = os.environ.get("SKIP_PAGE_GENERATION", "false").lower() == "true"

    if fast_build or skip_generation:
        print("Fast build mode: skipping dynamic page generation for performance.")
        return

    print("Generating dynamic pages with multiprocessing...")

    # All generators now return FilesToGenerate
    generators = [
        generate_topics_content,
        generate_families_content,
        generate_all_powers_content,
        generate_monsters_with_no_lore_content,
    ]

    try:
        # Run content generators in parallel worker processes
        with ProcessPoolExecutor(max_workers=min(4, len(generators))) as executor:
            future_to_name = {executor.submit(gen): gen.__name__ for gen in generators}

            results = []
            for future in as_completed(future_to_name):
                gen_name = future_to_name[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"Completed generating {result.name} content")
                except Exception as exc:
                    print(
                        f"Content generation of {gen_name} failed with exception: {exc}"
                    )
                    raise  # Re-raise to trigger fallback

        # Write all content results in main process
        write_content_results(results)

    except Exception as e:
        print(f"Multiprocessing/generation failed: {e}")
        print("Falling back to sequential generation...")
        generate_topics_index()
        generate_families_index()
        generate_all_powers()
        generate_monsters_with_no_lore()

    print("Dynamic page generation completed.")
