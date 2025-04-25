# Combine APIs of various exchanges to achieve trading strategies

## Setting up a virtual environment

To set up a virtual environment, follow these steps:

1. Install `virtualenv` if you haven't already:
   ```bash
   pip install virtualenv
   ```

2. Create a virtual environment:
   ```bash
   virtualenv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```


## Core Logic
* API Volume Strategy  
This arbitrage algorithm utilizes APIs from two accounts to execute a trading strategy. The core logic detects the price spread between the best bid and best ask in the order book. If the spread is only one tick, it places simultaneous buy and sell orders on both sides to ensure immediate matching, executing the trade between the two accounts via API.
本套利算法利用兩個帳號的API來執行交易策略。核心邏輯是偵測掛單簿的買一檔跟賣一檔的價差，如只差一個tick即會於買賣雙邊掛單，確保瞬間撮合，利用API在兩個帳號之間執行交易。  

* Funding Fee Arbitrage  
This algorithm detects a trading strategy based on the price spread between perpetual futures and spot markets within the same exchange. If the spread is smaller than a user-defined percentage, it executes a spot buy and a perpetual futures sell. This strategy is particularly suitable for funding rate arbitrage.
本算法偵測同一個交易所內，永續合約與現貨價差的交易策略，如掛單簿價差小於使用者規定的百分比，則進行現貨買入，永續合約賣出，特別適合資金費率的套利。  

* TBC
## Supported Exchanges

| Exchange | API Volume Strategy   | Funding Fee Arbitrage | 
|----------|----------|----------|
| bybit    | Supported|Supported|
| backpack | Supported|NotSupported|
