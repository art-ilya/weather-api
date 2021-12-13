import os


config_name = os.getenv("APP_CONFIG_NAME", "dev")
if config_name.lower() in {'prod', 'production'}:
    # TODO
    pass
else:
    from .dev import config