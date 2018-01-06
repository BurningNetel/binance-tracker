import pymongo
import sys
import binance
import threading 
import time

MONGODB_PORT = 27017
MONGODB_HOST = "localhost"
client = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT)
db = client.crypto
balancesCollection = db.balances
pricesCollection = db.prices


class RepeatedTimer(object):
  def __init__(self, interval, function, *args, **kwargs):
    self._timer = None
    self.interval = interval
    self.function = function
    self.args = args
    self.kwargs = kwargs
    self.is_running = False
    self.next_call = time.time()
    self.start()

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def start(self):
    if not self.is_running:
      self.next_call += self.interval
      self._timer = threading.Timer(self.next_call - time.time(), self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    self._timer.cancel()
    self.is_running = False


def getBalances():
    balances = binance.balances()
    prices = binance.prices()
    currentDateTime = time.time()
    dataBalances = {"balances":balances, "date":currentDateTime}
    dataPrices = {"prices":prices, "date":currentDateTime}
    balancesCollection.insert_one(dataBalances)
    pricesCollection.insert_one(dataPrices)
    print("inserted data")

def main():
    args =  sys.argv[1:]
    secret = args[0]
    apikey = args[1]
    binance.set(apikey, secret)

    rt = RepeatedTimer(60, getBalances)
    rt.start()
    print("Started!")

if __name__ == "__main__":
    main()

