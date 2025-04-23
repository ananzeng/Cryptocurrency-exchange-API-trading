import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import os
from backpack.backpackPublic import *
from backpack.backpackPublicAuth import *
import decimal
import logging
# 讀取 .env 檔案
load_dotenv()

BACKPACKAPIKEY1 = os.getenv("BACKPACKAPIKEY1")
BACKPACKAPISECRET1 = os.getenv("BACKPACKAPISECRET1")
BACKPACKAPIKEY2 = os.getenv("BACKPACKAPIKEY2")
BACKPACKAPISECRET2 = os.getenv("BACKPACKAPISECRET2")
SYMBOL = os.getenv("SYMBOL")

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

def getSymbolBalance(session, symbol):
    walletBalance = session.balances()
    symbolWalletBalance = walletBalance[symbol]['available']
    return symbolWalletBalance

def getMarketInfo(backpackMarketInfo, symbol):
    for market in backpackMarketInfo:
        if market['baseSymbol'] == symbol:
            return float(market['filters']['quantity']['minQuantity']), float(market['filters']['quantity']['stepSize'])
    return None, None


def main():
    backpackSession1 = BpxClient()
    backpackSession1.init(BACKPACKAPIKEY1, BACKPACKAPISECRET1)

    backpackSession2 = BpxClient()
    backpackSession2.init(BACKPACKAPIKEY2, BACKPACKAPISECRET2)    
    backpackMarketInfo = Markets()
    minOrderQty, tickSize = getMarketInfo(backpackMarketInfo, "SOL")
    logger.info(f"minOrderQty: {minOrderQty}, tickSize: {tickSize}")
    while True:
        logger.info("===========================")  #TODO Get account balance
        orderBookData = Depth('SOL_USDC')
        bestBid = decimal.Decimal(orderBookData['bids'][-1][0])
        bestBidVol = decimal.Decimal(orderBookData['bids'][-1][1])
        bestAsk = decimal.Decimal(orderBookData['asks'][0][0])
        bestAskVol = decimal.Decimal(orderBookData['asks'][0][1])
        
        logger.info(f"bestBid: {bestBid}, bestBidVol: {bestBidVol}")
        logger.info(f"bestAsk: {bestAsk}, bestAskVol: {bestAskVol}")
        qty = min(bestBidVol, bestAskVol)
        symbolWalletBalance1USDT = decimal.Decimal(getSymbolBalance(backpackSession1, "USDC"))
        symbolWalletBalance2 = decimal.Decimal(getSymbolBalance(backpackSession2, "SOL"))
        logger.info(f"symbolWalletBalance1USDT: {symbolWalletBalance1USDT}")
        logger.info(f"symbolWalletBalance2: {symbolWalletBalance2}")
        # 帳戶1下買單
        buyPrice = bestAsk + decimal.Decimal(str(tickSize))
        sellPrice = bestBid - decimal.Decimal(str(tickSize))
        logger.info(f"buyPrice: {buyPrice}")
        logger.info(f"sellPrice: {sellPrice}")
        
        if ((bestAsk - bestBid).quantize(decimal.Decimal(str(tickSize))) == decimal.Decimal(str(tickSize)) and 
        qty > minOrderQty and 
        symbolWalletBalance2 > qty and
        symbolWalletBalance1USDT > qty * buyPrice
        ):
            session1Response = backpackSession1.ExeOrder(
                symbol = "SOL_USDC",
                side = "Bid",
                orderType = "Limit",
                quantity = float(qty),
                price = float(buyPrice),
                timeInForce = "GTC"
            )
            session2Response = backpackSession2.ExeOrder(
                symbol = "SOL_USDC",
                side = "Ask",
                orderType = "Limit",
                quantity = float(qty),
                price = float(sellPrice),
                timeInForce = "GTC"
            )
            buyOrderId = session1Response.get('id')
            sellOrderId = session2Response.get('id')
            logger.info(f"buyPrice: {buyPrice}, Id: {buyOrderId} sellPrice: {sellPrice}, Id: {sellOrderId}, qty: {qty}")
            time.sleep(5)

        if symbolWalletBalance1USDT < 10 and symbolWalletBalance2 * sellPrice < 10:
            logger.info("Trigger SWAP Session")
            time.sleep(20)
            sessionTemp = backpackSession1
            backpackSession1 = backpackSession2
            backpackSession2 = sessionTemp
if __name__ == "__main__":
    main()
