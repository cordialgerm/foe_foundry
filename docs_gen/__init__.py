from .families import generate_families_index
from .monsters import generate_monsters_with_no_lore
from .powers import generate_all_powers
from .topics import generate_topics_index


def generate_pages():
    generate_topics_index()
    generate_families_index()
    generate_all_powers()
    generate_monsters_with_no_lore()
