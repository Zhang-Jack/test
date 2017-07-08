import ConfigParser


def get_api_key():
    """
    Returns a Poloniex API key from the config file
    """
    config = ConfigParser.ConfigParser()
    config.read("api_keys.ini")
    key = config.get("ApiKeys", "key")
    return key


def get_api_secret():
    """
    Returns a Poloniex API secret from the config file
    """
    config = ConfigParser.ConfigParser()
    config.read("api_keys.ini")
    secret = config.get("ApiKeys", "secret")
    return secret

access_key_chbtc    = '1ec4b319-74fb-4751-bc8f-8cdf92a73a50'
access_secret_chbtc = '61e66f7c-536b-4fd8-b157-731501ff587f'

def get_chbtc_api_key():
    """
    Returns a Poloniex API key from the config file
    """
    """config = ConfigParser.ConfigParser()
    config.read("chbtc_api_keys.ini")
    key = config.get("ApiKeys", "key")
    """
    key = access_key_chbtc
    return key


def get_chbtc_api_secret():
    """
    Returns a Poloniex API secret from the config file
    """
    """
    config = ConfigParser.ConfigParser()
    config.read("chbtc_api_keys.ini")
    secret = config.get("ApiKeys", "secret")
    """
    secret = access_secret_chbtc
    return secret

