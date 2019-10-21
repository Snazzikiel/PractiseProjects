
import time
import hmac
import hashlib
import requests

try:
    from urllib import urlencode
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import urljoin


#---- API Details ------
BASE_URL = 'https://bittrex.com/api/v1.1/%s/'
api_key = '<api_key>'
api_secret = '<api_secret>'
MARKET_SET = {'getopenorders', 'cancel', 'sellmarket', 'selllimit', 'buymarket', 'buylimit'}
ACCOUNT_SET = {'getbalances', 'getbalance', 'getdepositaddress', 'withdraw', 'getorderhistory'}


class GatherData(object):

    def BitRetrieval(self, Method, options=None):

        if not options:
            options = {}
        nonce = str(int(time.time() * 1000))

        method_set = 'public'
        if Method in MARKET_SET:
            method_set = 'market'
        elif Method in ACCOUNT_SET:
            method_set = 'account'

        request_url = (BASE_URL % method_set) + Method + '?'

        if method_set != 'public':
            request_url += 'apikey=' + api_key + "&nonce=" + nonce + '&'

        request_url += urlencode(options)

        return requests.get(
            request_url,
            headers={"apisign": hmac.new(api_secret.encode(), request_url.encode(), hashlib.sha512).hexdigest()}
        ).json()

    # Get Balance Function
    def BalanceCheck(self, Coin):
        return self.BitRetrieval(self, 'getbalance', {'currency': Coin})

    # Get Market Summaries
    def GetMarketSummaries(self):
        return self.BitRetrieval(self, 'getmarketsummaries', {})

    def GetMarketHistory(self, market, count):
        return self.BitRetrieval(self, 'getmarkethistory', {'market': market, 'count': count})

    # Get Open Orders
    def GetOrderUUIDIndividual(self, Coin, Type):
        Orders = self.BitRetrieval(self, 'getopenorders')
        x = Orders['result']
        for Order in x:
            if Order['OrderType'] == "LIMIT_SELL":
                Coin = ('BTC-' & Coin)
                if Order['Exchange'] == Coin:
                    return Order['OrderUuid']

            if Order['OrderType'] == "LIMIT_BUY":
                Coin = ('BTC-' & Coin)
                if Order['Exchange'] == Coin:
                    return Order['OrderUuid']

    #Cancel the order
    def CancelOrder(self, UUID):
        self.BitRetrieval(self, 'cancel', {'uuid': UUID})


    def BuyLimit(self, market, quantity, rate):
        self.BitRetrieval(self, 'buylimit', {'market': market, 'quantity': quantity, 'rate': rate})


    def SellLimit(self, market, quantity, rate):
        self.BitRetrieval(self, 'selllimit', {'market': market, 'quantity': quantity, 'rate': rate})

    def GetAllBalance(self):
        return self.BitRetrieval(self, 'getbalances', {})