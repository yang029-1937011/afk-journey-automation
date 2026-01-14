from tkinter import Tk, Button, Frame, messagebox
import automation.game_automation as game_automation

class App:
    def __init__(self, master):
        self.master = master
        master.title("AFK Journey Automation")

        self.frame = Frame(master)
        self.frame.pack()

        self.auto_click_button = Button(self.frame, text="Auto Click", command=self.auto_click)
        self.auto_click_button.pack(side="top", padx=10, pady=10)

        self.auto_fight_button = Button(self.frame, text="Auto Fight", command=self.auto_fight)
        self.auto_fight_button.pack(side="top", padx=10, pady=10)

        self.auto_fight_friends1_button = Button(self.frame, text="Auto Fight Friends 1", command=self.auto_fight_friends1)
        self.auto_fight_friends1_button.pack(side="top", padx=10, pady=10)

        self.dura_trail_challenge_button = Button(self.frame, text="Dura Trail Challenge", command=self.dura_trail_challenge)
        self.dura_trail_challenge_button.pack(side="top", padx=10, pady=10)

        self.faction_challenge_button = Button(self.frame, text="Faction Challenge", command=self.faction_challenge)
        self.faction_challenge_button.pack(side="top", padx=10, pady=10)

    def auto_click(self):
        try:
            game_automation.autoClick()
            messagebox.showinfo("Success", "Auto Click initiated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def auto_fight(self):
        try:
            game_automation.autoFight()
            messagebox.showinfo("Success", "Auto Fight initiated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def auto_fight_friends1(self):
        try:
            game_automation.autoFightFriends1()
            messagebox.showinfo("Success", "Auto Fight Friends 1 initiated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def dura_trail_challenge(self):
        try:
            game_automation.DuraTrailChallenge()
            messagebox.showinfo("Success", "Dura Trail Challenge initiated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def faction_challenge(self):
        try:
            game_automation.FactionChallenge()
            messagebox.showinfo("Success", "Faction Challenge initiated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()