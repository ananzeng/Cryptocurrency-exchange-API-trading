import decimal

def getSpotTradingParams(session, symbol):
    """
    Get spot market trading parameters
    
    Args:
        session: Bybit API session
        symbol: Trading pair symbol
        
    Returns:
        tuple: (tickSize, minOrderQty, minOrderAmt)
    """
    spotInstrumentsInfo = session.get_instruments_info(category="spot", symbol=symbol)
    spotTickSize = float(spotInstrumentsInfo['result']['list'][0]['priceFilter']['tickSize'])
    spotMinOrderQty = float(spotInstrumentsInfo['result']['list'][0]['lotSizeFilter']['minOrderQty'])
    spotMinOrderAmt = float(spotInstrumentsInfo['result']['list'][0]['lotSizeFilter']['minOrderAmt'])
    
    return spotTickSize, spotMinOrderQty, spotMinOrderAmt

def getLinearTradingParams(session, symbol):
    """
    Get linear perpetual swap trading parameters
    
    Args:
        session: Bybit API session
        symbol: Trading pair symbol
        
    Returns:
        tuple: (tickSize, minOrderQty)
    """
    linearInstrumentsInfo = session.get_instruments_info(category="linear", symbol=symbol)
    print("linearInstrumentsInfo", linearInstrumentsInfo)
    linearTickSize = float(linearInstrumentsInfo['result']['list'][0]['priceFilter']['tickSize'])
    linearMinOrderQty = float(linearInstrumentsInfo['result']['list'][0]['lotSizeFilter']['minOrderQty'])
    minNotionalValue = float(linearInstrumentsInfo['result']['list'][0]['lotSizeFilter']['minNotionalValue'])
    qtyStep = float(linearInstrumentsInfo['result']['list'][0]['lotSizeFilter']['qtyStep'])
    return linearTickSize, linearMinOrderQty, minNotionalValue, qtyStep

def getWalletBalance(coinName, symbolWalletBalancelist):
    for coin in symbolWalletBalancelist:
        if coin['coin'] == coinName:
            return coin['walletBalance']
    return None  # 如果找不到該 coin，就回傳 None

def getSymbolBalance(session, symbol):
    walletBalance = session.get_wallet_balance(accountType="UNIFIED")
    symbolWalletBalanceList = walletBalance['result']['list'][0]['coin']
    
    if symbol != "USDT":
        symbol = symbol.replace("USDT", "")

    symbolWalletBalance = getWalletBalance(symbol, symbolWalletBalanceList)
    return symbolWalletBalance

def getLinearOrderBookData(session, symbol):
    """
    Get order book data for linear perpetual swap
    
    Args:
        session: Bybit API session
        symbol: Trading pair symbol
        
    Returns:
        tuple: (bestBid, bestBidVol, bestAsk, bestAskVol)
    """
    # Get order book data for linear perpetual swap
    linearOrderBookData = session.get_orderbook(category="linear", symbol=symbol)
    
    # Extract best bid/ask prices and volumes
    linearBestBid = decimal.Decimal(linearOrderBookData['result']['b'][0][0])
    linearBestBidVol = decimal.Decimal(linearOrderBookData['result']['b'][0][1])
    linearBestAsk = decimal.Decimal(linearOrderBookData['result']['a'][0][0])
    linearBestAskVol = decimal.Decimal(linearOrderBookData['result']['a'][0][1])
    
    return linearBestBid, linearBestBidVol, linearBestAsk, linearBestAskVol

def getSpotOrderBookData(session, symbol):
    """
    Get order book data for spot market
    
    Args:
        session: Bybit API session
        symbol: Trading pair symbol
        
    Returns:
        tuple: (bestBid, bestBidVol, bestAsk, bestAskVol)
    """
    # Get order book data for spot market
    spotOrderBookData = session.get_orderbook(category="spot", symbol=symbol)
    
    # Extract best bid/ask prices and volumes
    spotBestBid = decimal.Decimal(spotOrderBookData['result']['b'][0][0])
    spotBestBidVol = decimal.Decimal(spotOrderBookData['result']['b'][0][1])
    spotBestAsk = decimal.Decimal(spotOrderBookData['result']['a'][0][0])
    spotBestAskVol = decimal.Decimal(spotOrderBookData['result']['a'][0][1])
    
    return spotBestBid, spotBestBidVol, spotBestAsk, spotBestAskVol
