import os
import sys

import dotenv
import uvicorn

from foe_foundry_search import setup_indexes

from .app import app


def main():
    dotenv.load_dotenv()
    fast_mode = "--fast" in sys.argv
    if not fast_mode:
        setup_indexes()
    uvicorn.run(app, port=int(os.getenv("PORT", 8080)), proxy_headers=True)


if __name__ == "__main__":
    main()
