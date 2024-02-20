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


def getMoscowTime():
    return int(100000000 / float(getPrice("USD")))

def getPriceDisplay(currency):
    price_str = f"{getPrice(currency):,}"
    if currency == "EUR":
        price_str = price_str.replace(",", ".")
    return price_str

def getHashrateDisplay():
    # need more fonts for below "E","H","/","s"
    #return "{:0.1f} EH/s".format(getCurrentHashrate() / 10**18)
    return "{:0.1f}e18".format(getCurrentHashrate() / 10**18)

def getDifficultyDisplay():
    # need more fonts for below "T"
    #return "{:0.2f}T".format(getCurrentDifficulty() / 10**12)
    return "{:0.2f}e12".format(getCurrentDifficulty() / 10**12)

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

def getNextHalving():
    return 210000 - getLastBlock() % 210000

def getNextDifficultyAdjustment():
    return 2016 - getLastBlock() % 2016


# _data is a singleton dict holding raw data from sources -- used internally,
# else use getDataSingleton()
_data = None

def getLastBlock():
    return int(_data["height"].data)

def getPrice(currency): # change USD to EUR for price in euro
    return _data["prices"].data[currency]

def getMempoolFees():
    return _data["fees"].data

def getCurrentHashrate():
    return _data['mining'].data["currentHashrate"]

def getCurrentDifficulty():
    return _data['mining'].data["currentDifficulty"]

def getNostrZapCount(nPub):
    return _data["zaps"].data["stats"][str(_data.json())[12:76]]["zaps_received"]["count"]

def setNostrPubKey(nPub):
    _data['zaps'] = ExternalData("https://api.nostr.band/v0/stats/profile/"+nPub, 300)


def getDataSingleton():
    global _data
    if _data == None:
        _data = {
            "prices": ExternalData("https://mempool.space/api/v1/prices", 300),
            "fees": ExternalData("https://mempool.space/api/v1/fees/recommended", 120),
            "height": ExternalData("https://mempool.space/api/blocks/tip/height", 180, json=False),
            "mining": ExternalData("https://mempool.space/api/v1/mining/hashrate/3d", 180),
        }
    return _data
