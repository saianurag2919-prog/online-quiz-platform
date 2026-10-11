"""
Online Quiz Platform
====================
A desktop quiz application built with Python and Tkinter (standard library only).

Features
--------
* Three built-in quizzes: Python Basics, General Knowledge, Computer Basics
* Customisable quizzes: choose how many questions, shuffle on/off, and add your own
  questions (they are saved as "My Custom Quiz")
* Answer checking with instant feedback and a short explanation
* Score calculation: score, percentage, grade message and time taken
* Review screen showing every question with your answer and the correct answer
* High-score table saved between sessions

Run:
    python quiz_platform.py

Requires Python 3.8+ with Tkinter (included in the standard Python installer).
Data files (custom_quiz.json, highscores.json) are created next to this file.
"""

import json
import random
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

BASE_DIR = Path(__file__).resolve().parent
CUSTOM_FILE = BASE_DIR / "custom_quiz.json"
SCORES_FILE = BASE_DIR / "highscores.json"
CUSTOM_NAME = "My Custom Quiz"
LETTERS = "ABCD"

# Colour palette
BG = "#EEF3F0"
SURFACE = "#FFFFFF"
SURFACE_ALT = "#F3F7F4"
TEXT = "#14241C"
MUTED = "#5E6F66"
LINE = "#D4DDD7"
PRIMARY = "#2E7D5B"
PRIMARY_DARK = "#235F45"
SELECTED_BG = "#E0F1E8"
CORRECT_BG = "#D5EEDD"
WRONG_BG = "#FBE1DE"
DANGER = "#B3261E"
FONT = "Helvetica"


# --------------------------------------------------------------------------
# Question bank
# --------------------------------------------------------------------------
def _q(question, options, answer, explain=""):
    return {"q": question, "options": options, "answer": answer, "explain": explain}


