"""Game automation functions for AFK Journey."""

import time
from typing import Optional, Callable
from threading import Event

from .click_simulation import clickOnScreenShoot, findImageLocation, click


# =============================================================================
# Constants
# =============================================================================

# Timing constants (in seconds)
class Delays:
    """Delay constants for various actions."""
    RECORD = 1.0
    NEXT = 0.5
    ADOPT = 1.0
    CHECK_MARK = 1.0
    FIGHT = 1.0
    BATTLE_WAIT = 5.0
    BATTLE_CHECK = 2.0
    END_ROUND = 4.0
    WIN_TRANSITION = 3.0


# Battle configuration
class BattleConfig:
    """Configuration for different battle types."""
    AUTO_FIGHT = {"max_rounds": 5000, "max_fails": 60, "fail_threshold": 6, "battle_checks": 100}
    AUTO_P_FIGHT = {"max_rounds": 5000, "max_fails": 60, "fail_threshold": 3, "battle_checks": 100}
    FRIENDS = {"max_rounds": 500, "max_fails": 15, "fail_threshold": 2, "battle_checks": 100}
    FACTION = {"max_rounds": 5000, "max_fails": 15, "fail_threshold": 2, "battle_checks": 100}


# Image assets
class Images:
    """Image file names for click detection."""
    RECORD = "record.png"
    NEXT = "next.png"
    ADOPT_TEAM = "adoptTeam.png"
    CHECK_MARK = "checkMark.png"
    FIGHT = "fight.png"
    FIGHT_AGAIN = "fightAgain.png"
    CHALLENGE = "challenge.png"
    CHALLENGE3 = "challenge3.png"
    NEXT_LEVEL = "nextLevel.png"


# =============================================================================
# Stop Flag Management
# =============================================================================

_stop_flag: Optional[Event] = None


def set_stop_flag(flag: Event) -> None:
    """Set the stop flag from main."""
    global _stop_flag
    _stop_flag = flag


def stop_automation() -> None:
    """Signal all automation to stop."""
    global _stop_flag
    if _stop_flag:
        _stop_flag.set()


def should_stop() -> bool:
    """Check if automation should stop."""
    global _stop_flag
    return _stop_flag is not None and _stop_flag.is_set()


# =============================================================================
# Helper Functions
# =============================================================================

def _select_team(fail_count: int, fail_threshold: int) -> None:
    """Select a team from the records based on fail count."""
    if should_stop():
        return
    
    clickOnScreenShoot(Images.RECORD)
    time.sleep(Delays.RECORD)
    
    if should_stop():
        return
    
    # Calculate how many times to click next
    next_clicks = fail_count // fail_threshold
    
    if next_clicks > 0:
        # Find NEXT button location once
        next_location = findImageLocation(Images.NEXT)
        
        if next_location:
            # Click the same location multiple times
            for i in range(next_clicks):
                if should_stop():
                    print("Team selection interrupted by stop request")
                    return
                click(next_location[0], next_location[1], focus=False)
                time.sleep(Delays.NEXT)
        else:
            # Fallback: use the old method if location not found
            print("Warning: NEXT button not found, skipping navigation")
    
    if should_stop():
        return
    
    clickOnScreenShoot(Images.ADOPT_TEAM, focus=False)
    time.sleep(Delays.ADOPT)


def _start_battle(double_confirm: bool = False) -> None:
    """Start a battle with optional double confirmation."""
    if should_stop():
        return
    
    clickOnScreenShoot(Images.CHECK_MARK, focus=False)
    time.sleep(Delays.CHECK_MARK)
    
    if should_stop():
        return
    
    clickOnScreenShoot(Images.FIGHT, focus=False)
    
    if double_confirm:
        time.sleep(Delays.FIGHT * 2)
        
        if should_stop():
            return
        
        clickOnScreenShoot(Images.CHECK_MARK, focus=False)
        time.sleep(Delays.CHECK_MARK)
        
        if should_stop():
            return
        
        clickOnScreenShoot(Images.FIGHT, focus=False)


def _wait_for_battle_result(
    win_image: str,
    max_checks: int,
    check_delay: float,
    on_win: Optional[Callable[[], None]] = None
) -> bool:
    """
    Wait for battle result and detect win/loss.
    
    Args:
        win_image: Image to detect for a win condition.
        max_checks: Maximum number of result checks.
        check_delay: Delay between checks.
        on_win: Optional callback to execute on win.
        
    Returns:
        True if battle was won, False if lost.
    """
    for _ in range(max_checks):
        # Check stop flag in the battle waiting loop
        if should_stop():
            print("Battle result check interrupted by stop request")
            return False
        
        if clickOnScreenShoot(Images.FIGHT_AGAIN, focus=False):
            print("battle lost")
            return False
        
        if clickOnScreenShoot(win_image, focus=False):
            print("battle won")
            if on_win:
                on_win()
            return True
        
        time.sleep(check_delay)
    
    return False


# =============================================================================
# Main Automation Functions
# =============================================================================

