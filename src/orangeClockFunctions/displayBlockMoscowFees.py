from color_setup import ssd
from gui.core.nanogui import refresh
from drivers.pico_hardware import (
    poll_bootsel,
    ack_short_press,
    ack_double_press,
    ack_long_press,
    nack_press,
)
from orangeClockFunctions.compositors import composeClock, composeSetup
from orangeClockFunctions import datastore
from orangeClockFunctions.logging import log_exception

import network
import time
import urequests
import json
import gc
import math


refresh_interval = 30
symbolRow1 = "A"
symbolRow2 = "L"
symbolRow3 = "F"
secretsSSID = ""
secretsPASSWORD = ""
npub = ""
all_dispVersions = (
    ("bh", "hal", "nda", "zap"),                               # top: dispVersion1
    ("mts", "mts2", "mt", "fp1", "fp2", "mch", "mcd", "dbt"),  # middle: dispVersion2
)


#
# network setup
#
def connectWIFI():
    global wifi
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(secretsSSID, secretsPASSWORD)
    time.sleep(1)
    print(wifi.isconnected())

def setSecrets(SSID, PASSWORD):
    global secretsSSID
    global secretsPASSWORD
    secretsSSID = SSID
    secretsPASSWORD = PASSWORD


#
# display setup
#
def setSelectDisplay(displayVersion1, nPub, displayVersion2):
    global npub
    npub = nPub

    global dispVersion
    dispVersion = [displayVersion1, displayVersion2]

def displayInit():
    refresh(ssd, True)
    ssd.wait_until_ready()
    ssd._full = False
    refresh(ssd, True)
    ssd.wait_until_ready()
    ssd.sleep()  # deep sleep

def nextDispVersion(_next=True):
    def is_last_value(a_value, a_list):
        if _next:
            return a_list.index(a_value) == len(a_list)-1
        else:
            return a_list.index(a_value) == 0

    def next_value(a_value, a_list):
        if _next:
            return a_list[(a_list.index(a_value) + 1) % len(a_list)]
        else:
            return a_list[(a_list.index(a_value) - 1) % len(a_list)]

    for i, dispVer in reversed([xy for xy in enumerate(dispVersion)]):
        was_last = is_last_value(dispVer, all_dispVersions[i])
        dispVersion[i] = next_value(dispVer, all_dispVersions[i])
        if was_last:
            continue
        else:
            break


#
# functions that return "displayable" strings from datastore
#
def getMoscowTime():
    return str(int(100000000 / float(datastore.get_price("USD"))))

def getPriceDisplay(currency):
    price_str = f"{datastore.get_price(currency):,}"
    if currency == "EUR":
        price_str = price_str.replace(",", ".")
    return price_str

def getLastBlock():
    return str(datastore.get_height())

def getMempoolFeesString():
    mempoolFees = datastore.get_fees_dict()
    mempoolFeesString = (
        "L:"
        + str(mempoolFees["hourFee"])
        + " M:"
        + str(mempoolFees["halfHourFee"])
        + " H:"
        + str(mempoolFees["fastestFee"])
    )
    return mempoolFeesString

def getNostrZapCount():
    return str(datastore.get_nostr_zap_count())

def getNextHalving():
    return str(210000 - datastore.get_height() % 210000)

def getHashrateDisplay():
    return "{:0.1f}e18".format(datastore.get_mining("currentHashrate") / 10**18)

def getDifficultyDisplay():
    return "{:0.2f}e12".format(datastore.get_mining("currentDifficulty") / 10**12)

def getNextDifficultyAdjustment():
    return str(2016 - datastore.get_height() % 2016)

def getUSTotalPublicDebtOutstandingDisplay():
    return "{:0.2f}e12".format(datastore.get_usdebt("tot_pub_debt_out_amt") / 10**12)


def debugConsoleOutput(id):
    mem_alloc = gc.mem_alloc()
    print("=============== debug id=" + id + " ===============")
    print("memory used: ", mem_alloc / 1024, "KiB")
    print("memory free: ", gc.mem_free() / 1024, "KiB")
    gc.collect()
    print("gc.collect() freed additional:", (mem_alloc - gc.mem_alloc()) / 1024, "KiB")
    print("=============== end debug ===============")