BUILT_IN = {
    "Python Basics": [
        _q("Which keyword is used to define a function in Python?", ["func", "def", "function", "lambda"], 1,
           "Functions are defined with the def keyword."),
        _q("What is the output of len('Pinnacle')?", ["7", "8", "9", "10"], 1,
           "The word Pinnacle has 8 characters."),
        _q("Which of these data types is immutable?", ["list", "dict", "set", "tuple"], 3,
           "A tuple cannot be changed after it is created."),
        _q("Which symbol starts a single-line comment in Python?", ["//", "#", "--", "/*"], 1,
           "Python comments begin with the # symbol."),
        _q("What does print(2 ** 3) display?", ["6", "8", "9", "23"], 1,
           "The ** operator means power, so 2 ** 3 is 8."),
        _q("Which list method adds an item to the end of a list?", ["add()", "insert_end()", "append()", "push()"], 2,
           "list.append(x) adds x at the end."),
        _q("What is the result of 10 // 3?", ["3.33", "3", "4", "1"], 1,
           "// is floor division, so 10 // 3 gives 3."),
        _q("Which block is used to handle errors in Python?", ["try / except", "if / else", "for / while", "def / return"], 0,
           "Code that may fail goes in try, and the error is handled in except."),
        _q("Which built-in function reads text typed by the user?", ["scan()", "read()", "input()", "get()"], 2,
           "input() waits for the user to type and returns a string."),
        _q("What is the file extension of a Python script?", [".pt", ".py", ".python", ".pyt"], 1,
           "Python source files end with .py."),
    ],
    "General Knowledge": [
        _q("What is the capital city of India?", ["Mumbai", "Chennai", "New Delhi", "Kolkata"], 2,
           "New Delhi is the capital of India."),
        _q("Which animal is the national animal of India?", ["Lion", "Tiger", "Elephant", "Peacock"], 1,
           "The Bengal tiger is India's national animal."),
        _q("Which is the largest planet in our solar system?", ["Earth", "Saturn", "Jupiter", "Neptune"], 2,
           "Jupiter is the biggest planet in the solar system."),
        _q("Who wrote the Indian national anthem?", ["Rabindranath Tagore", "Bankim Chandra Chatterjee",
                                                       "Sarojini Naidu", "Subramania Bharati"], 0,
           "Jana Gana Mana was written by Rabindranath Tagore."),
        _q("What is the currency of Japan?", ["Won", "Yuan", "Yen", "Ringgit"], 2,
           "Japan uses the yen."),
        _q("How many continents are there on Earth?", ["5", "6", "7", "8"], 2,
           "The seven continents are Asia, Africa, North America, South America, Antarctica, Europe and Australia."),
        _q("Which is the largest ocean on Earth?", ["Atlantic", "Indian", "Arctic", "Pacific"], 3,
           "The Pacific Ocean is the largest and deepest."),
        _q("In which city is the Taj Mahal located?", ["Delhi", "Agra", "Jaipur", "Lucknow"], 1,
           "The Taj Mahal is in Agra, Uttar Pradesh."),
        _q("What is the chemical formula of water?", ["CO2", "O2", "H2O", "NaCl"], 2,
           "Water is made of two hydrogen atoms and one oxygen atom."),
        _q("On which date is Gandhi Jayanti celebrated?", ["15 August", "26 January", "2 October", "14 November"], 2,
           "Gandhi Jayanti falls on 2 October."),
    ],
    "Computer Basics": [
        _q("What does CPU stand for?", ["Central Processing Unit", "Computer Personal Unit",
                                          "Central Program Utility", "Core Processing Unit"], 0,
           "The CPU is the Central Processing Unit, the brain of the computer."),
        _q("How many bits are there in one byte?", ["4", "8", "16", "32"], 1,
           "One byte equals 8 bits."),
        _q("What does HTML stand for?", ["HyperText Markup Language", "High Text Machine Language",
                                          "HyperTool Multi Language", "Home Text Markup Level"], 0,
           "HTML is HyperText Markup Language, used to structure web pages."),
        _q("Which of these is an output device?", ["Keyboard", "Mouse", "Scanner", "Monitor"], 3,
           "A monitor displays output, while the others are input devices."),
        _q("Which number system do computers use internally?", ["Decimal", "Binary", "Octal", "Roman"], 1,
           "Computers work with binary: 0s and 1s."),
        _q("RAM is what type of memory?", ["Volatile", "Permanent", "Read-only", "Optical"], 0,
           "RAM loses its data when the power is switched off."),
        _q("Which of these is an operating system?", ["Chrome", "Linux", "Python", "Excel"], 1,
           "Linux is an operating system."),
        _q("Who invented the World Wide Web?", ["Bill Gates", "Steve Jobs", "Tim Berners-Lee", "Linus Torvalds"], 2,
           "Tim Berners-Lee invented the World Wide Web in 1989."),
        _q("Which of these is a web browser?", ["Windows", "Firefox", "Photoshop", "Notepad"], 1,
           "Firefox is a web browser."),
        _q("Who created the Python programming language?", ["Dennis Ritchie", "James Gosling",
                                                             "Guido van Rossum", "Bjarne Stroustrup"], 2,
           "Guido van Rossum created Python."),
    ],
}


def _read_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, type(default)) else default
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def _write_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except OSError as exc:
        messagebox.showerror("Save failed", f"Could not save data:\n{exc}")
        return False


def _valid_question(q):
    return (isinstance(q, dict) and isinstance(q.get("q"), str) and isinstance(q.get("options"), list)
            and len(q["options"]) == 4 and isinstance(q.get("answer"), int) and 0 <= q["answer"] < 4)


class QuestionBank:
    """Built-in quizzes plus the user's custom quiz."""

    def __init__(self, custom_path=CUSTOM_FILE):
        self.custom_path = Path(custom_path)
        self.custom = [q for q in _read_json(self.custom_path, []) if _valid_question(q)]

    def names(self):
        names = list(BUILT_IN)
        if self.custom:
            names.append(CUSTOM_NAME)
        return names

    def questions(self, name):
        return self.custom if name == CUSTOM_NAME else BUILT_IN.get(name, [])

    def add_custom(self, question, options, answer, explain=""):
        self.custom.append(_q(question, options, answer, explain))
        return _write_json(self.custom_path, self.custom)

    def clear_custom(self):
        self.custom = []
        return _write_json(self.custom_path, self.custom)


