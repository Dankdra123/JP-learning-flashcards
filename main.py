# main.py
import tkinter as tk
from flashcard_app import FlashcardApp

if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()