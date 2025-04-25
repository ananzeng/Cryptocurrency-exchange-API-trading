def getSymbolBalance(session, symbol):
    walletBalance = session.balances()
    symbolWalletBalance = walletBalance[symbol]['available']
    return symbolWalletBalance

def getMarketInfo(backpackMarketInfo, symbol):
    for market in backpackMarketInfo:
        if market['baseSymbol'] == symbol:
            return float(market['filters']['quantity']['minQuantity']), float(market['filters']['quantity']['stepSize'])
    return None, None