# --------------------------------------------------------------------------
# Quiz engine: asks questions, checks answers, calculates the score
# --------------------------------------------------------------------------
class QuizSession:
    def __init__(self, name, questions, count=None, shuffle=True, rng=None):
        rng = rng or random.Random()
        pool = [dict(q) for q in questions]
        if shuffle:
            rng.shuffle(pool)
        if count:
            pool = pool[:count]
        self.name = name
        self.questions = []
        for q in pool:
            order = list(range(len(q["options"])))
            if shuffle:
                rng.shuffle(order)
            self.questions.append({
                "q": q["q"],
                "options": [q["options"][i] for i in order],
                "answer": order.index(q["answer"]),
                "explain": q.get("explain", ""),
            })
        self.index = 0
        self.score = 0
        self.answers = []  # one (chosen_index, was_correct) per answered question
        self.started = time.time()
        self.finished_at = None

    @property
    def total(self):
        return len(self.questions)

    @property
    def current(self):
        return self.questions[self.index]

    @property
    def finished(self):
        return self.index >= self.total

    def check(self, choice):
        """Checks the chosen option for the current question and updates the score."""
        correct = choice == self.current["answer"]
        if correct:
            self.score += 1
        self.answers.append((choice, correct))
        return correct

    def advance(self):
        self.index += 1
        if self.finished:
            self.finished_at = time.time()

    @property
    def percent(self):
        return round(100 * self.score / self.total) if self.total else 0

    @property
    def elapsed(self):
        return int((self.finished_at or time.time()) - self.started)


def grade_message(percent):
    if percent == 100:
        return "Perfect score! Outstanding work."
    if percent >= 80:
        return "Excellent! You know this topic very well."
    if percent >= 60:
        return "Good job! A little more practice and you will ace it."
    if percent >= 40:
        return "Not bad. Review the answers below and try again."
    return "Keep practising. You will improve with every attempt."


def format_time(seconds):
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


class ScoreBoard:
    def __init__(self, path=SCORES_FILE):
        self.path = Path(path)
        self.entries = _read_json(self.path, [])

    def add(self, name, quiz, score, total, seconds):
        self.entries.append({
            "name": name, "quiz": quiz, "score": score, "total": total,
            "percent": round(100 * score / total) if total else 0,
            "seconds": seconds, "date": datetime.now().strftime("%d %b %Y"),
        })
        return _write_json(self.path, self.entries)

    def top(self, limit=10):
        ranked = sorted(self.entries, key=lambda e: (-e.get("percent", 0), e.get("seconds", 0)))
        return ranked[:limit]

    def clear(self):
        self.entries = []
        return _write_json(self.path, self.entries)


