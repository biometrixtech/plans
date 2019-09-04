from fathomapi.api.config import Config

def get_visualization_parameter():

    environment = Config.get('ENVIRONMENT')

    if environment in ['dev', 'test', 'production']:
        return True
    else:
        return False
