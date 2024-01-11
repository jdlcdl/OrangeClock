import time
import requests


def getPrice(currency): # change USD to EUR for price in euro
    return data["prices"].data[currency]


def getMoscowTime():
    moscowTime = str(int(100000000 / float(getPrice("USD"))))
    return moscowTime


def getPriceDisplay(currency):
    price_str = f"{getPrice(currency):,}"
    if currency == "EUR":
        price_str = price_str.replace(",", ".")
    return price_str


def getLastBlock():
    return data["height"].data


def getMempoolFees():
    return data["fees"].data


def getMempoolFeesString():
    mempoolFees = getMempoolFees()
    mempoolFeesString = (
        "L:"
        + str(mempoolFees["hourFee"])
        + " M:"
        + str(mempoolFees["halfHourFee"])
        + " H:"
        + str(mempoolFees["fastestFee"])
    )
    return mempoolFeesString


def getNostrZapCount(nPub):
    jsonData = str(data["zaps"].data["stats"][str(data.json())[12:76]]["zaps_received"]["count"])
    return jsonData


def getNextHalving():
    return 210000 - getLastBlock() % 210000


def setNostrPubKey(nPub):
    data['zaps'] = ExternalData("https://api.nostr.band/v0/stats/profile/"+nPub, 300)


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
        answer = None

        if self.updated and self.updated + self.ttl > now:
            return answer

        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                if self.json:
                    data = response.json()
                else:
                    data = response.text
                self.updated = now
            else:
                print("status_code {}: requests.get({})".format(status_code, self.url))
                data = self.data
                answer = False
        except Exception as err:
            print("Exception {}: requests.get({})".format(err, self.url))
            data = self.data
            answer = False
        finally:
            try: response.close()
            except Exception: pass

        if data != self.data:
            self.data = data
            answer = True

        return answer


# a singleton to be imported by others.  (use setNostrPubKey() for "zaps" data setup)
data = {
    "prices": ExternalData("https://mempool.space/api/v1/prices", 300),
    "fees": ExternalData("https://mempool.space/api/v1/fees/recommended", 120),
    "height": ExternalData("https://mempool.space/api/blocks/tip/height", 180, json=False),
}