def main():
    gc.enable()
    global wifi
    global secretsSSID
    global secretsPASSWORD
    debugConsoleOutput("1")
    issue = False
    blockHeight = ""
    textRow2 = ""
    mempoolFees = ""
    i = 1
    connectWIFI()

    datastore.initialize()
    if npub:
        datastore.set_nostr_pubkey(npub)

    displayInit()
    while True:
        debugConsoleOutput("2")
        if issue:
            issue = False
        if i > 72*20:
            i = 1
            refresh(ssd, True)  # awake from deep sleep
            ssd._full = True
            ssd.wait_until_ready()
            refresh(ssd, True)
            ssd.wait_until_ready()
            ssd._full = False
            ssd.wait_until_ready()
            refresh(ssd, True)
        try:
            if dispVersion[0] == "zap":
                symbolRow1 = "I"
                blockHeight = str(getNostrZapCount())
            elif dispVersion[0] == "hal":
                symbolRow1 = "H"
                blockHeight = getNextHalving()
            elif dispVersion[0] == "nda":
                symbolRow1 = "G"
                blockHeight = getNextDifficultyAdjustment()
            else:
                symbolRow1 = "A"
                blockHeight = getLastBlock()
        except Exception as err:
            log_exception(err)
            blockHeight = "connection error"
            symbolRow1 = ""
            print("Block: Handling run-time error:", err)
            debugConsoleOutput("3")
            issue = True
        try:
            if dispVersion[1] == "mt":
                symbolRow2 = ""
                textRow2 = getMoscowTime()
            elif dispVersion[1] == "mts2":
                symbolRow2 = "M"
                textRow2 = getMoscowTime()
            elif dispVersion[1] == "fp1":
                symbolRow2 = "E"
                textRow2 = getPriceDisplay("USD")
            elif dispVersion[1] == "fp2":
                symbolRow2 = "B"
                textRow2 = getPriceDisplay("EUR")
            elif dispVersion[1] == "mch":
                symbolRow2 = "A"
                textRow2 = getHashrateDisplay()
            elif dispVersion[1] == "mcd":
                symbolRow2 = "B"
                textRow2 = getDifficultyDisplay()
            elif dispVersion[1] == "dbt":
                symbolRow2 = "K"
                textRow2 = getUSTotalPublicDebtOutstandingDisplay()
            else:
                symbolRow2 = "L"
                textRow2 = getMoscowTime()
        except Exception as err:
            log_exception(err)
            textRow2 = "error"
            symbolRow2 = ""
            print("Moscow: Handling run-time error:", err)
            debugConsoleOutput("4")
            issue = True
        try:
            symbolRow3 = "F"
            mempoolFees = getMempoolFeesString()
        except Exception as err:
            log_exception(err)
            mempoolFees = "connection error"
            symbolRow3 = ""
            print("Fees: Handling run-time error:", err)
            debugConsoleOutput("5")
            issue = True

        labels = composeClock(
            ssd,
            (blockHeight, symbolRow1),
            (textRow2, symbolRow2),
            (mempoolFees, symbolRow3),
            show_warning = bool(datastore.list_stale())
        )

        refresh(ssd, False)
        ssd.wait_until_ready()
        ssd.sleep()
        last_refreshed = time.time()
        if not issue:
            while time.time() < last_refreshed + refresh_interval:
                pressed = poll_bootsel(timeout_s=min(
                        30, time.time() - last_refreshed + refresh_interval
                ))
                if not pressed:
                    pass
                elif pressed == "short":
                    ack_short_press()
                    nextDispVersion()
                    break
                elif pressed == "double":
                    ack_double_press()
                    nextDispVersion(False)
                    break
                elif pressed == "long":
                    ack_long_press()
                    ssid_str = secretsSSID
                    ipaddr_str = "http://" + wifi.ifconfig()[0]
                    if len(ssid_str) > 17:
                        ssid_str = ssid_str[:14] + "..."
                    if len(ipaddr_str) > 19:
                        ipaddr_str = "..." + ipaddr_str[-15:]
                    for label in labels:
                        label.value("")
                    labels = composeSetup(
                        ssd,
                        ("app server:", "J"),
                        (ssid_str, "L"),
                        (ipaddr_str, "D")
                    )  
                    refresh(ssd, False)
                    ssd.wait_until_ready()
                    ssd.sleep()
                    return				
                else:
                    nack_press()
                    continue

                new_data = datastore.refresh()
                if new_data:
                    print("datastore.refresh() had updates: {}".format(",".join(new_data)))
                    break
        else:
            wifi.disconnect()
            debugConsoleOutput("6")
            wifi.connect(secretsSSID, secretsPASSWORD)
            time.sleep(60)

        # Have the Labels write blanks into the framebuf to erase what they
        # rendered in the previous cycle.
        for label in labels:
            label.value("")
            
        i = i + 1
