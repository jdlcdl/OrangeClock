from color_setup import ssd
from gui.core.nanogui import refresh
from drivers.pico_hardware import (
    poll_bootsel,
    ack_short_press,
    ack_double_press,
    ack_long_press,
    nack_press,
)
from orangeClockFunctions.datastore import ExternalData
from orangeClockFunctions.compositors import composeClock, composeSetup
from orangeClockFunctions.datastore import (
    getDataSingleton,
    getPrice,
    getMoscowTime,
    getPriceDisplay,
    getLastBlock,
    getMempoolFees,
    getMempoolFeesString,
    getNostrZapCount,
    getNextHalving,
    setNostrPubKey,
)

import network
import time
import urequests
import json
import gc
import math

refresh_interval = 600
symbolRow1 = "A"
symbolRow2 = "H"
symbolRow3 = "C"
secretsSSID = ""
secretsPASSWORD = ""
npub = ""
all_dispVersions = (
    ("bh", "hal"),				# top: dispVersion1
    ("mts", "mts2", "mt", "fp1", "fp2"),        # middle: dispVersion2
)

def connectWIFI():
    global wifi
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(secretsSSID, secretsPASSWORD)
    time.sleep(1)
    print(wifi.isconnected())


def setSelectDisplay(displayVersion1, nPub, displayVersion2):
    global npub
    npub = nPub

    global dispVersion
    dispVersion = [displayVersion1, displayVersion2]


def setSecrets(SSID, PASSWORD):
    global secretsSSID
    global secretsPASSWORD
    secretsSSID = SSID
    secretsPASSWORD = PASSWORD


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


def displayInit():
    refresh(ssd, True)
    ssd.wait_until_ready()
    time.sleep(5)
    ssd._full = False
    ssd.wait_until_ready()
    refresh(ssd, True)
    ssd.wait_until_ready()
    ssd.sleep()  # deep sleep
    time.sleep(5)


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
    global data
    debugConsoleOutput("1")
    issue = False
    blockHeight = ""
    textRow2 = ""
    mempoolFees = ""
    i = 1
    connectWIFI()

    data = getDataSingleton()
    if npub:
        setNostrPubKey(nPub)

    displayInit()
    while True:
        debugConsoleOutput("2")
        if issue:
            issue = False
        if i > 72:
            i = 1
            refresh(ssd, True)  # awake from deep sleep
            time.sleep(5)
            ssd._full = True
            ssd.wait_until_ready()
            refresh(ssd, True)
            ssd.wait_until_ready()
            time.sleep(20)
            ssd._full = False
            ssd.wait_until_ready()
            refresh(ssd, True)
            time.sleep(5)
        try:
            if dispVersion[0] == "zap":
                symbolRow1 = "F"
                blockHeight = str(getNostrZapCount(npub))
            elif dispVersion[0] == "hal":
                symbolRow1 = "E"
                blockHeight = str(getNextHalving())
            else:
                symbolRow1 = "A"
                blockHeight = str(getLastBlock())
        except Exception as err:
            blockHeight = "connection error"
            symbolRow1 = ""
            print("Block: Handling run-time error:", err)
            debugConsoleOutput("3")
            issue = True
        try:
            if dispVersion[1] == "mt":
                symbolRow2 = ""
                textRow2 = str(getMoscowTime())
            elif dispVersion[1] == "mts2":
                symbolRow2 = "I"
                textRow2 = str(getMoscowTime())
            elif dispVersion[1] == "fp1":
                symbolRow2 = "K"
                textRow2 = getPriceDisplay("USD")
            elif dispVersion[1] == "fp2":
                symbolRow2 = "B"
                textRow2 = getPriceDisplay("EUR")
            else:
                symbolRow2 = "H"
                textRow2 = str(getMoscowTime())
        except Exception as err:
            textRow2 = "error"
            symbolRow2 = ""
            print("Moscow: Handling run-time error:", err)
            debugConsoleOutput("4")
            issue = True
        try:
            symbolRow3 = "C"
            mempoolFees = getMempoolFeesString()
        except Exception as err:
            mempoolFees = "connection error"
            symbolRow3 = ""
            print("Fees: Handling run-time error:", err)
            debugConsoleOutput("5")
            issue = True

        labels = composeClock(
            ssd,
            (blockHeight, symbolRow1),
            (textRow2, symbolRow2),
            (mempoolFees, symbolRow3)
        )

        refresh(ssd, False)
        ssd.wait_until_ready()
        ssd.sleep()
        last_refreshed = time.time()
        if not issue:
            while time.time() < last_refreshed + refresh_interval:
                pressed = poll_bootsel(timeout_s=min(
                        60, time.time() - last_refreshed + refresh_interval
                ))
                if not pressed:
                    continue
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

                new_data = False
                for key, datum in data.items():
                    result = datum.refresh()
                    if result == False:
                        print("data[{}].refresh() returned False".format(key))
                    elif result == True:
                        new_data = True
                        print("{} data changed".format(key))
                if new_data:
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
