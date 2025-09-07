from .families import Families
from .monsters import Monsters

if __name__ == "__main__":
    print("Caching monsters...")
    Monsters.generate_cache()
    print("Monsters cached.")
    
    print("Caching families...")
    Families.generate_cache()
    print("Families cached.")
