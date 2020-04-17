from fathomapi.api.config import Config


def is_fathom_environment():

    environment = Config.get('ENVIRONMENT')

    if environment in ['dev', 'test', 'production']:
        return True
    else:
        return False


def consolidated_dosage():
    consolidate_dosage = Config.get('PROVIDER_INFO').get('consolidate_dosage') or 'false'
    consolidated = True if consolidate_dosage.lower() == 'true' else False
    return consolidated
