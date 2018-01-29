
def coin_list(market):
    """
    Parameters
    ----------
    market : Market Name (eg. "KRW", "BTC", "ETH", ...)

    Returns
    -------
    coins : tuple
    """
    KRW_coins = ("BTC", "BCC", "ETH", "DASH", "ZEC", "XMR", "LTC", "BTG", "REP",
                 "NEO", "QTUM", "ETC", "LSK", "OMG", "STRAT", "PIVX", "WAVES", "ARK",
                 "KMD", "SBD", "VTC", "MTL", "STEEM", "STORJ", "XRP", "ARDR", "TIX", "POWR",
                 "XEM", "GRS", "ADA", "EMC2", "MER", "XLM", "SNT")

    if market is "KRW":
        return KRW_coins

    pass
    # 현재 KRW 마켓에 상장된 코인들만 관리하고 있다.
    # 업비트에 상장된 코인 리스트를 직접 가져오도록 구현하려 함
    # 사실 구현하지 않아도 문제 될 것은 없다고 생각함
