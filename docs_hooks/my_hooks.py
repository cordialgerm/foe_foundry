from datetime import datetime


def on_config(config, **kwargs):
    config.copyright = (
        f"Copyright © {datetime.now().year} Evan Rash. All Rights Reserved."
    )
