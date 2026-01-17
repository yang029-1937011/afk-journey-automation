"""AFK Journey Automation - Main GUI Application."""

import argparse
import os
import sys
import threading
from tkinter import Tk, Button, Label, StringVar, OptionMenu, Frame

from PIL import Image, ImageTk, ImageDraw

from automation.game_automation import (
    autoFight,
    autoPFightFriends,
    autoFightFriends,
    autoPFight,
    FactionChallenge,
    set_stop_flag,
    stop_automation,
)
from automation.click_simulation import set_language, set_debug_mode
from utils.admin import is_admin, request_admin


# =============================================================================
# Constants
# =============================================================================

VERSION = "1.0"


def get_base_path() -> str:
    """Get the base path, works both in dev and when packaged with PyInstaller."""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return sys._MEIPASS
    else:
        # Running in development
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Theme colors (One Dark inspired)
class Colors:
    """Color palette for the GUI."""
    BG_DARK = "#1e1e1e"
    BG_LIGHTER = "#3c3c3c"
    TEXT_PRIMARY = "#abb2bf"
    TEXT_MUTED = "#5c6370"
    ACCENT_BLUE = "#61afef"
    ACCENT_YELLOW = "#e5c07b"
    ACCENT_PURPLE = "#c678dd"
    ACCENT_GREEN = "#98c379"
    ACCENT_RED = "#e06c75"
    ACCENT_RED_HOVER = "#be5046"
    WHITE = "#ffffff"


# GUI dimensions
WINDOW_WIDTH = 450
WINDOW_HEIGHT = 850
AVATAR_SIZE = 40
BUTTON_WIDTH = 28


# =============================================================================
# Threading Utilities
# =============================================================================

# Global flag to stop execution
stop_flag = threading.Event()
set_stop_flag(stop_flag)


def run_in_thread(func):
    """Decorator to run a function in a separate thread to prevent GUI freezing."""
    def wrapper():
        stop_flag.clear()
        thread = threading.Thread(target=func, daemon=True)
        thread.start()
    return wrapper


# =============================================================================
# Automation Wrappers
# =============================================================================

@run_in_thread
def run_autoFight():
    autoFight()


@run_in_thread
def run_autoPFightFriends():
    autoPFightFriends()


@run_in_thread
def run_autoFightFriends():
    autoFightFriends()


@run_in_thread
def run_autoPFight():
    autoPFight()


@run_in_thread
def run_FactionChallenge():
    FactionChallenge()


def change_language(lang: str) -> None:
    """Change the language for asset loading."""
    set_language(lang)
    print(f"Language set to {lang}")


def stop_execution() -> None:
    """Stop all running automation."""
    stop_automation()
    print("Automation stopped.")


# =============================================================================
# GUI Components
# =============================================================================

def create_button(parent: Frame, text: str, command, color: str) -> Button:
    """Create a styled button with hover effects."""
    btn = Button(
        parent,
        text=text,
        command=command,
        font=("Segoe UI", 11, "bold"),
        bg=color,
        fg=Colors.BG_DARK,
        activebackground=Colors.WHITE,
        activeforeground=Colors.BG_DARK,
        relief="flat",
        cursor="hand2",
        width=BUTTON_WIDTH,
        height=1,
        bd=0,
        pady=10,
    )
    
    def on_enter(e):
        btn.config(bg=Colors.WHITE)
    
    def on_leave(e):
        btn.config(bg=color)
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn


def create_round_avatar(path: str, size: int = AVATAR_SIZE):
    """Create a circular avatar image from file."""
    if not os.path.exists(path):
        return None
    
    img = Image.open(path)
    img = img.resize((size, size), Image.LANCZOS)
    
    # Create circular mask
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    
    # Apply mask
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output.paste(img, (0, 0))
    output.putalpha(mask)
    
    return ImageTk.PhotoImage(output)


