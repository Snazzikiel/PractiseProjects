import unittest
import json
from collections import Counter
import GatherData

SKIP_COINS = {'BITCNY-BTC', 'ETH-DGD', 'ETH-ETC', 'USDT-BTC'}

#Buy and Sell Percentage
Increase_Percentage = 5
Decrease_Percentage = 1

#How many BUYS there should be in history before purchase
ScanRows = 50
Buy_History = (35/ScanRows*100)

#How many bitcoin per purchase?
BTC_BuyPP = .00004000

#If sale has not happened X hours after placed sale
Sale_Time = 5
objGD = GatherData.GatherData

#Global new balance sheet
BitBalance = {}


class Pytrex(object):

    # method used for testing purposes - adds all coins to dictionary with balance of 0
    def GlobalBalance(self):
        Summary = objGD.GetMarketSummaries(objGD)
        for Coin in Summary['result']:
            BitBalance.update({Coin['MarketName']:0.00000000})

    def PrintSummary(self):
        Summaries = objGD.GetMarketSummaries(objGD)
        for Coin in Summaries['result']:
            if Coin['MarketName'] not in SKIP_COINS:
                if self.CheckBalance(Coin['MarketName']) == True:
                    print("Have balance for %s" % Coin['MarketName'])
                else:
                    if self.MarketHistory(Coin['MarketName']) == True:
                        if self.CheckBitcoins() == True:
                            print("Purchased %s at %.8f" % (Coin['MarketName'], Coin['Last']))
                        else:
                            continue
                    else:
                        continue

    # Check for Currency balance - if yes, return true
    def CheckBalance(self, CoinName):
        CoinName = CoinName.split('-')
        CoinName = CoinName[1]
        Balance = objGD.BalanceCheck(objGD, CoinName)
        Balance = Balance['result']
        if Balance['Available'] == None:
            return False
        else:
            return True

    # Check how many bitcoins there is left on the account
    def CheckBitcoins(self):
        Balance = objGD.BalanceCheck(objGD, 'BTC')
        Balance = Balance['result']

        if Balance['Available'] > BTC_BuyPP:
            return True
        else:
            return False

# Check market history for coin and compare sell/buy
    def MarketHistory(self, CoinName):
        History = objGD.GetMarketHistory(objGD, CoinName, 2)
        History = History['result']
        Counter = 0

        #Find out how many BUYS there are
        for Trans in History[:ScanRows]:
            if Trans['OrderType'] == 'BUY':
                Counter += 1

        if Counter > Buy_History:
            return True
        else:
            return False


Pytrex = Pytrex()
Pytrex.GlobalBalance()
Pytrex.PrintSummary()