def autoFight() -> None:
    """
    Automated AFK challenge battle loop.
    
    Continuously fights battles, selecting different teams after consecutive failures.
    """
    config = BattleConfig.AUTO_FIGHT
    rounds = config["max_rounds"]
    fail = 0
    
    while rounds > 0 and fail < config["max_fails"]:
        if should_stop():
            print("Auto Fight stopped by user")
            return
        
        # Select team on first attempt or after threshold failures
        if fail % config["fail_threshold"] == 0:
            _select_team(fail, config["fail_threshold"])
        
        _start_battle()
        time.sleep(Delays.BATTLE_WAIT)
        
        # Wait for result
        won = _wait_for_battle_result(
            win_image=Images.CHALLENGE,
            max_checks=config["battle_checks"],
            check_delay=Delays.BATTLE_CHECK
        )
        
        fail = 0 if won else fail + 1
        print(f"fail count: {fail}")
        
        time.sleep(Delays.END_ROUND)
        rounds -= 1


def autoPFight() -> None:
    """
    Automated Phatimal challenge battle loop.
    
    Similar to autoFight but with double confirmation and different win detection.
    """
    config = BattleConfig.AUTO_P_FIGHT
    rounds = config["max_rounds"]
    fail = 0
    
    while rounds > 0 and fail < config["max_fails"]:
        if should_stop():
            print("Auto P Fight stopped by user")
            return
        
        # Select team on first attempt or after threshold failures
        if fail % config["fail_threshold"] == 0:
            _select_team(fail, config["fail_threshold"])
        
        _start_battle(double_confirm=True)
        
        # Wait for result
        won = _wait_for_battle_result(
            win_image=Images.CHALLENGE3,
            max_checks=config["battle_checks"],
            check_delay=Delays.BATTLE_CHECK + 1
        )
        
        fail = 0 if won else fail + 1
        print(f"fail count: {fail}")
        
        time.sleep(Delays.END_ROUND + 1)
        rounds -= 1


def autoFightFriends() -> None:
    """
    Automated friend challenge battle loop.
    
    Fights friend battles with level progression on wins.
    """
    config = BattleConfig.FRIENDS
    rounds = config["max_rounds"]
    fail = 0
    
    def on_win():
        if should_stop():
            return
        time.sleep(Delays.WIN_TRANSITION)
        if should_stop():
            return
        clickOnScreenShoot(Images.CHALLENGE, focus=False)
    
    while rounds > 0 and fail < config["max_fails"]:
        if should_stop():
            print("Auto Fight Friends stopped by user")
            return
        
        _select_team(fail, config["fail_threshold"])
        _start_battle()
        time.sleep(Delays.BATTLE_WAIT)
        
        # Wait for result
        won = _wait_for_battle_result(
            win_image=Images.NEXT_LEVEL,
            max_checks=config["battle_checks"],
            check_delay=Delays.BATTLE_CHECK + 1,
            on_win=on_win
        )
        
        fail = 0 if won else fail + 1
        print(f"fail count: {fail}")
        
        time.sleep(Delays.END_ROUND)
        rounds -= 1


def autoPFightFriends() -> None:
    """
    Automated friend Phatimal challenge battle loop.
    
    Similar to autoFightFriends but uses challenge3 image on win.
    """
    config = BattleConfig.FRIENDS
    rounds = config["max_rounds"]
    fail = 0
    
    def on_win():
        if should_stop():
            return
        time.sleep(Delays.WIN_TRANSITION)
        if should_stop():
            return
        clickOnScreenShoot(Images.CHALLENGE3, focus=False)
    
    while rounds > 0 and fail < config["max_fails"]:
        if should_stop():
            print("Auto P Fight Friends stopped by user")
            return
        
        _select_team(fail, config["fail_threshold"])
        _start_battle()
        time.sleep(Delays.BATTLE_WAIT)
        
        # Wait for result
        won = _wait_for_battle_result(
            win_image=Images.NEXT_LEVEL,
            max_checks=config["battle_checks"],
            check_delay=Delays.BATTLE_CHECK + 1,
            on_win=on_win
        )
        
        fail = 0 if won else fail + 1
        print(f"fail count: {fail}")
        
        time.sleep(Delays.END_ROUND)
        rounds -= 1


def FactionChallenge() -> None:
    """
    Automated faction challenge battle loop.
    
    Fights faction battles with double confirmation and level progression.
    """
    config = BattleConfig.FACTION
    rounds = config["max_rounds"]
    fail = 0
    
    while rounds > 0 and fail < config["max_fails"]:
        if should_stop():
            print("Faction Challenge stopped by user")
            return
        
        _select_team(fail, config["fail_threshold"])
        _start_battle(double_confirm=True)
        
        # Wait for result
        won = _wait_for_battle_result(
            win_image=Images.NEXT_LEVEL,
            max_checks=config["battle_checks"],
            check_delay=Delays.BATTLE_CHECK + 1
        )
        
        fail = 0 if won else fail + 1
        print(f"fail count: {fail}")
        
        time.sleep(Delays.END_ROUND - 2)
        rounds -= 1