def create_gui() -> None:
    """Create and run the main GUI application."""
    root = Tk()
    root.title("AFK Journey Automation")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.configure(bg=Colors.BG_DARK)
    root.resizable(False, False)

    # Main container
    container = Frame(root, bg=Colors.BG_DARK)
    container.pack(fill="both", expand=True, padx=40, pady=20)

    # Footer - pack first at the bottom
    footer_frame = Frame(container, bg=Colors.BG_DARK)
    footer_frame.pack(side="bottom", fill="x", pady=(20, 0))

    # Avatar
    base_path = get_base_path()
    avatar_path = os.path.join(base_path, "assets", "avator.jpg")
    avatar_photo = create_round_avatar(avatar_path)
    
    if avatar_photo:
        avatar_label = Label(footer_frame, image=avatar_photo, bg=Colors.BG_DARK)
        avatar_label.image = avatar_photo  # Keep reference
        avatar_label.pack(side="left", padx=(0, 10))

    # Author and version
    Label(
        footer_frame,
        text="Authored by ylx",
        font=("Segoe UI", 10),
        fg=Colors.TEXT_MUTED,
        bg=Colors.BG_DARK,
    ).pack(side="left")

    Label(
        footer_frame,
        text=f" • v{VERSION}",
        font=("Segoe UI", 10),
        fg=Colors.TEXT_MUTED,
        bg=Colors.BG_DARK,
    ).pack(side="left")

    # Main content frame - pack after footer
    main_frame = Frame(container, bg=Colors.BG_DARK)
    main_frame.pack(fill="both", expand=True)

    # Title
    Label(
        main_frame,
        text="AFK Journey",
        font=("Segoe UI", 24, "bold"),
        fg=Colors.ACCENT_BLUE,
        bg=Colors.BG_DARK,
    ).pack(pady=(0, 5))

    Label(
        main_frame,
        text="Automation Tool",
        font=("Segoe UI", 14),
        fg=Colors.TEXT_PRIMARY,
        bg=Colors.BG_DARK,
    ).pack(pady=(0, 15))

    # Language selection
    lang_frame = Frame(main_frame, bg=Colors.BG_DARK)
    lang_frame.pack(fill="x", pady=(0, 15))

    Label(
        lang_frame,
        text="Language:",
        font=("Segoe UI", 12),
        fg=Colors.ACCENT_YELLOW,
        bg=Colors.BG_DARK,
    ).pack(side="left", padx=(0, 15))

    language_var = StringVar(root, value="EN")
    lang_menu = OptionMenu(lang_frame, language_var, "EN", "CN", command=change_language)
    lang_menu.config(
        font=("Segoe UI", 11),
        bg=Colors.BG_LIGHTER,
        fg=Colors.WHITE,
        activebackground=Colors.ACCENT_BLUE,
        activeforeground=Colors.WHITE,
        highlightthickness=0,
        width=10,
        relief="flat",
    )
    lang_menu["menu"].config(
        bg=Colors.BG_LIGHTER,
        fg=Colors.WHITE,
        activebackground=Colors.ACCENT_BLUE,
        activeforeground=Colors.WHITE,
        font=("Segoe UI", 11),
    )
    lang_menu.pack(side="left")

    # Separator
    Frame(main_frame, height=2, bg=Colors.BG_LIGHTER).pack(fill="x", pady=(0, 15))

    # Actions label
    Label(
        main_frame,
        text="Select an Action",
        font=("Segoe UI", 13),
        fg=Colors.ACCENT_GREEN,
        bg=Colors.BG_DARK,
    ).pack(pady=(0, 15))

    # Action buttons
    buttons_config = [
        ("Auto Fight", run_autoFight, Colors.ACCENT_BLUE),
        ("Auto P Fight", run_autoPFight, Colors.ACCENT_YELLOW),
        ("Auto Fight Friends", run_autoFightFriends, Colors.ACCENT_PURPLE),
        ("Auto P Fight Friends", run_autoPFightFriends, Colors.ACCENT_PURPLE),
        ("Faction Challenge", run_FactionChallenge, Colors.ACCENT_GREEN),
    ]

    for text, command, color in buttons_config:
        btn = create_button(main_frame, text, command, color)
        btn.pack(pady=4)

    # Stop button (same style as other buttons)
    stop_btn = create_button(main_frame, "⏹  Stop Automation", stop_execution, Colors.ACCENT_RED)
    stop_btn.pack(pady=4)

    root.mainloop()


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="AFK Journey Automation Tool",
        epilog="Example: AFK-Journey-Automation.exe --debug"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (show detailed logs for template matching and clicks)"
    )
    
    args = parser.parse_args()
    
    # Set debug mode from CLI argument
    if args.debug:
        set_debug_mode(True)
        print("Debug mode enabled via command line")
    
    # Request administrator privileges if not already elevated
    # This is needed to interact with games that run as admin
    request_admin()
    
    # Show admin status
    if is_admin():
        print("✓ Running with administrator privileges")
    else:
        print("⚠ Running without administrator privileges")
        print("  If automation doesn't work, try 'Run as administrator'")
    
    create_gui()