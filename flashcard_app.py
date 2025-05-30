import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import random
import database as db

class FlashcardApp:
    def __init__(self, master):
        self.master = master
        master.title("Language flashcard practice tool")
        master.geometry("1000x900") # Increased window size
        master.config(bg="#F0F4F8") # Light modern background

        self.current_deck = None
        self.flashcards = []
        self.current_card_index = -1
        self.practice_mode = tk.StringVar(value="japanese_to_english")
        self.selected_test_decks = []

        # Define modern fonts and colors
        self.font_large = ("Segoe UI", 24, "bold")
        self.font_medium = ("Segoe UI", 14)
        self.font_small = ("Segoe UI", 10)
        self.font_card_japanese = ("Meiryo UI", 60, "bold") # Japanese specific font
        self.font_card_english = ("Segoe UI", 32)

        self.color_primary = "#4CAF50"  # Green
        self.color_secondary = "#2196F3" # Blue
        self.color_accent = "#FFC107"   # Amber
        self.color_danger = "#F44336"   # Red
        self.color_background = "#F0F4F8"
        self.color_text_dark = "#333333"
        self.color_text_light = "#FFFFFF" # This is already white
        self.color_card_front = "#BBDEFB" # Light blue for card front
        self.color_card_back = "#E0E0E0"  # Grey for card back


        self.create_main_menu()

    def clear_frame(self):
        """Clears all widgets from the current frame."""
        for widget in self.master.winfo_children():
            widget.destroy()

    def create_main_menu(self):
        """Creates the main menu allowing deck selection and creation."""
        self.clear_frame()
        self.master.unbind("<Return>")
        self.master.config(bg=self.color_background)

        tk.Label(self.master, text="Japanese Flashcard Learner", font=self.font_large, bg=self.color_background, fg=self.color_text_dark).pack(pady=30)

        tk.Label(self.master, text="Select a Deck to Play or Edit:", font=self.font_medium, bg=self.color_background, fg=self.color_text_dark).pack(pady=10)
        
        listbox_frame = tk.Frame(self.master, bg=self.color_background)
        listbox_frame.pack(pady=5)
        
        self.deck_listbox = tk.Listbox(listbox_frame, height=8, width=50, font=self.font_medium, bd=2, relief="groove",
                                        selectbackground=self.color_secondary, selectforeground=self.color_text_light)
        self.deck_listbox.pack(side=tk.LEFT, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=self.deck_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.deck_listbox.config(yscrollcommand=scrollbar.set)
        
        self.populate_deck_listbox()

        deck_actions_frame = tk.Frame(self.master, bg=self.color_background)
        deck_actions_frame.pack(pady=15)

        tk.Button(deck_actions_frame, text="Play Deck", command=self.play_selected_deck, font=self.font_medium, bg=self.color_primary, fg=self.color_text_light, padx=15, pady=8).pack(side=tk.LEFT, padx=10)
        tk.Button(deck_actions_frame, text="Edit Deck", command=self.edit_selected_deck, font=self.font_medium, bg=self.color_secondary, fg=self.color_text_light, padx=15, pady=8).pack(side=tk.LEFT, padx=10)
        tk.Button(deck_actions_frame, text="Delete Deck", command=self.delete_selected_deck, font=self.font_medium, bg=self.color_danger, fg=self.color_text_light, padx=15, pady=8).pack(side=tk.LEFT, padx=10)

        tk.Label(self.master, text="-- OR -- Create New Deck:", font=self.font_medium, bg=self.color_background, fg=self.color_text_dark).pack(pady=15)
        
        new_deck_frame = tk.Frame(self.master, bg=self.color_background)
        new_deck_frame.pack(pady=5)
        tk.Label(new_deck_frame, text="Deck Name:", font=self.font_medium, bg=self.color_background, fg=self.color_text_dark).pack(side=tk.LEFT, padx=5)
        self.new_deck_entry = tk.Entry(new_deck_frame, width=30, font=self.font_medium, bd=2, relief="solid")
        self.new_deck_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(new_deck_frame, text="Create Deck", command=self.create_new_deck, font=self.font_medium, bg=self.color_accent, fg=self.color_text_dark, padx=15, pady=8).pack(side=tk.LEFT, padx=5)

        practice_mode_frame = tk.LabelFrame(self.master, text="Practice Mode", padx=20, pady=10, font=self.font_medium, bg=self.color_background, fg=self.color_text_dark, bd=2, relief="groove")
        practice_mode_frame.pack(pady=20, padx=50, fill="x")

        tk.Radiobutton(practice_mode_frame, text="Japanese to English", variable=self.practice_mode, value="japanese_to_english", font=self.font_medium, bg=self.color_background, fg=self.color_text_dark, selectcolor=self.color_background).pack(side=tk.LEFT, padx=20)
        tk.Radiobutton(practice_mode_frame, text="English to Japanese", variable=self.practice_mode, value="english_to_japanese", font=self.font_medium, bg=self.color_background, fg=self.color_text_dark, selectcolor=self.color_background).pack(side=tk.LEFT, padx=20)
        tk.Radiobutton(practice_mode_frame, text="Mixed (Random)", variable=self.practice_mode, value="mixed", font=self.font_medium, bg=self.color_background, fg=self.color_text_dark, selectcolor=self.color_background).pack(side=tk.LEFT, padx=20)

        tk.Button(self.master, text="Start Test Mode (Multiple Decks)", command=self.start_test_mode_selection, font=self.font_medium, bg="#9C27B0", fg=self.color_text_light, padx=20, pady=10).pack(pady=15)


    def populate_deck_listbox(self):
        """Populates the listbox with available decks from the database."""
        self.deck_listbox.delete(0, tk.END)
        decks = db.get_all_decks()
        if not decks:
            self.deck_listbox.insert(tk.END, "No decks found. Create one above!")
        else:
            for deck in decks:
                self.deck_listbox.insert(tk.END, deck)

    def get_selected_deck_name(self):
        """Helper to get the name of the currently selected deck."""
        selected_index = self.deck_listbox.curselection()
        if selected_index:
            return self.deck_listbox.get(selected_index[0])
        return None

    def play_selected_deck(self):
        """Starts a practice session for the selected deck."""
        deck_name = self.get_selected_deck_name()
        if deck_name and deck_name != "No decks found. Create one above!":
            self.current_deck = deck_name
            self.start_practice() 
        else:
            messagebox.showwarning("No Deck Selected", "Please select a deck to play.")

    def edit_selected_deck(self):
        """Enters the editing interface for the selected deck."""
        deck_name = self.get_selected_deck_name()
        if deck_name and deck_name != "No decks found. Create one above!":
            self.current_deck = deck_name
            self.enter_deck_editing()
        else:
            messagebox.showwarning("No Deck Selected", "Please select a deck to edit.")

    def delete_selected_deck(self):
        """Deletes the currently selected deck."""
        deck_to_delete = self.get_selected_deck_name()
        if deck_to_delete and deck_to_delete != "No decks found. Create one above!":
            if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the deck '{deck_to_delete}'? This action cannot be undone and will delete all cards in it."):
                if db.delete_deck(deck_to_delete):
                    messagebox.showinfo("Deck Deleted", f"Deck '{deck_to_delete}' has been deleted.")
                    self.populate_deck_listbox()
                    if self.current_deck == deck_to_delete:
                        self.current_deck = None
                else:
                    messagebox.showerror("Deletion Error", f"Could not delete deck '{deck_to_delete}'.")
        else:
            messagebox.showwarning("No Deck Selected", "Please select a deck to delete.")

    def create_new_deck(self):
        """Creates a new deck based on user input."""
        deck_name = self.new_deck_entry.get().strip()
        if deck_name:
            sanitized_deck_name = ''.join(c for c in deck_name if c.isalnum() or c == '_')
            if not sanitized_deck_name:
                messagebox.showerror("Invalid Deck Name", "Deck name must contain alphanumeric characters (A-Z, a-z, 0-9, or underscore).")
                return

            if sanitized_deck_name in db.get_all_decks():
                messagebox.showerror("Deck Exists", f"A deck named '{sanitized_deck_name}' already exists. Please choose a different name.")
                return

            db.create_table(sanitized_deck_name)
            messagebox.showinfo("Deck Created", f"Deck '{sanitized_deck_name}' created successfully!")
            self.new_deck_entry.delete(0, tk.END)
            self.populate_deck_listbox()
            self.current_deck = sanitized_deck_name
            self.enter_deck_editing() # Automatically go to editing new deck
        else:
            messagebox.showwarning("Input Error", "Please enter a name for the new deck.")

    def enter_deck_editing(self):
        """Displays the interface for adding, deleting, and renaming cards within a deck."""
        self.clear_frame()
        self.master.config(bg=self.color_background)

        tk.Label(self.master, text=f"Editing Deck: {self.current_deck}", font=self.font_large, bg=self.color_background, fg=self.color_text_dark).pack(pady=20)

        add_card_frame = tk.LabelFrame(self.master, text="Add New Card", padx=20, pady=15, font=self.font_medium, bg=self.color_background, fg=self.color_text_dark, bd=2, relief="groove")
        add_card_frame.pack(pady=10, padx=50, fill="x")

        tk.Label(add_card_frame, text="Japanese Word:", font=self.font_medium, bg=self.color_background, fg=self.color_text_dark).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.japanese_entry = tk.Entry(add_card_frame, width=30, font=self.font_medium, bd=2, relief="solid")
        self.japanese_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(add_card_frame, text="English Word:", font=self.font_medium, bg=self.color_background, fg=self.color_text_dark).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.english_entry = tk.Entry(add_card_frame, width=30, font=self.font_medium, bd=2, relief="solid")
        self.english_entry.grid(row=1, column=1, padx=10, pady=10)

        add_card_button = tk.Button(add_card_frame, text="Add Card", command=self.add_card_to_deck, font=self.font_medium, bg=self.color_primary, fg=self.color_text_light, padx=15, pady=8)
        add_card_button.grid(row=2, column=0, columnspan=2, pady=15)

        rename_frame = tk.Frame(self.master, bg=self.color_background)
        rename_frame.pack(pady=10)
        tk.Button(rename_frame, text="Rename This Deck", command=self.rename_current_deck, font=self.font_medium, bg=self.color_secondary, fg=self.color_text_light, padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        
        manage_cards_frame = tk.LabelFrame(self.master, text="Manage Existing Cards", padx=20, pady=15, font=self.font_medium, bg=self.color_background, fg=self.color_text_dark, bd=2, relief="groove")
        manage_cards_frame.pack(pady=10, padx=50, fill="both", expand=True)

        self.cards_listbox = tk.Listbox(manage_cards_frame, height=8, width=60, font=self.font_medium, bd=2, relief="groove",
                                        selectbackground=self.color_danger, selectforeground=self.color_text_light)
        self.cards_listbox.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
        
        cards_scrollbar = tk.Scrollbar(manage_cards_frame, orient="vertical", command=self.cards_listbox.yview)
        cards_scrollbar.pack(side=tk.RIGHT, fill="y")
        self.cards_listbox.config(yscrollcommand=cards_scrollbar.set)

        self.populate_cards_listbox()

        delete_card_button = tk.Button(manage_cards_frame, text="Delete Selected Card", command=self.delete_selected_card, font=self.font_medium, bg=self.color_danger, fg=self.color_text_light, padx=15, pady=8)
        delete_card_button.pack(pady=10)

        tk.Button(self.master, text="Back to Main Menu", command=self.create_main_menu, font=self.font_medium, bg="#607D8B", fg=self.color_text_light, padx=20, pady=10).pack(pady=20)

    def populate_cards_listbox(self):
        """Populates the cards_listbox with cards from the current deck."""
        self.cards_listbox.delete(0, tk.END)
        self.flashcards_for_editing = db.get_cards_from_deck(self.current_deck) 
        if not self.flashcards_for_editing:
            self.cards_listbox.insert(tk.END, "No cards in this deck yet.")
        else:
            for card_id, japanese, english in self.flashcards_for_editing:
                self.cards_listbox.insert(tk.END, f"{japanese} - {english}")

    def delete_selected_card(self):
        """Deletes the selected card from the current deck."""
        selected_index = self.cards_listbox.curselection()
        if selected_index:
            card_index_in_list = selected_index[0]
            if not self.flashcards_for_editing:
                messagebox.showwarning("No Card Selected", "There are no cards to delete in this deck.")
                return

            card_id_to_delete = self.flashcards_for_editing[card_index_in_list][0]
            japanese_word_display = self.flashcards_for_editing[card_index_in_list][1]
            english_word_display = self.flashcards_for_editing[card_index_in_list][2]

            if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete this card:\n'{japanese_word_display}' - '{english_word_display}'?"):
                if db.delete_card_by_id(self.current_deck, card_id_to_delete):
                    messagebox.showinfo("Card Deleted", "Card deleted successfully!")
                    self.populate_cards_listbox()
                else:
                    messagebox.showerror("Error", "Failed to delete card.")
        else:
            messagebox.showwarning("No Card Selected", "Please select a card to delete.")

    def rename_current_deck(self):
        """Renames the current deck."""
        if not self.current_deck:
            messagebox.showwarning("Error", "No deck selected for renaming.")
            return

        old_deck_name = self.current_deck
        new_deck_name = simpledialog.askstring("Rename Deck", f"Enter new name for '{old_deck_name}':",
                                             parent=self.master)
        if new_deck_name:
            new_deck_name = new_deck_name.strip()
            sanitized_new_deck_name = ''.join(c for c in new_deck_name if c.isalnum() or c == '_')
            if not sanitized_new_deck_name:
                messagebox.showerror("Invalid New Name", "New deck name must contain alphanumeric characters (A-Z, a-z, 0-9, or underscore).")
                return
            
            if sanitized_new_deck_name in db.get_all_decks():
                messagebox.showerror("Deck Exists", f"A deck named '{sanitized_new_deck_name}' already exists. Please choose a different name.")
                return
            
            if sanitized_new_deck_name == old_deck_name:
                messagebox.showinfo("No Change", "The new name is the same as the old name.")
                return

            if db.rename_deck(old_deck_name, sanitized_new_deck_name):
                messagebox.showinfo("Deck Renamed", f"Deck '{old_deck_name}' renamed to '{sanitized_new_deck_name}'.")
                self.current_deck = sanitized_new_deck_name
                self.create_main_menu()
            else:
                messagebox.showerror("Rename Error", f"Could not rename deck '{old_deck_name}'.")
        
    def add_card_to_deck(self):
        """Adds a new flashcard to the current deck."""
        japanese_word = self.japanese_entry.get().strip()
        english_word = self.english_entry.get().strip()

        if japanese_word and english_word and self.current_deck:
            if db.add_card(self.current_deck, japanese_word, english_word):
                messagebox.showinfo("Card Added", "Flashcard added successfully!")
                self.japanese_entry.delete(0, tk.END)
                self.english_entry.delete(0, tk.END)
                self.populate_cards_listbox()
            else:
                messagebox.showerror("Error", "Failed to add flashcard.")
        else:
            messagebox.showwarning("Input Error", "Please fill in both Japanese and English words.")

    def start_practice(self):
        """Initializes and displays the practice interface for a single deck."""
        self._load_and_prepare_cards([self.current_deck])
        if not self.flashcards:
            messagebox.showwarning("No Cards", "This deck has no cards yet. Please add some cards first.")
            self.create_main_menu()
            return
        self._begin_practice_session()


    def start_test_mode_selection(self):
        """Displays a window to select multiple decks for test mode."""
        self.clear_frame()
        self.master.config(bg=self.color_background)

        tk.Label(self.master, text="Select Decks for Test Mode", font=self.font_large, bg=self.color_background, fg=self.color_text_dark).pack(pady=20)

        all_decks = db.get_all_decks()
        if not all_decks:
            tk.Label(self.master, text="No decks available. Please create some first.", font=self.font_medium, bg=self.color_background, fg=self.color_text_dark).pack(pady=10)
            tk.Button(self.master, text="Back to Main Menu", command=self.create_main_menu, font=self.font_medium, bg="#607D8B", fg=self.color_text_light, padx=20, pady=10).pack(pady=20)
            return

        checkbox_container = tk.Frame(self.master, bg=self.color_background)
        checkbox_container.pack(pady=10, padx=50, fill="both", expand=True)

        canvas = tk.Canvas(checkbox_container, bg=self.color_background, bd=0, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill="both", expand=True)

        scrollbar = tk.Scrollbar(checkbox_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion = canvas.bbox("all")))

        self.deck_checkbox_frame = tk.Frame(canvas, bg=self.color_background)
        canvas.create_window((0, 0), window=self.deck_checkbox_frame, anchor="nw")

        self.deck_checkboxes = {}
        self.selected_test_decks_vars = []

        for deck_name in all_decks:
            var = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(self.deck_checkbox_frame, text=deck_name, variable=var, font=self.font_medium, bg=self.color_background, fg=self.color_text_dark, selectcolor=self.color_background)
            cb.pack(anchor="w", padx=10, pady=5)
            self.deck_checkboxes[deck_name] = var
            self.selected_test_decks_vars.append((deck_name, var))

        tk.Button(self.master, text="Start Test", command=self.start_test_practice, font=self.font_medium, bg=self.color_primary, fg=self.color_text_light, padx=20, pady=10).pack(pady=15)
        tk.Button(self.master, text="Back to Main Menu", command=self.create_main_menu, font=self.font_medium, bg="#607D8B", fg=self.color_text_light, padx=20, pady=10).pack(pady=10)


    def start_test_practice(self):
        """Initiates the practice session with selected multiple decks."""
        self.selected_test_decks = [deck_name for deck_name, var in self.selected_test_decks_vars if var.get()]

        if not self.selected_test_decks:
            messagebox.showwarning("No Decks Selected", "Please select at least one deck to start the test.")
            return

        self._load_and_prepare_cards(self.selected_test_decks)
        
        if not self.flashcards:
            messagebox.showwarning("No Cards", "The selected decks contain no cards. Please add some cards to them first.")
            self.create_main_menu()
            return

        self.current_deck = ", ".join(self.selected_test_decks)
        self._begin_practice_session()

    def _load_and_prepare_cards(self, deck_names):
        """Loads cards from specified decks and prepares them for practice based on mode."""
        all_cards_raw = []
        for deck_name in deck_names:
            all_cards_raw.extend(db.get_cards_from_deck(deck_name))

        self.flashcards = []
        mode = self.practice_mode.get()

        for _id, japanese, english in all_cards_raw:
            if mode == "japanese_to_english":
                self.flashcards.append({"question": japanese, "answer": english, "type": "jp_to_en"})
            elif mode == "english_to_japanese":
                self.flashcards.append({"question": english, "answer": japanese, "type": "en_to_jp"})
            elif mode == "mixed":
                self.flashcards.append({"question": japanese, "answer": english, "type": "jp_to_en"})
                self.flashcards.append({"question": english, "answer": japanese, "type": "en_to_jp"})
        
        random.shuffle(self.flashcards)
        self.current_card_index = -1
        self.correct_count = 0
        self.total_tested = 0


    def _begin_practice_session(self):
        """Common method to start the practice session after cards are loaded."""
        self.show_next_card()


    def show_next_card(self):
        """Displays the next flashcard for practice."""
        self.current_card_index += 1
        if self.current_card_index >= len(self.flashcards):
            self.end_practice_session()
            return

        self.clear_frame()
        self.master.config(bg=self.color_background)
        self.master.bind("<Return>", lambda event: self.check_answer())

        card_data = self.flashcards[self.current_card_index]
        question_text = card_data["question"]
        card_type = card_data["type"]

        display_deck_name = self.current_deck
        if len(self.selected_test_decks) > 0 and self.current_deck == ", ".join(self.selected_test_decks):
            display_deck_name = "Multi-Deck Test"

        tk.Label(self.master, text=f"Practicing: {display_deck_name}", font=self.font_medium, bg=self.color_background, fg=self.color_text_dark).pack(pady=10)
        tk.Label(self.master, text=f"Card {self.current_card_index + 1} of {len(self.flashcards)}", font=self.font_small, bg=self.color_background, fg=self.color_text_dark).pack(pady=5)

        card_frame = tk.Frame(self.master, bg=self.color_card_front, bd=5, relief="raised")
        card_frame.pack(pady=30, padx=50, fill="both", expand=True)

        if card_type == "jp_to_en":
            tk.Label(card_frame, text="Translate Japanese to English:", font=self.font_medium, bg=self.color_card_front, fg=self.color_text_dark).pack(pady=10)
            self.japanese_display_label = tk.Label(card_frame, text=question_text, font=self.font_card_japanese, bg=self.color_card_front, fg="blue")
        else:
            tk.Label(card_frame, text="Translate English to Japanese:", font=self.font_medium, bg=self.color_card_front, fg=self.color_text_dark).pack(pady=10)
            self.japanese_display_label = tk.Label(card_frame, text=question_text, font=self.font_card_english, bg=self.color_card_front, fg="blue")
        
        self.japanese_display_label.pack(pady=30)

        tk.Label(self.master, text="Your Answer:", font=self.font_medium, bg=self.color_background, fg=self.color_text_dark).pack(pady=10)
        self.user_answer_entry = tk.Entry(self.master, width=50, font=self.font_medium, bd=2, relief="solid")
        self.user_answer_entry.pack(pady=5)

        self.feedback_label = tk.Label(self.master, text="", font=self.font_medium, bg=self.color_background)
        self.feedback_label.pack(pady=10)

        submit_frame = tk.Frame(self.master, bg=self.color_background)
        submit_frame.pack(pady=10)

        self.submit_button = tk.Button(submit_frame, text="Submit Answer", command=self.check_answer, font=self.font_medium, bg=self.color_accent, fg=self.color_text_dark, padx=15, pady=8)
        self.submit_button.pack(side=tk.LEFT, padx=10)

        # Explicitly setting foreground (fg) to white for the "Next Card" button
        self.next_card_button = tk.Button(submit_frame, text="Next Card", command=self.show_next_card, font=self.font_medium, bg=self.color_primary, fg=self.color_text_light, state=tk.DISABLED, padx=15, pady=8)
        self.next_card_button.pack(side=tk.LEFT, padx=10)

        self.show_all_answers_button = tk.Button(submit_frame, text="Show All Answers", command=self.open_all_cards_window, font=self.font_medium, bg="#9C27B0", fg=self.color_text_light, padx=15, pady=8)
        self.show_all_answers_button.pack(side=tk.LEFT, padx=10)

        self.back_to_main_menu_button = tk.Button(self.master, text="Back to Main Menu", command=self.create_main_menu, font=self.font_medium, bg="#607D8B", fg=self.color_text_light, padx=20, pady=10)
        self.back_to_main_menu_button.pack(pady=20)
        self.user_answer_entry.focus_set()

    def check_answer(self):
        """Checks the user's answer against the correct translation."""
        self.total_tested += 1
        user_answer = self.user_answer_entry.get().strip().lower()
        correct_answer = self.flashcards[self.current_card_index]["answer"].strip().lower()

        if user_answer == correct_answer:
            self.feedback_label.config(text="Correct!", fg="green")
            self.correct_count += 1
        else:
            self.feedback_label.config(text=f"Incorrect. Correct answer was: '{self.flashcards[self.current_card_index]['answer']}'", fg="red")

        self.user_answer_entry.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.DISABLED)
        self.next_card_button.config(state=tk.NORMAL)
        self.master.bind("<Return>", lambda event: self.show_next_card())

    def end_practice_session(self):
        """Displays results at the end of a practice session."""
        self.clear_frame()
        self.master.config(bg=self.color_background)

        tk.Label(self.master, text="Practice Session Complete!", font=self.font_large, bg=self.color_background, fg=self.color_text_dark).pack(pady=40)
        tk.Label(self.master, text=f"You answered {self.correct_count} out of {self.total_tested} cards correctly.", font=self.font_medium, bg=self.color_background, fg=self.color_text_dark).pack(pady=15)
        
        button_frame = tk.Frame(self.master, bg=self.color_background)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Back to Main Menu", command=self.create_main_menu, font=self.font_medium, bg="#607D8B", fg=self.color_text_light, padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        
        if len(self.selected_test_decks) > 0 and self.current_deck == ", ".join(self.selected_test_decks):
            tk.Button(button_frame, text="Start New Test Practice", command=self.start_test_practice, font=self.font_medium, bg=self.color_primary, fg=self.color_text_light, padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        else:
            tk.Button(button_frame, text="Start New Practice (Current Deck)", command=self.start_practice, font=self.font_medium, bg=self.color_primary, fg=self.color_text_light, padx=20, pady=10).pack(side=tk.LEFT, padx=10)

        self.master.unbind("<Return>")

    def open_all_cards_window(self):
        """Opens a new Toplevel window listing all cards in the current practice session's decks."""
        decks_to_display = []
        if self.current_deck and len(self.current_deck.split(', ')) > 1:
            decks_to_display = self.selected_test_decks if self.selected_test_decks else []
        elif self.current_deck:
            decks_to_display = [self.current_deck]
        
        if not decks_to_display:
            messagebox.showwarning("Error", "No deck(s) currently selected for practice.")
            return

        all_cards_window = tk.Toplevel(self.master)
        all_cards_window.title(f"All Answers: {', '.join(decks_to_display)}")
        all_cards_window.geometry("500x800")
        all_cards_window.config(bg=self.color_background)

        tk.Label(all_cards_window, text=f"Cards from: {', '.join(decks_to_display)}", font=self.font_medium, bg=self.color_background, fg=self.color_text_dark).pack(pady=15)

        cards_text_area = scrolledtext.ScrolledText(all_cards_window, width=55, height=18, font=self.font_medium, bd=2, relief="groove",
                                                    bg=self.color_card_back, fg=self.color_text_dark, padx=10, pady=10)
        cards_text_area.pack(pady=10, padx=20, fill="both", expand=True)

        combined_cards_data = []
        for deck_name in decks_to_display:
            combined_cards_data.extend(db.get_cards_from_deck(deck_name))
        
        if not combined_cards_data:
            cards_text_area.insert(tk.END, "No cards in the selected decks yet.")
        else:
            combined_cards_data.sort(key=lambda x: x[1])
            for i, (_id, japanese, english) in enumerate(combined_cards_data):
                cards_text_area.insert(tk.END, f"{i+1}. {japanese} - {english}\n")
        
        cards_text_area.config(state=tk.DISABLED)

        close_button = tk.Button(all_cards_window, text="Close", command=all_cards_window.destroy, font=self.font_medium, bg="#607D8B", fg=self.color_text_light, padx=15, pady=8)
        close_button.pack(pady=15)

        all_cards_window.grab_set()
        self.master.wait_window(all_cards_window)