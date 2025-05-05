import os

import dotenv
import uvicorn

from foe_foundry_data.powers import index_powers

from .app import app

if __name__ == "__main__":
    dotenv.load_dotenv()
    index_powers()
    uvicorn.run(app, port=int(os.getenv("PORT", 8080)), proxy_headers=True)
