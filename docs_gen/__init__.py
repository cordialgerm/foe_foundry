import os
from concurrent.futures import ProcessPoolExecutor, as_completed

from .families import generate_families_index
from .monsters import generate_monsters_with_no_lore
from .powers import generate_all_powers
from .topics import generate_topics_index


def _generate_topics():
    """Wrapper function for multiprocessing."""
    generate_topics_index()
    return "topics"

def _generate_families():
    """Wrapper function for multiprocessing."""
    generate_families_index()
    return "families"

def _generate_powers():
    """Wrapper function for multiprocessing."""
    generate_all_powers()
    return "powers"

def _generate_monsters():
    """Wrapper function for multiprocessing."""
    generate_monsters_with_no_lore()
    return "monsters"


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
    
    # Use multiprocessing to generate pages in parallel
    generators = [_generate_topics, _generate_families, _generate_powers, _generate_monsters]
    
    try:
        with ProcessPoolExecutor(max_workers=4) as executor:
            # Submit all tasks
            future_to_name = {executor.submit(gen): gen.__name__ for gen in generators}
            
            # Collect results as they complete
            for future in as_completed(future_to_name):
                gen_name = future_to_name[future]
                try:
                    result = future.result()
                    print(f"Completed generating {result} pages")
                except Exception as exc:
                    print(f"Generation of {gen_name} failed with exception: {exc}")
                    # Fall back to sequential generation on error
                    print("Falling back to sequential generation...")
                    generate_topics_index()
                    generate_families_index()
                    generate_all_powers()
                    generate_monsters_with_no_lore()
                    break
    except Exception as e:
        print(f"Multiprocessing failed: {e}")
        print("Falling back to sequential generation...")
        generate_topics_index()
        generate_families_index()
        generate_all_powers()
        generate_monsters_with_no_lore()
    
    print("Dynamic page generation completed.")
