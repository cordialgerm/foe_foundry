from .monsters import Monsters

if __name__ == "__main__":
    print("Caching monsters...")
    Monsters.generate_cache()
    print("Monsters cached.")
