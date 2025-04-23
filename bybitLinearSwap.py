import time
import logging
from datetime import datetime
from pybit.unified_trading import HTTP
from dotenv import load_dotenv
import os
import decimal

# 讀取 .env 檔案
load_dotenv()

# 兩個不同 Bybit 帳戶(或子帳戶)的 API Key，從環境變數中讀取
API_KEY_1 = os.getenv("API_KEY_1")
API_SECRET_1 = os.getenv("API_SECRET_1")

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

# 設定 logger
log_dir = "log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_filename = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(log_filename),
    logging.StreamHandler()
])
logger = logging.getLogger(__name__)

def main():
    session1 = HTTP(api_key=API_KEY_1, api_secret=API_SECRET_1)
    symbol = os.getenv("SYMBOL")  
    leverageResult = session1.set_leverage(category="linear", symbol=symbol, buyLeverage = "1", sellLeverage = "1")
    print("leverageResult", leverageResult)
    spotInstrumentsInfo = session1.get_instruments_info(category="spot", symbol=symbol)
    spotTickSize = float(spotInstrumentsInfo['result']['list'][0]['priceFilter']['tickSize'])
    spotMinOrderQty = float(spotInstrumentsInfo['result']['list'][0]['lotSizeFilter']['minOrderQty'])
    spotMinOrderAmt = float(spotInstrumentsInfo['result']['list'][0]['lotSizeFilter']['minOrderAmt'])

    linearInstrumentsInfo = session1.get_instruments_info(category="linear", symbol=symbol)
    linearTickSize = float(linearInstrumentsInfo['result']['list'][0]['priceFilter']['tickSize'])
    linearMinOrderQty = float(linearInstrumentsInfo['result']['list'][0]['lotSizeFilter']['minOrderQty'])

    logger.info(f"linearTickSize: {linearTickSize}")
    logger.info(f"spotTickSize: {spotTickSize}")
    while True:
        #sell linear
        linearOrderBookData = session1.get_orderbook(category="linear", symbol=symbol)

        #buy spot
        spotOrderBookData = session1.get_orderbook(category="spot", symbol=symbol)

        #get linear order book
        linearBestBid = decimal.Decimal(linearOrderBookData['result']['b'][0][0])
        linearBestBidVol = decimal.Decimal(linearOrderBookData['result']['b'][0][1])
        linearBestAsk = decimal.Decimal(linearOrderBookData['result']['a'][0][0])
        linearBestAskVol = decimal.Decimal(linearOrderBookData['result']['a'][0][1])

        logger.info(f"SPOT:   bestBid: {linearBestBid}, bestBidVol: {linearBestBidVol}, bestAsk: {linearBestAsk}, bestAskVol: {linearBestAskVol}")

        #get spot order book
        spotBestBid = decimal.Decimal(spotOrderBookData['result']['b'][0][0])
        spotBestBidVol = decimal.Decimal(spotOrderBookData['result']['b'][0][1])
        spotBestAsk = decimal.Decimal(spotOrderBookData['result']['a'][0][0])
        spotBestAskVol = decimal.Decimal(spotOrderBookData['result']['a'][0][1])

        logger.info(f"LINEAR: bestBid: {spotBestBid}, bestBidVol: {spotBestBidVol}, bestAsk: {spotBestAsk}, bestAskVol: {spotBestAskVol}")

        qty = min(linearBestBidVol, spotBestAskVol)

        slippagePercentage = decimal.Decimal(0.005)  # 定義滑點百分比，例如 0.5%
        slippageValue = linearBestAsk * slippagePercentage  # 計算滑點值

        symbolWalletBalance1USDT = decimal.Decimal(getSymbolBalance(session1, "USDT"))
        logger.info(f"symbolWalletBalanceUSDT: {symbolWalletBalance1USDT}")

        buyPrice = spotBestAsk + decimal.Decimal(str(spotTickSize))
        sellPrice = linearBestBid - decimal.Decimal(str(linearTickSize))
        logger.info(f"buyPrice: {buyPrice}")
        logger.info(f"sellPrice: {sellPrice}")
        logger.info("===========================")  #TODO Get account balance
        if (abs(linearBestAsk - spotBestBid) < slippageValue and            
            qty > spotMinOrderQty and  
            qty > linearMinOrderQty and
            symbolWalletBalance1USDT > ((qty * spotBestAsk) + (qty * linearBestBid))):
            print("match!")
            session1.place_order(
                category="spot",
                symbol=symbol,
                side="Buy",
                orderType="Limit",
                qty=qty,
                price=buyPrice
            )
            session1.place_order(
                category="linear",
                symbol=symbol,
                side="Sell",
                orderType="Limit",
                qty=qty,
                price=sellPrice
            )
            logger.info(f"buyPrice: {buyPrice}, sellPrice: {sellPrice}, qty: {qty}")
            time.sleep(500)

if __name__ == "__main__":
    main()
