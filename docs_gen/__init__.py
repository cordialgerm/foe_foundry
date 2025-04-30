from .families import generate_families_index
from .monsters import generate_monster_index
from .topics import generate_topics_index


def generate_pages():
    generate_monster_index()
    generate_topics_index()
    # generate_blog_topics()
    generate_families_index()
