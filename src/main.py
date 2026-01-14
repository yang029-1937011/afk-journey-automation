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
from automation.click_simulation import set_language
import threading
import os

# Global flag to stop execution
stop_flag = threading.Event()
set_stop_flag(stop_flag)

def run_in_thread(func):
    """Run a function in a separate thread to prevent GUI freezing"""
    def wrapper():
        stop_flag.clear()  # Reset stop flag before starting
        thread = threading.Thread(target=func)
        thread.daemon = True
        thread.start()
    return wrapper

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

def change_language(lang):
    set_language(lang)
    print(f"Language set to {lang}")

def stop_execution():
    """Stop all running automation"""
    stop_automation()
    print("Automation stopped.")

def create_gui():
    root = Tk()
    root.title("AFK Journey Automation")
    root.geometry("450x750")
    root.configure(bg="#1e1e1e")
    root.resizable(False, False)

    # Main frame with padding
    main_frame = Frame(root, bg="#1e1e1e")
    main_frame.pack(fill="both", expand=True, padx=40, pady=20)

    # Title
    title_label = Label(
        main_frame,
        text="AFK Journey",
        font=("Segoe UI", 24, "bold"),
        fg="#61afef",
        bg="#1e1e1e",
    )
    title_label.pack(pady=(0, 5))

    subtitle_label = Label(
        main_frame,
        text="Automation Tool",
        font=("Segoe UI", 14),
        fg="#abb2bf",
        bg="#1e1e1e",
    )
    subtitle_label.pack(pady=(0, 15))

    # Language selection frame
    lang_frame = Frame(main_frame, bg="#1e1e1e")
    lang_frame.pack(fill="x", pady=(0, 15))

    lang_label = Label(
        lang_frame,
        text="Language:",
        font=("Segoe UI", 12),
        fg="#e5c07b",
        bg="#1e1e1e",
    )
    lang_label.pack(side="left", padx=(0, 15))

    language_var = StringVar(root)
    language_var.set("EN")

    lang_menu = OptionMenu(lang_frame, language_var, "EN", "CN", command=change_language)
    lang_menu.config(
        font=("Segoe UI", 11),
        bg="#3c3c3c",
        fg="white",
        activebackground="#61afef",
        activeforeground="white",
        highlightthickness=0,
        width=10,
        relief="flat",
    )
    lang_menu["menu"].config(
        bg="#3c3c3c",
        fg="white",
        activebackground="#61afef",
        activeforeground="white",
        font=("Segoe UI", 11),
    )
    lang_menu.pack(side="left")

    # Separator line
    separator = Frame(main_frame, height=2, bg="#3c3c3c")
    separator.pack(fill="x", pady=(0, 15))

    # Actions label
    actions_label = Label(
        main_frame,
        text="Select an Action",
        font=("Segoe UI", 13),
        fg="#98c379",
        bg="#1e1e1e",
    )
    actions_label.pack(pady=(0, 15))

    # Button configurations
    buttons_config = [
        ("Auto Fight", run_autoFight, "#61afef"),
        ("Auto P Fight", run_autoPFight, "#e5c07b"),
        ("Auto Fight Friends", run_autoFightFriends, "#c678dd"),
        ("Auto P Fight Friends", run_autoPFightFriends, "#c678dd"),
        ("Faction Challenge", run_FactionChallenge, "#98c379"),
    ]

    for text, command, color in buttons_config:
        btn = Button(
            main_frame,
            text=text,
            command=command,
            font=("Segoe UI", 11, "bold"),
            bg=color,
            fg="#1e1e1e",
            activebackground="#ffffff",
            activeforeground="#1e1e1e",
            relief="flat",
            cursor="hand2",
            width=28,
            height=1,
            bd=0,
            pady=10,
        )
        btn.pack(pady=4)

        # Store original color for hover effect
        original_color = color
        hover_color = "#ffffff"
        
        def on_enter(e, b=btn, hc=hover_color):
            b.config(bg=hc)
        
        def on_leave(e, b=btn, oc=original_color):
            b.config(bg=oc)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # Stop button
    stop_btn = Button(
        main_frame,
        text="⏹  Stop Automation",
        command=stop_execution,
        font=("Segoe UI", 11, "bold"),
        bg="#e06c75",
        fg="white",
        activebackground="#be5046",
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        width=28,
        height=1,
        bd=0,
        pady=10,
    )
    stop_btn.pack(pady=(15, 4))

    def on_stop_enter(e):
        stop_btn.config(bg="#be5046")

    def on_stop_leave(e):
        stop_btn.config(bg="#e06c75")

    stop_btn.bind("<Enter>", on_stop_enter)
    stop_btn.bind("<Leave>", on_stop_leave)

    # Footer with avatar
    footer_frame = Frame(main_frame, bg="#1e1e1e")
    footer_frame.pack(side="bottom", pady=(10, 0))

    # Load and create round avatar
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    avatar_path = os.path.join(script_dir, "assets", "avator.jpg")
    if os.path.exists(avatar_path):
        # Open image and resize
        img = Image.open(avatar_path)
        img = img.resize((40, 40), Image.LANCZOS)
        
        # Create circular mask
        mask = Image.new("L", (40, 40), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 40, 40), fill=255)
        
        # Apply mask to create round image
        output = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        avatar_photo = ImageTk.PhotoImage(output)
        avatar_label = Label(footer_frame, image=avatar_photo, bg="#1e1e1e")
        avatar_label.image = avatar_photo  # Keep reference
        avatar_label.pack(side="left", padx=(0, 10))

    # Author text
    author_label = Label(
        footer_frame,
        text="Authored by ylx",
        font=("Segoe UI", 10),
        fg="#5c6370",
        bg="#1e1e1e",
    )
    author_label.pack(side="left")

    # Version
    version_label = Label(
        footer_frame,
        text=" • v1.0",
        font=("Segoe UI", 10),
        fg="#5c6370",
        bg="#1e1e1e",
    )
    version_label.pack(side="left")

    root.mainloop()

if __name__ == "__main__":
    create_gui()