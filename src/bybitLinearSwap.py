import time
import logging
from datetime import datetime
from pybit.unified_trading import HTTP
from dotenv import load_dotenv
import os
import decimal
import math
from util.bybitUtil import (
    getSymbolBalance, 
    getLinearOrderBookData, 
    getSpotOrderBookData,
    getSpotTradingParams,
    getLinearTradingParams
)

load_dotenv()
API_KEY_1 = os.getenv("BYBITAPIKEY1")
API_SECRET_1 = os.getenv("APISECRET1")

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

    # leverageResult = session1.set_leverage(category="linear", symbol=symbol, buyLeverage = "1", sellLeverage = "1")
    # print("leverageResult", leverageResult)

    spotTickSize, spotMinOrderQty, spotMinOrderAmt = getSpotTradingParams(session1, symbol)
    linearTickSize, linearMinOrderQty, minNotionalValue, qtyStep = getLinearTradingParams(session1, symbol)

    logger.info(f"linearTickSize: {linearTickSize}")
    logger.info(f"spotTickSize: {spotTickSize}")
    logger.info(f"spotMinOrderQty: {spotMinOrderQty}")
    logger.info(f"linearMinOrderQty: {linearMinOrderQty}")
    
    while True:
        # Get order book data using utility functions
        linearBestBid, linearBestBidVol, linearBestAsk, linearBestAskVol = getLinearOrderBookData(session1, symbol)
        spotBestBid, spotBestBidVol, spotBestAsk, spotBestAskVol = getSpotOrderBookData(session1, symbol)
        
        # Log the order book data
        logger.info(f"LINEAR: bestBid: {linearBestBid}, bestBidVol: {linearBestBidVol}, bestAsk: {linearBestAsk}, bestAskVol: {linearBestAskVol}")
        logger.info(f"SPOT:   bestBid: {spotBestBid}, bestBidVol: {spotBestBidVol}, bestAsk: {spotBestAsk}, bestAskVol: {spotBestAskVol}")

        # Calculate the maximum quantity that can be traded (minimum of available volumes)
        qty = decimal.Decimal((math.floor(min(linearBestBidVol, spotBestAskVol)) // qtyStep) * qtyStep)

        slippagePercentage = decimal.Decimal(0.005)
        slippageValue = linearBestAsk * slippagePercentage

        # Get USDT balance from wallet
        symbolWalletBalance1USDT = decimal.Decimal(getSymbolBalance(session1, "USDT"))
        logger.info(f"symbolWalletBalanceUSDT: {symbolWalletBalance1USDT}")

        # Calculate buy and sell prices with slight adjustments to ensure order execution
        buyPrice = spotBestAsk + decimal.Decimal(str(spotTickSize))
        sellPrice = linearBestBid - decimal.Decimal(str(linearTickSize))
        logger.info(f"buyPrice: {buyPrice}")
        logger.info(f"sellPrice: {sellPrice}")
        logger.info(f"qty: {qty}")

        logger.info("===========================")

        # logger.info(f"qty * spotBestAsk: {qty * spotBestAsk}")
        # logger.info(f"qty * linearBestBid: {qty * linearBestBid}")

        # Define condition variables with meaningful names
        isPriceGapAcceptable = abs(linearBestAsk - spotBestBid) < slippageValue
        isSpotQtySufficient = qty > spotMinOrderQty
        isLinearQtySufficient = qty * linearBestBid > minNotionalValue
        isBalanceSufficient = symbolWalletBalance1USDT > ((qty * spotBestAsk) + (qty * linearBestBid))
        
        # Check all conditions
        if (isPriceGapAcceptable and 
            isSpotQtySufficient and 
            isLinearQtySufficient and 
            isBalanceSufficient):
            logger.info(f"match!")
            # Execute spot market buy order
            session1.place_order(
                category="spot",
                symbol=symbol,
                side="Buy",
                orderType="Limit",
                qty=qty,
                price=buyPrice
            )
            symbolWalletBalance1USDT = decimal.Decimal(getSymbolBalance(session1, "USDT"))
            logger.info(f"symbolWalletBalanceUSDT: {symbolWalletBalance1USDT}")
            # Execute linear perpetual swap sell order
            session1.place_order(
                category="linear",
                symbol=symbol,
                side="Sell",
                orderType="Limit",
                qty=qty,
                price=sellPrice
            )
            symbolWalletBalance1USDT = decimal.Decimal(getSymbolBalance(session1, "USDT"))
            logger.info(f"symbolWalletBalanceUSDT: {symbolWalletBalance1USDT}")
            # Log the executed arbitrage trade details
            logger.info(f"buyPrice: {buyPrice}, sellPrice: {sellPrice}, qty: {qty}")
            logger.info("----------------------------")  #TODO Get account balance
            # Wait for 500 seconds before checking for new opportunities
            time.sleep(50)

if __name__ == "__main__":
    main()