# --------------------------------------------------------------------------
# User interface
# --------------------------------------------------------------------------
class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Online Quiz Platform")
        self.geometry("920x700")
        self.minsize(820, 640)
        self.configure(bg=BG)

        self.bank = QuestionBank()
        self.board = ScoreBoard()
        self.session = None
        self.settings = None
        self.mode = "menu"
        self.selected = None
        self.locked = False
        self.score_saved = False
        self.last_name = tk.StringVar(value="")

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Quiz.Horizontal.TProgressbar", troughcolor=LINE, background=PRIMARY, bordercolor=LINE,
                        lightcolor=PRIMARY, darkcolor=PRIMARY)
        style.configure("Treeview", rowheight=28, font=(FONT, 10), background=SURFACE,
                        fieldbackground=SURFACE, foreground=TEXT)
        style.configure("Treeview.Heading", font=(FONT, 10, "bold"), background=SURFACE_ALT, foreground=MUTED)
        style.map("Treeview", background=[("selected", SELECTED_BG)], foreground=[("selected", TEXT)])

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)
        self.bind("<Key>", self._on_key)
        self.show_menu()

    # ----- helpers --------------------------------------------------------
    def clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def button(self, parent, text, command, kind="secondary", width=None):
        colours = {
            "primary": (PRIMARY, "white", PRIMARY),
            "secondary": (SURFACE, TEXT, LINE),
            "danger": (SURFACE, DANGER, DANGER),
        }[kind]
        label = tk.Label(parent, text=text, bg=colours[0], fg=colours[1], font=(FONT, 11, "bold"), padx=16, pady=9,
                         highlightthickness=1, highlightbackground=colours[2], cursor="hand2", width=width)
        label.bind("<Button-1>", lambda e: command())
        return label

    def heading(self, parent, text, sub=None):
        tk.Label(parent, text=text, bg=parent["bg"], fg=TEXT, font=(FONT, 22, "bold")).pack(anchor="w")
        if sub:
            tk.Label(parent, text=sub, bg=parent["bg"], fg=MUTED, font=(FONT, 11)).pack(anchor="w", pady=(2, 0))

    # ----- menu -----------------------------------------------------------
    def show_menu(self):
        self.mode = "menu"
        self.clear()
        outer = tk.Frame(self.container, bg=BG)
        outer.pack(fill="both", expand=True, padx=40, pady=30)
        self.heading(outer, "Online Quiz Platform", "Pick a quiz, set it up the way you like, and test yourself.")

        card = tk.Frame(outer, bg=SURFACE, highlightthickness=1, highlightbackground=LINE)
        card.pack(fill="x", pady=(20, 0))
        inner = tk.Frame(card, bg=SURFACE)
        inner.pack(fill="x", padx=24, pady=22)
        inner.columnconfigure(1, weight=1)

        def field_label(text, row):
            tk.Label(inner, text=text, bg=SURFACE, fg=MUTED, font=(FONT, 10, "bold")).grid(
                row=row, column=0, sticky="w", pady=8, padx=(0, 16))

        names = self.bank.names()
        self.var_quiz = tk.StringVar(value=(self.settings or {}).get("name", names[0]))
        if self.var_quiz.get() not in names:
            self.var_quiz.set(names[0])
        field_label("Quiz", 0)
        self.quiz_box = ttk.Combobox(inner, textvariable=self.var_quiz, values=names, state="readonly", font=(FONT, 11))
        self.quiz_box.grid(row=0, column=1, sticky="ew", pady=8)
        self.quiz_box.bind("<<ComboboxSelected>>", lambda e: self._sync_count())

        field_label("Number of questions", 1)
        count_row = tk.Frame(inner, bg=SURFACE)
        count_row.grid(row=1, column=1, sticky="w", pady=8)
        self.var_count = tk.StringVar(value="10")
        self.count_spin = tk.Spinbox(count_row, from_=1, to=10, width=5, textvariable=self.var_count,
                                     justify="center", font=(FONT, 11))
        self.count_spin.pack(side="left")
        self.count_info = tk.Label(count_row, text="", bg=SURFACE, fg=MUTED, font=(FONT, 10))
        self.count_info.pack(side="left", padx=10)

        self.var_shuffle = tk.BooleanVar(value=True)
        tk.Checkbutton(inner, text="Shuffle questions and answer options", variable=self.var_shuffle, bg=SURFACE,
                       activebackground=SURFACE, fg=TEXT, selectcolor=SURFACE, font=(FONT, 11)).grid(
            row=2, column=1, sticky="w", pady=8)

        self.menu_error = tk.Label(inner, text="", bg=SURFACE, fg=DANGER, font=(FONT, 10))
        self.menu_error.grid(row=3, column=0, columnspan=2, sticky="w")
        self.button(inner, "Start quiz", self.start_quiz, "primary").grid(row=4, column=0, columnspan=2,
                                                                         sticky="ew", pady=(8, 0))
        self._sync_count()

        row = tk.Frame(outer, bg=BG)
        row.pack(fill="x", pady=(16, 0))
        self.button(row, "Add your own question", self.show_add_question).pack(side="left")
        self.button(row, "High scores", self.show_scores).pack(side="left", padx=10)

    def _sync_count(self):
        total = len(self.bank.questions(self.var_quiz.get()))
        self.count_spin.config(to=max(total, 1))
        try:
            value = int(self.var_count.get())
        except ValueError:
            value = total
        self.var_count.set(str(min(max(value, 1), max(total, 1))))
        self.count_info.config(text=f"(1 to {total} available)")

    def start_quiz(self):
        name = self.var_quiz.get()
        pool = self.bank.questions(name)
        try:
            count = int(self.var_count.get())
        except ValueError:
            self.menu_error.config(text="Enter the number of questions as a whole number.")
            return
        if not pool:
            self.menu_error.config(text="This quiz has no questions yet.")
            return
        if count < 1 or count > len(pool):
            self.menu_error.config(text=f"Choose between 1 and {len(pool)} questions.")
            return
        self.settings = {"name": name, "count": count, "shuffle": self.var_shuffle.get()}
        self.begin_session()

    def begin_session(self):
        s = self.settings
        self.session = QuizSession(s["name"], self.bank.questions(s["name"]), s["count"], s["shuffle"])
        self.score_saved = False
        self.show_question()

    # ----- question screen ------------------------------------------------
    def show_question(self):
        self.mode = "quiz"
        self.clear()
        s = self.session
        q = s.current
        self.selected = None
        self.locked = False

        outer = tk.Frame(self.container, bg=BG)
        outer.pack(fill="both", expand=True, padx=40, pady=24)

        top = tk.Frame(outer, bg=BG)
        top.pack(fill="x")
        tk.Label(top, text=s.name, bg=BG, fg=PRIMARY_DARK, font=(FONT, 12, "bold")).pack(side="left")
        self.score_label = tk.Label(top, text=f"Score: {s.score}", bg=BG, fg=TEXT, font=(FONT, 12, "bold"))
        self.score_label.pack(side="right")
        tk.Label(outer, text=f"Question {s.index + 1} of {s.total}", bg=BG, fg=MUTED, font=(FONT, 10)).pack(
            anchor="w", pady=(10, 4))
        ttk.Progressbar(outer, style="Quiz.Horizontal.TProgressbar", maximum=s.total, value=s.index).pack(fill="x")

        tk.Label(outer, text=q["q"], bg=BG, fg=TEXT, font=(FONT, 17, "bold"), wraplength=800, justify="left",
                 anchor="w").pack(fill="x", pady=(22, 14))

        self.option_cards = []
        for i, text in enumerate(q["options"]):
            card = tk.Frame(outer, bg=SURFACE, highlightthickness=2, highlightbackground=LINE, cursor="hand2")
            card.pack(fill="x", pady=5)
            badge = tk.Label(card, text=LETTERS[i], bg=SURFACE_ALT, fg=PRIMARY_DARK, font=(FONT, 12, "bold"),
                             width=3, pady=8)
            badge.pack(side="left", padx=(8, 12), pady=8)
            label = tk.Label(card, text=text, bg=SURFACE, fg=TEXT, font=(FONT, 13), anchor="w", justify="left",
                             wraplength=700)
            label.pack(side="left", fill="x", expand=True, pady=8)
            for widget in (card, badge, label):
                widget.bind("<Button-1>", lambda e, i=i: self.choose(i))
            self.option_cards.append((card, badge, label))

        self.feedback = tk.Label(outer, text="", bg=BG, fg=TEXT, font=(FONT, 12, "bold"), anchor="w",
                                 justify="left", wraplength=800)
        self.feedback.pack(fill="x", pady=(12, 0))
        self.explain = tk.Label(outer, text="", bg=BG, fg=MUTED, font=(FONT, 11), anchor="w", justify="left",
                                wraplength=800)
        self.explain.pack(fill="x")

        bottom = tk.Frame(outer, bg=BG)
        bottom.pack(side="bottom", fill="x", pady=(12, 0))
        self.action_btn = self.button(bottom, "Submit answer", self.submit_or_next, "primary")
        self.action_btn.pack(side="right")
        self.button(bottom, "Quit quiz", self.quit_quiz).pack(side="left")
        tk.Label(bottom, text="Tip: press A-D or 1-4 to choose, Enter to continue", bg=BG, fg=MUTED,
                 font=(FONT, 9)).pack(side="left", padx=14)

    def _paint(self, index, state):
        card, badge, label = self.option_cards[index]
        look = {
            "default": (SURFACE, LINE, SURFACE_ALT),
            "selected": (SELECTED_BG, PRIMARY, SELECTED_BG),
            "correct": (CORRECT_BG, PRIMARY, CORRECT_BG),
            "wrong": (WRONG_BG, DANGER, WRONG_BG),
        }[state]
        card.config(bg=look[0], highlightbackground=look[1])
        label.config(bg=look[0])
        badge.config(bg=look[2])

    def choose(self, index):
        if self.mode != "quiz" or self.locked:
            return
        if self.selected is not None:
            self._paint(self.selected, "default")
        self.selected = index
        self._paint(index, "selected")
        self.feedback.config(text="")

    def submit_or_next(self):
        if self.mode != "quiz":
            return
        s = self.session
        if not self.locked:
            if self.selected is None:
                self.feedback.config(text="Choose an answer first.", fg=DANGER)
                return
            correct = s.check(self.selected)
            self.locked = True
            answer = s.current["answer"]
            self._paint(answer, "correct")
            if not correct:
                self._paint(self.selected, "wrong")
            self.score_label.config(text=f"Score: {s.score}")
            if correct:
                self.feedback.config(text="Correct!", fg=PRIMARY_DARK)
            else:
                self.feedback.config(text=f"Wrong. The correct answer is {LETTERS[answer]}: "
                                          f"{s.current['options'][answer]}", fg=DANGER)
            self.explain.config(text=s.current["explain"])
            last = s.index == s.total - 1
            self.action_btn.config(text="See results" if last else "Next question")
        else:
            s.advance()
            if s.finished:
                self.show_results()
            else:
                self.show_question()

    def quit_quiz(self):
        if messagebox.askyesno("Quit quiz", "Quit this quiz? Your progress will be lost."):
            self.show_menu()

    def _on_key(self, event):
        if self.mode != "quiz":
            return
        key = event.keysym.lower()
        if len(key) == 1 and key in "1234":
            index = int(key) - 1
        elif len(key) == 1 and key in "abcd":
            index = "abcd".index(key)
        elif key in ("return", "kp_enter"):
            self.submit_or_next()
            return
        else:
            return
        if index < len(self.option_cards):
            self.choose(index)

    # ----- results --------------------------------------------------------
    def show_results(self):
        self.mode = "results"
        self.clear()
        s = self.session
        outer = tk.Frame(self.container, bg=BG)
        outer.pack(fill="both", expand=True, padx=40, pady=24)
        self.heading(outer, "Quiz complete", s.name)

        summary = tk.Frame(outer, bg=SURFACE, highlightthickness=1, highlightbackground=LINE)
        summary.pack(fill="x", pady=(14, 10))
        left = tk.Frame(summary, bg=SURFACE)
        left.pack(side="left", padx=24, pady=14)
        tk.Label(left, text=f"{s.score} / {s.total}", bg=SURFACE, fg=PRIMARY_DARK, font=(FONT, 34, "bold")).pack(
            anchor="w")
        tk.Label(left, text=f"{s.percent}%   |   Time {format_time(s.elapsed)}", bg=SURFACE, fg=MUTED,
                 font=(FONT, 11)).pack(anchor="w")
        tk.Label(summary, text=grade_message(s.percent), bg=SURFACE, fg=TEXT, font=(FONT, 12), wraplength=360,
                 justify="left").pack(side="left", padx=10)

        save_row = tk.Frame(outer, bg=BG)
        save_row.pack(fill="x", pady=(0, 8))
        tk.Label(save_row, text="Your name", bg=BG, fg=MUTED, font=(FONT, 10, "bold")).pack(side="left")
        ttk.Entry(save_row, textvariable=self.last_name, width=20).pack(side="left", padx=8)
        self.save_btn = self.button(save_row, "Save score", self.save_score)
        self.save_btn.pack(side="left")
        self.save_info = tk.Label(save_row, text="", bg=BG, fg=PRIMARY_DARK, font=(FONT, 10, "bold"))
        self.save_info.pack(side="left", padx=10)

        tk.Label(outer, text="Review your answers", bg=BG, fg=TEXT, font=(FONT, 13, "bold")).pack(anchor="w")
        box = tk.Frame(outer, bg=SURFACE, highlightthickness=1, highlightbackground=LINE)
        box.pack(fill="both", expand=True, pady=(6, 10))
        text = tk.Text(box, wrap="word", bg=SURFACE, fg=TEXT, font=(FONT, 11), relief="flat", padx=12, pady=8,
                       height=8)
        scroll = ttk.Scrollbar(box, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        text.pack(side="left", fill="both", expand=True)
        text.tag_configure("q", font=(FONT, 11, "bold"), spacing1=8)
        text.tag_configure("ok", foreground=PRIMARY_DARK)
        text.tag_configure("bad", foreground=DANGER)
        for number, (question, (chosen, correct)) in enumerate(zip(s.questions, s.answers), start=1):
            text.insert("end", f"{number}. {question['q']}\n", "q")
            mine = f"{LETTERS[chosen]}: {question['options'][chosen]}"
            right = f"{LETTERS[question['answer']]}: {question['options'][question['answer']]}"
            if correct:
                text.insert("end", f"   Correct - {mine}\n", "ok")
            else:
                text.insert("end", f"   Your answer - {mine}\n", "bad")
                text.insert("end", f"   Correct answer - {right}\n", "ok")
        text.config(state="disabled")

        row = tk.Frame(outer, bg=BG)
        row.pack(fill="x")
        self.button(row, "Retake quiz", self.begin_session, "primary").pack(side="left")
        self.button(row, "Main menu", self.show_menu).pack(side="left", padx=10)
        self.button(row, "High scores", self.show_scores).pack(side="left")

    def save_score(self):
        if self.score_saved:
            self.save_info.config(text="Already saved.")
            return
        name = self.last_name.get().strip() or "Player"
        s = self.session
        if self.board.add(name, s.name, s.score, s.total, s.elapsed):
            self.score_saved = True
            self.save_info.config(text="Score saved to the leaderboard.")

    # ----- high scores ----------------------------------------------------
    def show_scores(self):
        self.mode = "other"
        self.clear()
        outer = tk.Frame(self.container, bg=BG)
        outer.pack(fill="both", expand=True, padx=40, pady=24)
        self.heading(outer, "High scores", "Top 10 results, ranked by percentage and then by time.")

        wrap = tk.Frame(outer, bg=SURFACE, highlightthickness=1, highlightbackground=LINE)
        wrap.pack(fill="both", expand=True, pady=14)
        columns = ("rank", "name", "quiz", "score", "percent", "time", "date")
        tree = ttk.Treeview(wrap, columns=columns, show="headings", selectmode="none")
        for col, head, width in zip(columns, ("#", "Name", "Quiz", "Score", "Percent", "Time", "Date"),
                                    (40, 160, 170, 80, 80, 70, 110)):
            tree.heading(col, text=head)
            tree.column(col, width=width, anchor="w", stretch=(col == "quiz"))
        tree.pack(fill="both", expand=True)
        entries = self.board.top(10)
        for rank, e in enumerate(entries, start=1):
            tree.insert("", "end", values=(rank, e["name"], e["quiz"], f"{e['score']}/{e['total']}",
                                           f"{e['percent']}%", format_time(e.get("seconds", 0)), e["date"]))
        if not entries:
            tk.Label(wrap, text="No scores yet. Finish a quiz and save your score.", bg=SURFACE, fg=MUTED,
                     font=(FONT, 11)).place(relx=0.5, rely=0.55, anchor="center")

        row = tk.Frame(outer, bg=BG)
        row.pack(fill="x")
        self.button(row, "Back to menu", self.show_menu, "primary").pack(side="left")
        self.button(row, "Clear scores", self.clear_scores, "danger").pack(side="left", padx=10)

    def clear_scores(self):
        if self.board.entries and messagebox.askyesno("Clear scores", "Delete all saved high scores?"):
            self.board.clear()
            self.show_scores()

    # ----- add a custom question -----------------------------------------
    def show_add_question(self):
        self.mode = "other"
        self.clear()
        outer = tk.Frame(self.container, bg=BG)
        outer.pack(fill="both", expand=True, padx=40, pady=24)
        self.heading(outer, "Add your own question",
                     f"Questions are saved in \"{CUSTOM_NAME}\". You have {len(self.bank.custom)} saved so far.")

        card = tk.Frame(outer, bg=SURFACE, highlightthickness=1, highlightbackground=LINE)
        card.pack(fill="x", pady=14)
        inner = tk.Frame(card, bg=SURFACE)
        inner.pack(fill="x", padx=22, pady=18)
        inner.columnconfigure(1, weight=1)

        self.var_question = tk.StringVar()
        self.var_opts = [tk.StringVar() for _ in range(4)]
        self.var_correct = tk.IntVar(value=0)
        self.var_explain = tk.StringVar()

        tk.Label(inner, text="Question", bg=SURFACE, fg=MUTED, font=(FONT, 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=6, padx=(0, 12))
        ttk.Entry(inner, textvariable=self.var_question).grid(row=0, column=1, columnspan=2, sticky="ew", pady=6)
        tk.Label(inner, text="Options (select the correct one)", bg=SURFACE, fg=MUTED,
                 font=(FONT, 10, "bold")).grid(row=1, column=0, columnspan=3, sticky="w", pady=(10, 2))
        for i in range(4):
            tk.Radiobutton(inner, text=LETTERS[i], variable=self.var_correct, value=i, bg=SURFACE,
                           activebackground=SURFACE, fg=TEXT, selectcolor=SURFACE, font=(FONT, 11, "bold")).grid(
                row=2 + i, column=0, sticky="w")
            ttk.Entry(inner, textvariable=self.var_opts[i]).grid(row=2 + i, column=1, columnspan=2, sticky="ew",
                                                                  pady=4)
        tk.Label(inner, text="Explanation (optional)", bg=SURFACE, fg=MUTED, font=(FONT, 10, "bold")).grid(
            row=6, column=0, sticky="w", pady=(10, 6), padx=(0, 12))
        ttk.Entry(inner, textvariable=self.var_explain).grid(row=6, column=1, columnspan=2, sticky="ew",
                                                              pady=(10, 6))
        self.add_info = tk.Label(inner, text="", bg=SURFACE, fg=DANGER, font=(FONT, 10, "bold"), anchor="w")
        self.add_info.grid(row=7, column=0, columnspan=3, sticky="w")

        row = tk.Frame(outer, bg=BG)
        row.pack(fill="x")
        self.button(row, "Save question", self.save_question, "primary").pack(side="left")
        self.button(row, "Back to menu", self.show_menu).pack(side="left", padx=10)
        if self.bank.custom:
            self.button(row, "Delete all custom questions", self.clear_custom, "danger").pack(side="left")

    def save_question(self):
        question = self.var_question.get().strip()
        options = [v.get().strip() for v in self.var_opts]
        if not question:
            self.add_info.config(text="Enter the question text.", fg=DANGER)
            return
        if not all(options):
            self.add_info.config(text="Fill in all four options.", fg=DANGER)
            return
        if len({o.lower() for o in options}) < 4:
            self.add_info.config(text="Each option must be different.", fg=DANGER)
            return
        if self.bank.add_custom(question, options, self.var_correct.get(), self.var_explain.get().strip()):
            self.show_add_question()
            self.add_info.config(text="Question saved. Add another or go back to the menu.", fg=PRIMARY_DARK)

    def clear_custom(self):
        if messagebox.askyesno("Delete questions", "Delete all of your custom questions?"):
            self.bank.clear_custom()
            self.show_add_question()


if __name__ == "__main__":
    QuizApp().mainloop()