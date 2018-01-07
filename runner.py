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
    """Runs a function at every interval without drift due to execution time of the function."""
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


def get_balances():
    balances = binance.balances()
    prices = binance.prices()
    epoch = time.time()
    data_balances = {"balances": balances, "date": epoch}
    data_prices = {"prices": prices, "date": epoch}
    balancesCollection.insert_one(data_balances)
    pricesCollection.insert_one(data_prices)
    print("inserted data")


def main():
    args = sys.argv[1:]
    secret_key = args[0]
    api_key = args[1]
    binance.set(api_key, secret_key)

    rt = RepeatedTimer(60, get_balances)
    rt.start()
    print("Started!")


if __name__ == "__main__":
    main()
