import os

import uvicorn

from .app import app

if __name__ == "__main__":
    uvicorn.run(app, port=int(os.getenv("PORT", 8080)), proxy_headers=True)
