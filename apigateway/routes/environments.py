from fathomapi.api.config import Config

def is_fathom_environment():

    environment = Config.get('ENVIRONMENT')

    if environment in ['dev', 'test', 'production']:
        return True
    else:
        return False
