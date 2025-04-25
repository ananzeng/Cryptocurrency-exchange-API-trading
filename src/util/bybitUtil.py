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
