import os
import sys

import dotenv
import uvicorn

from foe_foundry_data.powers import index_powers

from .app import app


def main():
    dotenv.load_dotenv()
    fast_mode = "--fast" in sys.argv
    if not fast_mode:
        index_powers()
    uvicorn.run(app, port=int(os.getenv("PORT", 8080)), proxy_headers=True)


if __name__ == "__main__":
    main()
