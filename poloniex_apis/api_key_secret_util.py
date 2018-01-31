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


def get_chbtc_api_key():
    """
    Returns a Poloniex API key from the config file
    """
    config = ConfigParser.ConfigParser()
    config.read("chbtc_api_keys.ini")
    key = config.get("ApiKeys", "key")
    return key


def get_chbtc_api_secret():
    """
    Returns a Poloniex API secret from the config file
    """
    config = ConfigParser.ConfigParser()
    config.read("chbtc_api_keys.ini")
    secret = config.get("ApiKeys", "secret")
    return secret

def get_zb_bch_address():
    """
    Returns a Poloniex API secret from the config file
    """
    config = ConfigParser.ConfigParser()
    config.read("chbtc_api_keys.ini")
    secret = config.get("address", "bch")
    return secret

