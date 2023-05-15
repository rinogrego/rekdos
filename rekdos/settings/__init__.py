from .base import *


DEPLOYMENT = os.getenv("DEPLOYMENT_MODE")

if DEPLOYMENT == "dev":
    from .dev import *
    
elif DEPLOYMENT == "prod":
    from .prod import *
    
# DEBUG = True