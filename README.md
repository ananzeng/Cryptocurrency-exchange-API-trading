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
This project utilizes the APIs of two accounts to perform trading strategies. The core logic involves using the APIs to execute trades between the two accounts, effectively leveraging the differences in exchange rates or other market conditions to achieve profitable trades.
本專案利用兩個帳號的API來執行交易策略。核心邏輯是利用API在兩個帳號之間執行交易，有效利用匯率差異或其他市場條件來實現盈利交易。
* TBC
## Supported Exchanges

| Exchange | API Volume Strategy   |
|----------|----------|
| bybit    | Supported|
| backpack | Supported|
