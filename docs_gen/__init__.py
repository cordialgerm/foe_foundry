from .families import generate_families_index
from .powers import generate_all_powers
from .topics import generate_topics_index


def generate_pages():
    generate_topics_index()
    generate_families_index()
    generate_all_powers()
