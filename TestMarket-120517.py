import GatherData
import datetime

timeout = 10

SKIP_COINS = {'ETH-LUN', 'ETH-SNGLS', 'ETH-GNT', 'ETH-WINGS', 'ETH-GUP', 'ETH-TKN', 'UBQ-APX',
              'ETH-RLC', 'ETH-REP', 'ETH-GNO', 'ETH-DGD', 'ETH-ETC', 'USDT-BTC', 'USDT-ETH', 'BITCNY-BTC'}

#Buy and Sell Percentage
Increase_Percentage = .10
Decrease_Percentage = -.02

#How many bitcoin per purchase?
BTC_BuyPP = .01000000

#Test balance - Bitcoin start balance
MainBalance = 1.00000000

#Make sale after X hours
Sale_Time = 5

#Time to reset sale data
ResetSaleTime = 18

#Every Xmin+ Check if rise or decrease
SaleCheck = 15
TimeNow = datetime.datetime.now()
NowPlusSaleCheck = TimeNow + datetime.timedelta(minutes =SaleCheck)

#If Last if over X% of High
LastPercCheck = 80

PastPerc = 0.0

#Global new balance sheet
BitBalance = {}
PurchaseTime = {}
PurchasePrice = {}
BuyPerc = {}
SalePerc = {}
CurrPerc = 0.0

#Timer Input
answer = "yeah"

objGD = GatherData.GatherData

