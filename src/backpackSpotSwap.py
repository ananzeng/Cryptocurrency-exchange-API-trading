import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import os
from backpack.backpackPublic import *
from backpack.backpackPublicAuth import *
import decimal
import logging
from util.backpackUtil import getSymbolBalance, getMarketInfo
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




def main():
    backpackSession1 = BpxClient()
    backpackSession1.init(BACKPACKAPIKEY1, BACKPACKAPISECRET1)

    backpackSession2 = BpxClient()
    backpackSession2.init(BACKPACKAPIKEY2, BACKPACKAPISECRET2)    
    backpackMarketInfo = Markets()
    minOrderQty, tickSize = getMarketInfo(backpackMarketInfo, "SOL")
    logger.info(f"minOrderQty: {minOrderQty}, tickSize: {tickSize}")
    tradingTime = int(time.time() * 1000)

    while True:
        logger.info("===========================")
        #Get Order Book
        orderBookData = Depth('SOL_USDC')
        bestBid = decimal.Decimal(orderBookData['bids'][-1][0])
        bestBidVol = decimal.Decimal(orderBookData['bids'][-1][1])
        bestAsk = decimal.Decimal(orderBookData['asks'][0][0])
        bestAskVol = decimal.Decimal(orderBookData['asks'][0][1])
        
        logger.info(f"bestBid: {bestBid}, bestBidVol: {bestBidVol}")
        logger.info(f"bestAsk: {bestAsk}, bestAskVol: {bestAskVol}")
        qty = min(bestBidVol, bestAskVol)

        #Get balance
        symbolWalletBalance1USDT = decimal.Decimal(getSymbolBalance(backpackSession1, "USDC"))
        symbolWalletBalance2 = decimal.Decimal(getSymbolBalance(backpackSession2, "SOL"))

        logger.info(f"symbolWalletBalance-1-USDT: {symbolWalletBalance1USDT}")
        logger.info(f"symbolWalletBalance-2-{SYMBOL.split("_")[0]}: {symbolWalletBalance2}")

        # Cal the Best price
        buyPrice = bestAsk + decimal.Decimal(str(tickSize))
        sellPrice = bestBid - decimal.Decimal(str(tickSize))
        logger.info(f"buyPrice: {buyPrice}")
        logger.info(f"sellPrice: {sellPrice}")

        #Excute buy/sell order
        # Check if the spread is exactly one tick
        is_one_tick_spread = (bestAsk - bestBid).quantize(decimal.Decimal(str(tickSize))) == decimal.Decimal(str(tickSize))

        # Check if the order quantity is above the minimum
        is_valid_qty = qty > minOrderQty

        # Check if account 2 has enough asset balance to sell
        has_balance_to_sell = symbolWalletBalance2 > qty

        # Check if account 1 has enough USDT to buy
        has_balance_to_buy = symbolWalletBalance1USDT > qty * buyPrice

        # Execute buy/sell order if all conditions are met
        if is_one_tick_spread and is_valid_qty and has_balance_to_sell and has_balance_to_buy:
            session1Response = backpackSession1.ExeOrder(  #買sol
                symbol = "SOL_USDC",
                side = "Bid",
                orderType = "Limit",
                quantity = float(qty),
                price = float(buyPrice),
                timeInForce = "GTC"
            )
            session2Response = backpackSession2.ExeOrder( #賣sol
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
            tradingTime = session2Response.get('createdAt')
            if tradingTime == None:
                tradingTime = int(time.time() * 1000)
            time.sleep(5)

        if int(time.time() * 1000) - tradingTime > 100000:
            logger.info(f"Into timeout session - {str(int(time.time() * 1000))}")
            backpackSession1.ordersCancel(symbol = "SOL_USDC")
            backpackSession2.ordersCancel(symbol = "SOL_USDC")
            symbolWalletBalance1USDT = decimal.Decimal(getSymbolBalance(backpackSession1, "USDC"))
            symbolWalletBalance2 = decimal.Decimal(getSymbolBalance(backpackSession2, "SOL"))
            session1Response = backpackSession1.ExeOrder(  #買sol
                            symbol = "SOL_USDC",
                            side = "Bid",
                            orderType = "Limit",
                            quantity = float((float(symbolWalletBalance1USDT / buyPrice) // float(tickSize)) * float(tickSize)),
                            price = float(buyPrice),
                            timeInForce = "GTC"
                        )

            session2Response = backpackSession2.ExeOrder( #賣sol
                            symbol = "SOL_USDC",
                            side = "Ask",
                            orderType = "Limit",
                            quantity = float((symbolWalletBalance2 // decimal.Decimal(tickSize)) * decimal.Decimal(tickSize)),
                            price = float(sellPrice),
                            timeInForce = "GTC"
                        )

            symbolWalletBalance1USDT = decimal.Decimal(getSymbolBalance(backpackSession1, "USDC"))
            symbolWalletBalance2 = decimal.Decimal(getSymbolBalance(backpackSession2, "SOL"))
            tradingTime = int(time.time() * 1000)

        if symbolWalletBalance1USDT < 10 and symbolWalletBalance2 * sellPrice < 10:
            logger.info("Trigger SWAP Session")
            time.sleep(10)
            sessionTemp = backpackSession1
            backpackSession1 = backpackSession2
            backpackSession2 = sessionTemp
if __name__ == "__main__":
    main()
