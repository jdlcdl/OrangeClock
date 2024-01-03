import time
import requests


class ExternalData:
    def __init__(self, url, ttl=300, json=True):
        self.url = url
        self.ttl = ttl
        self.json = json
        self.updated = None
        self.data = None
        self.refresh()

    def __str__(self):
        return 'ExternalData("{}")'.format(self.url)

    def refresh(self):
        now = time.time()

        if self.updated and self.updated + self.ttl > now:
            return False

        with requests.get(self.url) as data:
            if data.status_code != 200:
                print("ExternalData error: status_code: {}".format(
                    data.status_code
                ))
                return False

            if self.json:
                self.data = data.json()
            else:
                self.data = data.text

        self.updated = now

        return True


if __name__ == '__main__':
    def time_it(a_callable):
        now = time.time()
        result = a_callable()
        return "returned {} in {:0.3f}s".format(
            result, time.time() - now)
    
    prices = ExternalData('https://mempool.space/api/v1/prices', 300)
    fees = ExternalData('https://mempool.space/api/v1/fees/recommended', 120)
    height = ExternalData('https://mempool.space/api/blocks/tip/height', 180, json=False)

    while True:
        print()
        print("{}.refresh() {}".format(prices, time_it(prices.refresh)))
        print("{}.refresh() {}".format(fees, time_it(fees.refresh)))
        print("{}.refresh() {}".format(height, time_it(height.refresh)))
        time.sleep(30)
