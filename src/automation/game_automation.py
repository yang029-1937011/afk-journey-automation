import time
from .click_simulation import clickOnScreenShoot

# Global stop flag
_stop_flag = None

def set_stop_flag(flag):
    """Set the stop flag from main"""
    global _stop_flag
    _stop_flag = flag

def stop_automation():
    """Signal all automation to stop"""
    global _stop_flag
    if _stop_flag:
        _stop_flag.set()

def should_stop():
    """Check if automation should stop"""
    global _stop_flag
    return _stop_flag and _stop_flag.is_set()

def autoFight():
    cnt = 5000
    fail = 0
    while cnt > 0 and fail < 60:
        if should_stop():
            print("Auto Fight stopped by user")
            return
        if fail % 6 == 0:
            clickOnScreenShoot("record.png")
            time.sleep(3)
            for i in range(fail // 6):
                clickOnScreenShoot("next.png", focus=False)
                time.sleep(0.5)
            clickOnScreenShoot("adoptTeam.png", focus=False)
            time.sleep(1)
        clickOnScreenShoot("checkMark.png", focus=False)
        time.sleep(1)

        clickOnScreenShoot("fight.png", focus=False)
        time.sleep(1)

        clickOnScreenShoot("checkMark.png", focus=False)
        time.sleep(5)

        cnt2 = 100
        while cnt2 > 0:
            if clickOnScreenShoot("fightAgain.png", focus=False):
                print("battle lost")
                fail += 1
                break
            if clickOnScreenShoot("challenge.png", focus=False):
                print("battle won")
                fail = 0
                break

            time.sleep(2)
            cnt2 -= 1
        print(f"fail {fail}")

        time.sleep(4)
        cnt -= 1

def autoPFightFriends():
    cnt = 500
    fail = 0
    while cnt > 0 and fail < 15:
        if should_stop():
            print("Auto P Fight Friends stopped by user")
            return
        clickOnScreenShoot("record.png")
        time.sleep(1)

        for i in range(fail // 2):
            clickOnScreenShoot("next.png", focus=False)
            time.sleep(0.5)

        clickOnScreenShoot("adoptTeam.png", focus=False)
        time.sleep(1)

        clickOnScreenShoot("checkMark.png", focus=False)
        time.sleep(1)
        clickOnScreenShoot("fight.png", focus=False)

        time.sleep(5)

        cnt2 = 9
        while cnt2 > 0:
            if clickOnScreenShoot("fightAgain.png", focus=False):
                print("battle lost")
                fail += 1
                break
            if clickOnScreenShoot("nextLevel.png", focus=False):
                print("battle won")
                time.sleep(3)
                clickOnScreenShoot("challenge3.png", focus=False)
                fail = 0
                break

            time.sleep(3)
            cnt2 -= 1
        print(f"fail {fail}")

        time.sleep(4)
        cnt -= 1

def autoFightFriends():
    cnt = 500
    fail = 0
    while cnt > 0 and fail < 15:
        if should_stop():
            print("Auto Fight Friends stopped by user")
            return
        clickOnScreenShoot("record.png")
        time.sleep(1)

        for i in range(fail // 2):
            clickOnScreenShoot("next.png", focus=False)
            time.sleep(0.5)

        clickOnScreenShoot("adoptTeam.png", focus=False)
        time.sleep(1)

        clickOnScreenShoot("checkMark.png", focus=False)
        time.sleep(1)
        clickOnScreenShoot("fight.png", focus=False)

        time.sleep(5)

        cnt2 = 9
        while cnt2 > 0:
            if clickOnScreenShoot("fightAgain.png", focus=False):
                print("battle lost")
                fail += 1
                break
            if clickOnScreenShoot("nextLevel.png", focus=False):
                print("battle won")
                time.sleep(3)
                clickOnScreenShoot("challenge.png", focus=False)
                fail = 0
                break

            time.sleep(3)
            cnt2 -= 1
        print(f"fail {fail}")

        time.sleep(4)
        cnt -= 1

def autoPFight():
    cnt = 5000
    fail = 0
    failCnt = 3
    while cnt > 0 and fail < 60:
        if should_stop():
            print("Auto P Fight stopped by user")
            return
        if fail % failCnt == 0:
            clickOnScreenShoot("record.png")
            time.sleep(1)
            for i in range(fail // failCnt):
                clickOnScreenShoot("next.png", focus=False)
                time.sleep(0.5)
            clickOnScreenShoot("adoptTeam.png", focus=False)
            time.sleep(1)

        clickOnScreenShoot("checkMark.png", focus=False)
        time.sleep(1)
        clickOnScreenShoot("fight.png", focus=False)

        time.sleep(2)
        clickOnScreenShoot("checkMark.png", focus=False)
        time.sleep(1)

        clickOnScreenShoot("fight.png", focus=False)

        cnt2 = 100
        while cnt2 > 0:
            if clickOnScreenShoot("fightAgain.png", focus=False):
                print("battle lost")
                fail += 1
                break
            if clickOnScreenShoot("challenge3.png", focus=False):
                print("battle won")
                fail = 0
                break

            time.sleep(3)
            cnt2 -= 1
        print(f"fail {fail}")

        time.sleep(5)
        cnt -= 1

def FactionChallenge():
    RECORD_DELAY = 1
    NEXT_DELAY = 0.5
    ADOPT_DELAY = 1
    CHECK_MARK_DELAY = 1
    FIGHT_DELAY = 2
    SECOND_FIGHT_DELAY = 1
    BATTLE_CHECK_DELAY = 3
    END_DELAY = 2

    cnt = 5000
    fail = 0

    while cnt > 0 and fail < 15:
        if should_stop():
            print("Faction Challenge stopped by user")
            return
        clickOnScreenShoot("record.png")
        time.sleep(RECORD_DELAY)

        for i in range(fail // 2):
            clickOnScreenShoot("next.png", focus=False)
            time.sleep(NEXT_DELAY)

        clickOnScreenShoot("adoptTeam.png", focus=False)
        time.sleep(ADOPT_DELAY)

        clickOnScreenShoot("checkMark.png", focus=False)
        time.sleep(CHECK_MARK_DELAY)
        clickOnScreenShoot("fight.png", focus=False)

        time.sleep(FIGHT_DELAY)
        clickOnScreenShoot("checkMark.png", focus=False)
        time.sleep(SECOND_FIGHT_DELAY)

        clickOnScreenShoot("fight.png", focus=False)

        cnt2 = 9
        while cnt2 > 0:
            if clickOnScreenShoot("fightAgain.png", focus=False):
                print("battle lost")
                fail += 1
                break
            if clickOnScreenShoot("nextLevel.png", focus=False):
                print("battle won")
                fail = 0
                break

            time.sleep(BATTLE_CHECK_DELAY)
            cnt2 -= 1

        print(f"fail {fail}")
        time.sleep(END_DELAY)
        cnt -= 1