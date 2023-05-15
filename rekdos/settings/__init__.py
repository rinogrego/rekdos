from .base import *


DEPLOYMENT = os.getenv("DEPLOYMENT_MODE")

if DEPLOYMENT == "dev":
    from .dev import *
    
elif DEPLOYMENT == "prod":
    from .prod import *
    
DEBUG = True
CSRF_TRUSTED_ORIGINS = ["https://rekdos-production.up.railway.app"] # thanks : https://stackoverflow.com/questions/70285834/forbidden-403-csrf-verification-failed-request-aborted-reason-given-for-fail