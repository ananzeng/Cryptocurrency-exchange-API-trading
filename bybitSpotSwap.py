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
API_KEY_2 = os.getenv("API_KEY_2")
API_SECRET_2 = os.getenv("API_SECRET_2")

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

def main():
    # 初始化 session1, session2
    session1 = HTTP(api_key=API_KEY_1, api_secret=API_SECRET_1)
    session2 = HTTP(api_key=API_KEY_2, api_secret=API_SECRET_2)

    symbol = os.getenv("SYMBOL")
    instrumentsInfo = session1.get_instruments_info(category="spot", symbol=symbol)
    tickSize = float(instrumentsInfo['result']['list'][0]['priceFilter']['tickSize'])
    minOrderQty = float(instrumentsInfo['result']['list'][0]['lotSizeFilter']['minOrderQty'])
    minOrderAmt = float(instrumentsInfo['result']['list'][0]['lotSizeFilter']['minOrderAmt'])

    while True:
        try:
            # 查詢 order book
            orderBookData = session1.get_orderbook(category="spot", symbol=symbol)
            #print("orderbook_data", orderbook_data)
            bestBid = decimal.Decimal(orderBookData['result']['b'][0][0])
            bestBidVol = decimal.Decimal(orderBookData['result']['b'][0][1])
            bestAsk = decimal.Decimal(orderBookData['result']['a'][0][0])
            bestAskVol = decimal.Decimal(orderBookData['result']['a'][0][1])
            logger.info(f"bestBid: {bestBid}, bestBidVol: {bestBidVol}")
            logger.info(f"bestAsk: {bestAsk}, bestAskVol: {bestAskVol}")
            qty = min(bestBidVol, bestAskVol)
            symbolWalletBalance1USDT = decimal.Decimal(getSymbolBalance(session1, "USDT"))
            symbolWalletBalance2 = decimal.Decimal(getSymbolBalance(session2, symbol))
            logger.info(f"symbolWalletBalance1USDT: {symbolWalletBalance1USDT}")
            logger.info(f"symbolWalletBalance2: {symbolWalletBalance2}")
            
            # 帳戶1下買單
            buyPrice = bestAsk + decimal.Decimal(str(tickSize))
            sellPrice = bestBid - decimal.Decimal(str(tickSize))
            logger.info(f"buyPrice: {buyPrice}")
            logger.info(f"sellPrice: {sellPrice}")
            logger.info("===========================")  #TODO Get account balance
            if ((bestAsk - bestBid).quantize(decimal.Decimal(str(tickSize))) == decimal.Decimal(str(tickSize)) and 
            qty > minOrderQty and 
            qty * buyPrice > minOrderAmt and 
            symbolWalletBalance2 > qty and
            symbolWalletBalance1USDT > qty * buyPrice
            ):
                session1.place_order(
                    category="spot",
                    symbol=symbol,
                    side="Buy",
                    orderType="Limit",
                    qty=qty,
                    price=buyPrice
                )
                session2.place_order(
                    category="spot",
                    symbol=symbol,
                    side="Sell",
                    orderType="Limit",
                    qty=qty,
                    price=sellPrice
                )
                logger.info(f"buyPrice: {buyPrice}, sellPrice: {sellPrice}, qty: {qty}")
                time.sleep(5)

            if symbolWalletBalance1USDT < 10 and symbolWalletBalance2 * sellPrice < 10:
                logger.info("Trigger SWAP Session")
                time.sleep(20)
                sessionTemp = session1
                session1 = session2
                session2 = sessionTemp




        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
