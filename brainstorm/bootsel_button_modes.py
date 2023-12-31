"""
brainstorm: 
    rp2.bootsel_button() returns int(1) if pressed, else int(0).
    Perhaps this can be used for:
    * "next" (short press), 
    * "prev" (long press ~2s)
    * "config" (extra long press ~5s)

    Then modes could be changed by hand using the bootsel_button.
    They might auto-next-mode every x seconds via settings config.
    Not all modes will be interesting for all user, so enabling
    which modes are included in all_modes would be a user preference.
"""

all_modes = (
    ("Block Time", "Halving Countdown", "Nostr Zap Counter"),
    ("Moscow Time (satsymbol icon)", "Moscow Time (sat/USD icon)", "Moscow Time (noicon)", "Fiat Price ($)", "Fiat Price (€)"),
    ("Transaction Fees",)
)

modes = [all_modes[0][0], all_modes[1][0], all_modes[2][0]]
def nextMode(_next=True):
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

    for i, mode in reversed([xy for xy in enumerate(modes)]):
        was_last = is_last_value(mode, all_modes[i])
        modes[i] = next_value(mode, all_modes[i])
        if was_last:
            continue
        else:
            break

def dispMode():
    return ("{}, {}, {}".format(*modes))

if __name__ == '__main__':
    print("\nIncrementing through next modes (from: {})...".format(
        dispMode()
    ))
    for i in range(len(all_modes[0]) * len(all_modes[1]) * len(all_modes[2])):
        nextMode()
        print(dispMode())

    print("\nIncrementing through previous modes (from: {})...".format(
        dispMode()
    ))
    for i in range(len(all_modes[0]) * len(all_modes[1]) * len(all_modes[2])):
        nextMode(False)
        print(dispMode())