class PytrexTest():

    # method used for testing purposes - adds all coins to dictionary with balance of 0
    def GlobalBalance(self):
        Summary = objGD.GetMarketSummaries(objGD)
        for Coin in Summary['result']:
            BitBalance.update({Coin['MarketName']:0.00000000})
            PurchaseTime.update({Coin['MarketName']:Coin['TimeStamp']})
            PurchasePrice.update({Coin['MarketName']:0.00000000})
            BuyPerc.update({Coin['MarketName']:0})
            SalePerc.update({Coin['MarketName']:0})

    def Main(self):
        global MainBalance
        global PastPerc
        global CurrPerc
        global NowPlusSaleCheck
        global TimeNow

        with open("BitcoinBalance.txt", "a+") as BalanceSheet:
            Summaries = objGD.GetMarketSummaries(objGD)
            for Coin in Summaries['result']:
                if Coin['MarketName'][:3] == 'BTC':
                #if Coin['MarketName'] not in SKIP_COINS:
                    if self.CheckBalance(Coin['MarketName']):
                        PrevTime = PurchaseTime[Coin['MarketName']].split('T')
                        PrevTime = PrevTime[1].split(':')
                        CurrTime = Coin['TimeStamp'].split('T')
                        CurrTime = CurrTime[1].split(':')
                        CurrPerc = Coin['Last'] / Coin['PrevDay'] - 1

                        if NowPlusSaleCheck < TimeNow:
                            PastPerc = Coin['Last'] / Coin['PrevDay'] - 1
                            NowPlusSaleCheck = TimeNow + datetime.timedelta(minutes=SaleCheck)
                        else:
                            TimeNow = datetime.datetime.now()

                        #was the purchase made X hours ago
                        if ((int(CurrTime[0]) - int(PrevTime[0])) >= Sale_Time) and (int(PrevTime[1]) <= int(CurrTime[1])):
                            MainBalance = MainBalance + (BitBalance[Coin['MarketName']] * Coin['Last'])
                            BitBalance.update({Coin['MarketName']: 0.00000000})
                            PurchaseTime.update({Coin['MarketName']: Coin['TimeStamp']})
                            SalePerc.update({Coin['MarketName']:CurrPerc})
                            BalanceSheet.write('\nSale:; Market Name: %s; Last: %.8f; Main Balance: %.8f;  '
                                               'BitBalance: %s;  TimeStamp: %s, CurrPerc: %s' % (
                                Coin['MarketName'], Coin['Last'], MainBalance, BitBalance[Coin['MarketName']],
                                Coin['TimeStamp'], CurrPerc))
                            print('Sale:; %s; %.8f; %.8f; %s; %s, %s' % (
                                Coin['MarketName'], Coin['Last'], MainBalance, BitBalance[Coin['MarketName']],
                                Coin['TimeStamp'], CurrPerc))
                        else:
                            #has the current % dropped in the last XXminutes
                            if (CurrPerc - PastPerc) <= Decrease_Percentage:
                                MainBalance = MainBalance + (BitBalance[Coin['MarketName']] * Coin['Last'])
                                BitBalance.update({Coin['MarketName']: 0.00000000})
                                PurchaseTime.update({Coin['MarketName']: Coin['TimeStamp']})
                                SalePerc.update({Coin['MarketName']: CurrPerc})
                                BalanceSheet.write('\nSale:; Market Name: %s; Last: %.8f; Main Balance: %.8f;  '
                                                   'BitBalance: %s;  TimeStamp: %s, CurrPerc: %s' % (
                                Coin['MarketName'], Coin['Last'], MainBalance, BitBalance[Coin['MarketName']],
                                Coin['TimeStamp'], CurrPerc))
                                print('Sale:; %s; %.8f; %.8f; %s; %s, %s' % (
                                Coin['MarketName'], Coin['Last'], MainBalance, BitBalance[Coin['MarketName']],
                                Coin['TimeStamp'], CurrPerc))
                            else:
                                #print("Has currency, but has not dropped in percentage")
                                continue

                    else:
                        try:
                            CurrPerc = (Coin['Last'] / Coin['PrevDay']) - 1
                        except:
                            continue

                        if CurrPerc >= Increase_Percentage:
                            if self.CheckBitcoins():
                                if SalePerc[Coin['MarketName']] != 0:
                                    if SalePerc[Coin['MarketName']] < CurrPerc:
                                        BitBalance.update({Coin['MarketName'] : (BTC_BuyPP / Coin['Last'])})
                                        MainBalance = MainBalance - BTC_BuyPP
                                        PurchaseTime.update({Coin['MarketName']:Coin['TimeStamp']})
                                        PurchasePrice.update({Coin['MarketName']:Coin['Last']})
                                        BuyPerc.update({Coin['MarketName']:(Coin['Last'] / Coin['PrevDay'] - 1)})
                                        BalanceSheet.write('\nBuy:; Market Name: %s; Last: %.8f; Main Balance: %.8f;  '
                                            'BitBalance: %s;  TimeStamp: %s, CurrPerc: %s' % (
                                        Coin['MarketName'], Coin['Last'], MainBalance, Coin['TimeStamp']))
                                        print('Buy:; %s; %.8f; %.8f; %s; %s, %s' % (
                                            Coin['MarketName'], Coin['Last'], MainBalance, BitBalance[Coin['MarketName']],
                                            Coin['TimeStamp'], CurrPerc))
                                    else:
                                        #Reset Sale stats if it has been over XX Hours since last purchase
                                        PrevTime = PurchaseTime[Coin['MarketName']].split('T')
                                        PrevTime = PrevTime[1].split(':')
                                        CurrTime = Coin['TimeStamp'].split('T')
                                        CurrTime = CurrTime[1].split(':')

                                        if ((int(CurrTime[0]) - int(PrevTime[0])) >= ResetSaleTime) and (
                                            int(PrevTime[1]) <= int(CurrTime[1])):
                                            PurchaseTime.update({Coin['MarketName']: 0})
                                            SalePerc.update({Coin['MarketName']: 0})
                                        else:
                                            continue
                                else:
                                    if self.LastCheck(Coin):
                                        BitBalance.update({Coin['MarketName']: (BTC_BuyPP / Coin['Last'])})
                                        MainBalance = MainBalance - BTC_BuyPP
                                        PurchaseTime.update({Coin['MarketName']: Coin['TimeStamp']})
                                        PurchasePrice.update({Coin['MarketName']: Coin['Last']})
                                        BuyPerc.update({Coin['MarketName']: (Coin['Last'] / Coin['PrevDay'] - 1)})
                                        BalanceSheet.write('\nBuy:; Market Name: %s; Last: %.8f; Main Balance: %.8f;  '
                                                           'BitBalance: %s;  TimeStamp: %s, CurrPerc: %s' % (
                                            Coin['MarketName'], Coin['Last'], MainBalance, BitBalance[Coin['MarketName']],
                                            Coin['TimeStamp'], CurrPerc))
                                        print('Buy:; %s; %.8f; %.8f; %s; %s, %s' % (
                                            Coin['MarketName'], Coin['Last'], MainBalance, BitBalance[Coin['MarketName']],
                                            Coin['TimeStamp'], CurrPerc))
                                    else:
                                     #   print("Does not meet over 80% of 24h High")
                                        continue
                            else:
                                #print('Ready to buy, but insufficient bitcoins. %s, %.8f' % (Coin['MarketName'], Coin['Last']))
                                continue
                        else:
                            #print('Current Perc < Increased_perc %s. %.8f' % (Coin['MarketName'], Coin['Last']))
                            continue
            BalanceSheet.close()

    #Sell all remaining
    def SellAll(self):
        with open("BitcoinBalance.txt", "a+") as BalanceSheet:
            Summaries = objGD.GetMarketSummaries(objGD)
            for Coin in Summaries['result']:
                    if self.CheckBalance(Coin['MarketName']):
                        PrevTime = PurchaseTime[Coin['MarketName']].split('T')
                        PrevTime = PrevTime[1].split(':')
                        CurrTime = Coin['TimeStamp'].split('T')
                        CurrTime = CurrTime[1].split(':')
                        CurrPerc = Coin['Last'] / Coin['PrevDay'] - 1

                        # was the purchase made X hours ago
                        MainBalance = MainBalance + (BitBalance[Coin['MarketName']] * Coin['Last'])
                        BitBalance.update({Coin['MarketName']: 0.00000000})
                        PurchaseTime.update({Coin['MarketName']: Coin['TimeStamp']})
                        SalePerc.update({Coin['MarketName']: CurrPerc})
                        BalanceSheet.write("\nSale, %s, %.8f, %.8f, %s, %s %" % (
                        Coin['MarketName'], Coin['Last'], MainBalance, Coin['TimeStamp']))
                        print('Sale:; %s; %.8f; %.8f; %s; %s, %s' % (
                            Coin['MarketName'], Coin['Last'], MainBalance, BitBalance[Coin['MarketName']],
                            Coin['TimeStamp'], CurrPerc))
        BalanceSheet.close()

    #Last Check if over 80%
    def LastCheck(self, Coin):
        if Coin['Last'] >= LastPercCheck/100 * Coin['High']:
            return True
        else:
            return False

    # Check for Currency balance - if yes, return true
    def CheckBalance(self, CoinName):
        if BitBalance[CoinName] == 0.00000000:
            return False
        else:
            return True

    # Check how many bitcoins there is left on the account
    def CheckBitcoins(self):
        if MainBalance >= BTC_BuyPP:
            return True
        else:
            return False


Pytrex = PytrexTest()
Pytrex.GlobalBalance()
x = 1

while answer != '1':

    try:
        with open("Coins.txt", "r+") as BalanceSheet1:
            Pytrex.Main()
            print('Time: %s' % (datetime.datetime.now().time()))
            BalanceSheet1.write("------------------------------------------\n")
            BalanceSheet1.write("Main Balance: %.8f\n" % MainBalance)
            Summaries = objGD.GetMarketSummaries(objGD)
            for Coin in Summaries['result']:
                if Coin['MarketName'] not in SKIP_COINS and Coin['MarketName'][:3] == 'BTC':
                    try:
                        BalanceSheet1.write("%s  |  %.8f  |  %.8f\n" % (Coin['MarketName'], BitBalance[Coin['MarketName']], Coin['Last']))
                    except:
                        BalanceSheet1.write("%s  |  null  |  null\n" % Coin['MarketName'])
        BalanceSheet1.close()
    except:
        print("There was an error")

print("Exited!")

