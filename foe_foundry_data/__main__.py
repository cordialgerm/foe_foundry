from .monster_families import MonsterFamilies
from .monsters import Monsters

if __name__ == "__main__":
    print("Caching monsters...")
    Monsters.generate_cache()
    print("Monsters cached.")
    
    print("Caching monster families...")
    MonsterFamilies.generate_cache()
    print("Monster families cached.")
