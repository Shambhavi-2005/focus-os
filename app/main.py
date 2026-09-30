import tkinter as tk
from tkinter import messagebox
import time
import json
import os

import psutil

from app.app_monitor import get_active_window
from app.power_manager import get_power_status
from app.focus_engine import FocusEngine
from app.browser_monitor import start_browser_monitor

from ai.voice_engine import VoiceEngine
from ai.intent_engine import IntentEngine

# Adaptive optimizer
try:
    from app.adaptive_optimizer import AdaptiveOptimizer
except ImportError:
    try:
        from app.optimizer import AdaptiveOptimizer
    except ImportError:
        AdaptiveOptimizer = None


class FocusOS:

    def __init__(self, root):

        self.root = root

        # ============================================================
        # WINDOW
        # ============================================================

        self.root.title("Focus OS")
        self.root.geometry("1100x800")
        self.root.minsize(900, 700)

        self.root.configure(
            bg="#07111F"
        )

        self.root.resizable(
            True,
            True
        )

        self.root.bind(
            "<F11>",
            self.toggle_fullscreen
        )

        self.root.bind(
            "<Escape>",
            self.exit_fullscreen
        )

        # ============================================================
        # COLORS
        # ============================================================

        self.bg = "#07111F"
        self.card = "#0D1B2A"
        self.card_light = "#12263A"
        self.input_bg = "#0A1725"

        self.white = "#FFFFFF"
        self.text = "#DCE6EF"
        self.muted = "#8FA3B7"

        self.blue = "#38BDF8"
        self.blue_dark = "#0EA5E9"

        self.green = "#4ADE80"
        self.red = "#F87171"
        self.yellow = "#FACC15"

        # ============================================================
        # STATE
        # ============================================================

        self.running = False

        self.goal = ""
        self.session_duration = 0
        self.session_start_time = None

        self.current_application = "Unknown"
        self.current_domain = "Unknown"

        self.current_focus_status = "UNKNOWN"

        self.power_status = {
            "battery": "Unknown",
            "charging": False,
            "power": "Unknown"
        }

        self.last_voice_command = None
        self.last_voice_intent = None

        self.voice_busy = False

        # ============================================================
        # FOCUS COINS
        # ============================================================

        self.coins_file = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "focus_coins.json"
        )

        self.focus_coins = self.load_focus_coins()

        self.session_coins_awarded = 0

        # ============================================================
        # ENGINES
        # ============================================================

        self.focus_engine = FocusEngine()

        self.voice_engine = VoiceEngine(
            microphone_device=1
        )

        self.intent_engine = IntentEngine()

        if AdaptiveOptimizer is not None:

            try:

                self.optimizer = AdaptiveOptimizer()

            except Exception as error:

                print(
                    "Adaptive optimizer initialization error:"
                )
                print(error)

                self.optimizer = None

        else:

            self.optimizer = None

        # ============================================================
        # UI
        # ============================================================

        self.build_interface()

        # ============================================================
        # START MONITORS
        # ============================================================

        self.update_system_state()
        self.update_power_status()
        self.update_optimizer()

    # ================================================================
    # FOCUS COINS
    # ================================================================

    def load_focus_coins(self):

        try:

            if os.path.exists(
                self.coins_file
            ):

                with open(
                    self.coins_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    data = json.load(file)

                    return int(
                        data.get(
                            "coins",
                            0
                        )
                    )

        except Exception as error:

            print(
                "Could not load focus coins:"
            )

            print(error)

        return 0

    def save_focus_coins(self):

        try:

            with open(
                self.coins_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    {
                        "coins": self.focus_coins
                    },
                    file,
                    indent=4
                )

        except Exception as error:

            print(
                "Could not save focus coins:"
            )

            print(error)

    def award_focus_coins(
        self,
        completed_seconds
    ):

        # 1 coin for every 5 completed minutes
        earned_coins = int(
            completed_seconds // 300
        )

        if earned_coins <= 0:

            return 0

        self.focus_coins += earned_coins

        self.session_coins_awarded = earned_coins

        self.save_focus_coins()

        self.update_coin_display()

        return earned_coins

    def update_coin_display(self):

        if hasattr(
            self,
            "coins_label"
        ):

            self.coins_label.config(
                text=(
                    f"🪙 {self.focus_coins} COINS"
                )
            )

    # ================================================================
    # FULLSCREEN
    # ================================================================

    def toggle_fullscreen(
        self,
        event=None
    ):

        current = self.root.attributes(
            "-fullscreen"
        )

        self.root.attributes(
            "-fullscreen",
            not current
        )

    def exit_fullscreen(
        self,
        event=None
    ):

        self.root.attributes(
            "-fullscreen",
            False
        )

    # ================================================================
    # UI HELPERS
    # ================================================================

    def create_card(
        self,
        parent,
        bg=None
    ):

        if bg is None:
            bg = self.card

        return tk.Frame(
            parent,
            bg=bg,
            highlightthickness=1,
            highlightbackground="#173149"
        )

    def create_label(
        self,
        parent,
        text="",
        size=10,
        weight="normal",
        color=None,
        bg=None
    ):

        if color is None:
            color = self.text

        if bg is None:
            bg = self.card

        return tk.Label(
            parent,
            text=text,
            bg=bg,
            fg=color,
            font=(
                "Segoe UI",
                size,
                weight
            )
        )

    # ================================================================
    # BUILD INTERFACE
    # ================================================================

    def build_interface(self):

        # ------------------------------------------------------------
        # Main container
        # ------------------------------------------------------------

        self.main_container = tk.Frame(
            self.root,
            bg=self.bg
        )

        self.main_container.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=24
        )

        # ------------------------------------------------------------
        # HEADER
        # ------------------------------------------------------------

        header = tk.Frame(
            self.main_container,
            bg=self.bg
        )

        header.pack(
            fill="x",
            pady=(0, 20)
        )

        title = tk.Label(
            header,
            text="◉  FOCUS OS",
            bg=self.bg,
            fg=self.white,
            font=(
                "Segoe UI",
                22,
                "bold"
            )
        )

        title.pack(
            side="left"
        )

        subtitle = tk.Label(
            header,
            text="Privacy-first adaptive productivity",
            bg=self.bg,
            fg=self.muted,
            font=(
                "Segoe UI",
                10
            )
        )

        subtitle.pack(
            side="left",
            padx=(16, 0),
            pady=(7, 0)
        )

        # ------------------------------------------------------------
        # COINS
        # ------------------------------------------------------------

        self.coins_label = tk.Label(
            header,
            text=f"🪙 {self.focus_coins} COINS",
            bg="#17293A",
            fg=self.yellow,
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            padx=14,
            pady=7
        )

        self.coins_label.pack(
            side="right",
            padx=(0, 10)
        )

        # ------------------------------------------------------------
        # STATUS
        # ------------------------------------------------------------

        self.status_label = tk.Label(
            header,
            text="● READY",
            bg="#102B24",
            fg=self.green,
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            padx=14,
            pady=7
        )

        self.status_label.pack(
            side="right"
        )

        # ------------------------------------------------------------
        # TWO COLUMN LAYOUT
        # ------------------------------------------------------------

        content = tk.Frame(
            self.main_container,
            bg=self.bg
        )

        content.pack(
            fill="both",
            expand=True
        )

        content.grid_columnconfigure(
            0,
            weight=1
        )

        content.grid_columnconfigure(
            1,
            weight=1
        )

        content.grid_rowconfigure(
            0,
            weight=1
        )

        # ============================================================
        # LEFT COLUMN
        # ============================================================

        left_column = tk.Frame(
            content,
            bg=self.bg
        )

        left_column.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 10)
        )

        # ------------------------------------------------------------
        # FOCUS SESSION CARD
        # ------------------------------------------------------------

        session_card = self.create_card(
            left_column
        )

        session_card.pack(
            fill="x",
            pady=(0, 12)
        )

        self.create_label(
            session_card,
            "FOCUS SESSION",
            size=11,
            weight="bold",
            color=self.white
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 14)
        )

        self.create_label(
            session_card,
            "What are you working on?",
            size=9,
            color=self.muted
        ).pack(
            anchor="w",
            padx=20
        )

        self.goal_entry = tk.Entry(
            session_card,
            bg=self.input_bg,
            fg=self.white,
            insertbackground=self.white,
            relief="flat",
            font=(
                "Segoe UI",
                11
            )
        )

        self.goal_entry.pack(
            fill="x",
            padx=20,
            pady=(7, 14),
            ipady=9
        )

        self.create_label(
            session_card,
            "Duration (minutes)",
            size=9,
            color=self.muted
        ).pack(
            anchor="w",
            padx=20
        )

        self.duration_entry = tk.Entry(
            session_card,
            bg=self.input_bg,
            fg=self.white,
            insertbackground=self.white,
            relief="flat",
            font=(
                "Segoe UI",
                11
            )
        )

        self.duration_entry.insert(
            0,
            "25"
        )

        self.duration_entry.pack(
            fill="x",
            padx=20,
            pady=(7, 16),
            ipady=9
        )

        button_row = tk.Frame(
            session_card,
            bg=self.card
        )

        button_row.pack(
            fill="x",
            padx=20,
            pady=(0, 18)
        )

        self.start_button = tk.Button(
            button_row,
            text="START FOCUS",
            command=self.start_session,
            bg=self.blue_dark,
            fg=self.white,
            activebackground=self.blue,
            activeforeground=self.white,
            relief="flat",
            borderwidth=0,
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="hand2"
        )

        self.start_button.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=9
        )

        self.stop_button = tk.Button(
            button_row,
            text="STOP",
            command=self.stop_session,
            bg="#17293A",
            fg=self.text,
            activebackground="#233D52",
            activeforeground=self.white,
            relief="flat",
            borderwidth=0,
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="hand2"
        )

        self.stop_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
            ipady=9
        )

        # ------------------------------------------------------------
        # VOICE CARD
        # ------------------------------------------------------------

        voice_card = self.create_card(
            left_column
        )

        voice_card.pack(
            fill="x",
            pady=(0, 12)
        )

        self.create_label(
            voice_card,
            "VOICE COMMAND",
            size=11,
            weight="bold",
            color=self.white
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 5)
        )

        self.voice_status_label = self.create_label(
            voice_card,
            "Say something like:",
            size=9,
            color=self.muted
        )

        self.voice_status_label.pack(
            anchor="w",
            padx=20
        )

        self.voice_example_label = self.create_label(
            voice_card,
            '"Start a 45 minute Verilog session"',
            size=10,
            color=self.text
        )

        self.voice_example_label.pack(
            anchor="w",
            padx=20,
            pady=(5, 12)
        )

        self.voice_button = tk.Button(
            voice_card,
            text="🎤  VOICE COMMAND",
            command=self.start_voice_command,
            bg="#173149",
            fg=self.white,
            activebackground="#214764",
            activeforeground=self.white,
            relief="flat",
            borderwidth=0,
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="hand2"
        )

        self.voice_button.pack(
            fill="x",
            padx=20,
            pady=(0, 18),
            ipady=9
        )

        # ------------------------------------------------------------
        # SESSION INFO CARD
        # ------------------------------------------------------------

        session_info = self.create_card(
            left_column
        )

        session_info.pack(
            fill="both",
            expand=True
        )

        self.create_label(
            session_info,
            "SESSION",
            size=11,
            weight="bold",
            color=self.white
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        self.timer_label = tk.Label(
            session_info,
            text="25:00",
            bg=self.card,
            fg=self.white,
            font=(
                "Segoe UI",
                40,
                "bold"
            )
        )

        self.timer_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 5)
        )

        self.session_goal_label = self.create_label(
            session_info,
            "No active session",
            size=10,
            color=self.muted
        )

        self.session_goal_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        self.voice_command_display = self.create_label(
            session_info,
            "Last voice command: —",
            size=9,
            color=self.text
        )

        self.voice_command_display.pack(
            anchor="w",
            padx=20,
            pady=(0, 8)
        )

        self.voice_intent_display = self.create_label(
            session_info,
            "Intent: —",
            size=9,
            color=self.muted
        )

        self.voice_intent_display.pack(
            anchor="w",
            padx=20,
            pady=(0, 18)
        )

        # ============================================================
        # RIGHT COLUMN
        # ============================================================

        right_column = tk.Frame(
            content,
            bg=self.bg
        )

        right_column.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(10, 0)
        )

        # ------------------------------------------------------------
        # ADAPTIVE PERFORMANCE CARD
        # ------------------------------------------------------------

        adaptive_card = self.create_card(
            right_column,
            bg=self.card_light
        )

        adaptive_card.pack(
            fill="x",
            pady=(0, 12)
        )

        tk.Label(
            adaptive_card,
            text="⚡  ADAPTIVE PERFORMANCE",
            bg=self.card_light,
            fg=self.white,
            font=(
                "Segoe UI",
                12,
                "bold"
            )
        ).pack(
            anchor="w",
            padx=22,
            pady=(18, 4)
        )

        self.optimizer_mode_label = tk.Label(
            adaptive_card,
            text="BALANCED",
            bg=self.card_light,
            fg="#FFFFFF",
            font=(
                "Segoe UI",
                22,
                "bold"
            )
        )

        self.optimizer_mode_label.pack(
            anchor="w",
            padx=22,
            pady=(3, 5)
        )

        self.optimizer_reason_label = tk.Label(
            adaptive_card,
            text="Waiting for adaptive analysis...",
            bg=self.card_light,
            fg="#EAF2F8",
            font=(
                "Segoe UI",
                10
            ),
            wraplength=430,
            justify="left"
        )

        self.optimizer_reason_label.pack(
            anchor="w",
            padx=22,
            pady=(0, 14)
        )

        self.optimizer_metrics_label = tk.Label(
            adaptive_card,
            text="CPU --   •   Battery --   •   Power --",
            bg=self.card_light,
            fg="#FFFFFF",
            font=(
                "Segoe UI",
                9,
                "bold"
            )
        )

        self.optimizer_metrics_label.pack(
            anchor="w",
            padx=22,
            pady=(0, 12)
        )

        self.optimizer_action_label = tk.Label(
            adaptive_card,
            text="",
            bg=self.card_light,
            fg="#DCE6EF",
            font=(
                "Segoe UI",
                9
            ),
            wraplength=430,
            justify="left"
        )

        self.optimizer_action_label.pack(
            anchor="w",
            padx=22,
            pady=(0, 18)
        )

        # ------------------------------------------------------------
        # CURRENT ACTIVITY CARD
        # ------------------------------------------------------------

        activity_card = self.create_card(
            right_column
        )

        activity_card.pack(
            fill="x",
            pady=(0, 12)
        )

        self.create_label(
            activity_card,
            "CURRENT ACTIVITY",
            size=11,
            weight="bold",
            color=self.white
        ).pack(
            anchor="w",
            padx=20,
            pady=(17, 12)
        )

        app_row = tk.Frame(
            activity_card,
            bg=self.card
        )

        app_row.pack(
            fill="x",
            padx=20,
            pady=3
        )

        self.create_label(
            app_row,
            "Application",
            size=9,
            color=self.muted
        ).pack(
            side="left"
        )

        self.active_app_label = self.create_label(
            app_row,
            "Unknown",
            size=10,
            weight="bold",
            color=self.white
        )

        self.active_app_label.pack(
            side="right"
        )

        website_row = tk.Frame(
            activity_card,
            bg=self.card
        )

        website_row.pack(
            fill="x",
            padx=20,
            pady=3
        )

        self.create_label(
            website_row,
            "Website",
            size=9,
            color=self.muted
        ).pack(
            side="left"
        )

        self.website_label = self.create_label(
            website_row,
            "Unknown",
            size=10,
            weight="bold",
            color=self.white
        )

        self.website_label.pack(
            side="right"
        )

        focus_row = tk.Frame(
            activity_card,
            bg=self.card
        )

        focus_row.pack(
            fill="x",
            padx=20,
            pady=(3, 17)
        )

        self.create_label(
            focus_row,
            "Focus status",
            size=9,
            color=self.muted
        ).pack(
            side="left"
        )

        self.focus_status_label = self.create_label(
            focus_row,
            "UNKNOWN",
            size=10,
            weight="bold",
            color=self.muted
        )

        self.focus_status_label.pack(
            side="right"
        )

        # ------------------------------------------------------------
        # SYSTEM STATUS CARD
        # ------------------------------------------------------------

        system_card = self.create_card(
            right_column
        )

        system_card.pack(
            fill="x",
            pady=(0, 12)
        )

        self.create_label(
            system_card,
            "SYSTEM STATUS",
            size=11,
            weight="bold",
            color=self.white
        ).pack(
            anchor="w",
            padx=20,
            pady=(17, 12)
        )

        system_row = tk.Frame(
            system_card,
            bg=self.card
        )

        system_row.pack(
            fill="x",
            padx=20,
            pady=(0, 17)
        )

        self.battery_label = self.create_label(
            system_row,
            "Battery: --",
            size=10,
            weight="bold",
            color=self.white
        )

        self.battery_label.pack(
            side="left"
        )

        self.power_label = self.create_label(
            system_row,
            "Power: --",
            size=10,
            weight="bold",
            color=self.white
        )

        self.power_label.pack(
            side="right"
        )

        # ------------------------------------------------------------
        # FOOTER
        # ------------------------------------------------------------

        footer = tk.Frame(
            self.main_container,
            bg=self.bg
        )

        footer.pack(
            fill="x",
            pady=(12, 0)
        )

        footer_text = tk.Label(
            footer,
            text=(
                "Focus OS runs locally • "
                "No screenshots • No keystroke monitoring • "
                "Privacy-first"
            ),
            bg=self.bg,
            fg="#71869A",
            font=(
                "Segoe UI",
                8
            )
        )

        footer_text.pack(
            side="left"
        )

        fullscreen_text = tk.Label(
            footer,
            text="F11  Fullscreen",
            bg=self.bg,
            fg="#71869A",
            font=(
                "Segoe UI",
                8
            )
        )

        fullscreen_text.pack(
            side="right"
        )

    # ================================================================
    # SESSION
    # ================================================================

    def start_session(
        self,
        goal_override=None,
        minutes_override=None
    ):

        if goal_override is not None:

            goal = str(
                goal_override
            ).strip()

        else:

            goal = self.goal_entry.get().strip()

        if not goal:
            goal = "general"

        if minutes_override is not None:

            try:

                minutes = int(
                    minutes_override
                )

            except Exception:

                minutes = 25

        else:

            try:

                minutes = int(
                    self.duration_entry.get()
                )

            except Exception:

                messagebox.showerror(
                    "Invalid Duration",
                    "Please enter a valid number of minutes."
                )

                return

        if minutes <= 0:

            messagebox.showerror(
                "Invalid Duration",
                "Duration must be greater than zero."
            )

            return

        self.goal = goal

        self.session_duration = (
            minutes * 60
        )

        self.session_start_time = time.time()

        self.running = True

        self.session_coins_awarded = 0

        self.session_goal_label.config(
            text=f"Goal: {goal}"
        )

        self.status_label.config(
            text="● FOCUSING",
            bg="#102B24",
            fg=self.green
        )

        self.start_button.config(
            state="disabled"
        )

        self.stop_button.config(
            state="normal"
        )

        self.update_timer()

        self.update_optimizer()

    def stop_session(self):

        earned_coins = 0

        # Award coins for completed 5-minute blocks
        # if the user manually stops early.
        if (
            self.running
            and self.session_start_time
        ):

            elapsed = int(
                time.time()
                - self.session_start_time
            )

            earned_coins = self.award_focus_coins(
                elapsed
            )

        self.running = False

        self.session_start_time = None

        self.status_label.config(
            text="● READY",
            bg="#102B24",
            fg=self.green
        )

        self.start_button.config(
            state="normal"
        )

        self.stop_button.config(
            state="normal"
        )

        self.timer_label.config(
            text="00:00"
        )

        self.session_goal_label.config(
            text="No active session"
        )

        self.optimizer_mode_label.config(
            text="STANDBY",
            fg=self.muted
        )

        self.optimizer_reason_label.config(
            text=(
                "Start a focus session to activate "
                "adaptive optimization."
            )
        )

        self.optimizer_metrics_label.config(
            text="CPU --   •   Battery --   •   Power --"
        )

        self.optimizer_action_label.config(
            text=""
        )

        if earned_coins > 0:

            self.voice_status_label.config(
                text=(
                    f"Session stopped. "
                    f"🪙 +{earned_coins} Focus Coins!"
                ),
                fg=self.yellow
            )

    # ================================================================
    # TIMER
    # ================================================================

    def update_timer(self):

        if not self.running:
            return

        elapsed = int(
            time.time()
            - self.session_start_time
        )

        remaining = (
            self.session_duration
            - elapsed
        )

        if remaining <= 0:

            self.timer_label.config(
                text="00:00"
            )

            self.running = False

            self.session_start_time = None

            # --------------------------------------------------------
            # AWARD COINS
            # --------------------------------------------------------

            earned_coins = self.award_focus_coins(
                self.session_duration
            )

            self.status_label.config(
                text="● COMPLETE",
                bg="#16301F",
                fg=self.green
            )

            self.start_button.config(
                state="normal"
            )

            self.stop_button.config(
                state="normal"
            )

            self.voice_status_label.config(
                text=(
                    f"🎉 Session complete! "
                    f"🪙 +{earned_coins} Focus Coins!"
                ),
                fg=self.yellow
            )

            messagebox.showinfo(
                "Focus Session Complete",
                (
                    "🎉 Focus session complete!\n\n"
                    f"🪙 You earned {earned_coins} "
                    "Focus Coins!\n\n"
                    f"💰 Total coins: "
                    f"{self.focus_coins}"
                )
            )

            return

        minutes = remaining // 60

        seconds = remaining % 60

        self.timer_label.config(
            text=f"{minutes:02d}:{seconds:02d}"
        )

        self.root.after(
            1000,
            self.update_timer
        )

    # ================================================================
    # SYSTEM MONITOR
    # ================================================================

    def update_system_state(self):

        try:

            self.current_application = (
                get_active_window()
            )

        except Exception:

            self.current_application = "Unknown"

        try:

            browser_state = (
                self.get_browser_state()
            )

            self.current_domain = (
                browser_state.get(
                    "domain",
                    "Unknown"
                )
            )

        except Exception:

            self.current_domain = "Unknown"

        try:

            self.current_focus_status = (
                self.focus_engine.evaluate(
                    self.current_application,
                    self.current_domain
                )
            )

        except Exception:

            self.current_focus_status = "UNKNOWN"

        self.active_app_label.config(
            text=self.current_application
        )

        self.website_label.config(
            text=self.current_domain
        )

        self.update_focus_status_ui()

        self.root.after(
            1000,
            self.update_system_state
        )

    def get_browser_state(self):

        import urllib.request
        import json

        try:

            with urllib.request.urlopen(
                "http://127.0.0.1:8765/browser",
                timeout=0.2
            ) as response:

                return json.loads(
                    response.read().decode()
                )

        except Exception:

            return {
                "browser": "Unknown",
                "domain": "Unknown"
            }

    def update_focus_status_ui(self):

        status = self.current_focus_status

        if status == "FOCUSED":

            self.focus_status_label.config(
                text="FOCUSED",
                fg=self.green
            )

        elif status == "DISTRACTION":

            self.focus_status_label.config(
                text="DISTRACTION",
                fg=self.red
            )

        else:

            self.focus_status_label.config(
                text="UNKNOWN",
                fg=self.muted
            )

    # ================================================================
    # POWER
    # ================================================================

    def update_power_status(self):

        try:

            self.power_status = (
                get_power_status()
            )

            battery = self.power_status.get(
                "battery",
                "Unknown"
            )

            charging = self.power_status.get(
                "charging",
                False
            )

            power = self.power_status.get(
                "power",
                "Unknown"
            )

            if isinstance(
                battery,
                int
            ):

                self.battery_label.config(
                    text=f"Battery: {battery}%"
                )

            else:

                self.battery_label.config(
                    text="Battery: Unknown"
                )

            if charging:

                self.power_label.config(
                    text="Power: Plugged In"
                )

            else:

                self.power_label.config(
                    text=f"Power: {power}"
                )

        except Exception as error:

            print(
                "Power status error:"
            )

            print(error)

        self.root.after(
            5000,
            self.update_power_status
        )

    # ================================================================
    # ADAPTIVE OPTIMIZER
    # ================================================================

    def update_optimizer(self):

        if not self.running:

            self.root.after(
                3000,
                self.update_optimizer
            )

            return

        cpu_percent = 0.0

        try:

            cpu_percent = psutil.cpu_percent(
                interval=None
            )

        except Exception:

            pass

        battery = self.power_status.get(
            "battery",
            0
        )

        charging = self.power_status.get(
            "charging",
            False
        )

        # ------------------------------------------------------------
        # No optimizer module
        # ------------------------------------------------------------

        if self.optimizer is None:

            self.optimizer_mode_label.config(
                text="BALANCED",
                fg=self.white
            )

            self.optimizer_reason_label.config(
                text="Adaptive optimizer unavailable."
            )

            self.optimizer_metrics_label.config(
                text=(
                    f"CPU {cpu_percent:.1f}%   •   "
                    f"Battery {battery}%   •   "
                    f"{'Plugged In' if charging else 'On Battery'}"
                )
            )

            self.root.after(
                3000,
                self.update_optimizer
            )

            return

        # ------------------------------------------------------------
        # Run optimizer
        # ------------------------------------------------------------

        try:

            result = None

            if hasattr(
                self.optimizer,
                "evaluate"
            ):

                method = self.optimizer.evaluate

                try:

                    result = method(
                        self.goal,
                        self.current_application,
                        battery,
                        charging,
                        cpu_percent
                    )

                except TypeError:

                    result = method(
                        goal=self.goal,
                        application=self.current_application,
                        battery=battery,
                        charging=charging,
                        cpu_percent=cpu_percent
                    )

            elif hasattr(
                self.optimizer,
                "optimize"
            ):

                method = self.optimizer.optimize

                try:

                    result = method(
                        self.goal,
                        self.current_application,
                        battery,
                        charging,
                        cpu_percent
                    )

                except TypeError:

                    result = method(
                        goal=self.goal,
                        application=self.current_application,
                        battery=battery,
                        charging=charging,
                        cpu_percent=cpu_percent
                    )

            # --------------------------------------------------------
            # Convert result
            # --------------------------------------------------------

            if hasattr(
                result,
                "to_dict"
            ):

                result = result.to_dict()

            if not isinstance(
                result,
                dict
            ):

                raise ValueError(
                    "Optimizer returned an invalid result."
                )

            mode = result.get(
                "mode",
                "BALANCED"
            )

            reason = result.get(
                "reason",
                "Adaptive optimization active."
            )

            actions = result.get(
                "actions",
                []
            )

            # --------------------------------------------------------
            # Mode color
            # --------------------------------------------------------

            if mode == "PERFORMANCE":

                mode_color = self.blue

            elif mode == "EFFICIENCY":

                mode_color = self.green

            elif mode == "BALANCED":

                mode_color = self.white

            else:

                mode_color = self.muted

            self.optimizer_mode_label.config(
                text=str(mode),
                fg=mode_color
            )

            self.optimizer_reason_label.config(
                text=str(reason),
                fg="#EAF2F8"
            )

            power_text = (
                "Plugged In"
                if charging
                else "On Battery"
            )

            self.optimizer_metrics_label.config(
                text=(
                    f"CPU {cpu_percent:.1f}%   •   "
                    f"Battery {battery}%   •   "
                    f"{power_text}"
                )
            )

            # --------------------------------------------------------
            # Actions
            # --------------------------------------------------------

            if isinstance(
                actions,
                list
            ):

                action_lines = []

                for action in actions[:3]:

                    action_lines.append(
                        f"✓ {action}"
                    )

                action_text = "\n".join(
                    action_lines
                )

            else:

                action_text = str(
                    actions
                )

            self.optimizer_action_label.config(
                text=action_text
            )

        except Exception as error:

            print(
                "Adaptive optimizer error:"
            )

            print(error)

            self.optimizer_mode_label.config(
                text="BALANCED",
                fg=self.white
            )

            self.optimizer_reason_label.config(
                text="Adaptive optimization active."
            )

            self.optimizer_metrics_label.config(
                text=(
                    f"CPU {cpu_percent:.1f}%   •   "
                    f"Battery {battery}%   •   "
                    f"{'Plugged In' if charging else 'On Battery'}"
                )
            )

        self.root.after(
            3000,
            self.update_optimizer
        )

    # ================================================================
    # VOICE COMMAND
    # ================================================================

    def start_voice_command(self):

        if self.voice_busy:
            return

        self.voice_busy = True

        self.voice_button.config(
            text="🎤  LISTENING...",
            bg="#234A63"
        )

        self.voice_status_label.config(
            text="Listening... speak your command.",
            fg=self.blue
        )

        self.status_label.config(
            text="● LISTENING",
            bg="#102A3B",
            fg=self.blue
        )

        self.voice_engine.listen_async(
            self.handle_voice_result,
            duration=8
        )

    def handle_voice_result(
        self,
        result
    ):

        self.root.after(
            0,
            lambda: self.process_voice_result(
                result
            )
        )

    def process_voice_result(
        self,
        transcription
    ):

        self.voice_busy = False

        self.voice_button.config(
            text="🎤  VOICE COMMAND",
            bg="#173149"
        )

        if self.running:

            self.status_label.config(
                text="● FOCUSING",
                bg="#102B24",
                fg=self.green
            )

        else:

            self.status_label.config(
                text="● READY",
                bg="#102B24",
                fg=self.green
            )

        if not transcription:

            self.voice_status_label.config(
                text="No speech detected.",
                fg=self.red
            )

            return

        # ------------------------------------------------------------
        # Parse command
        # ------------------------------------------------------------

        try:

            parsed_command = (
                self.voice_engine.parse_command(
                    transcription
                )
            )

        except Exception as error:

            print(
                "Voice parser error:"
            )

            print(error)

            self.voice_status_label.config(
                text="Could not understand command.",
                fg=self.red
            )

            return

        self.last_voice_command = parsed_command

        # ------------------------------------------------------------
        # Intent
        # ------------------------------------------------------------

        try:

            intent = (
                self.intent_engine.understand(
                    parsed_command
                )
            )

        except Exception as error:

            print(
                "Intent engine error:"
            )

            print(error)

            intent = {
                "intent": "UNKNOWN"
            }

        self.last_voice_intent = intent

        # ------------------------------------------------------------
        # UI
        # ------------------------------------------------------------

        self.voice_status_label.config(
            text=transcription,
            fg=self.text
        )

        self.voice_command_display.config(
            text=(
                f"Last voice command: "
                f"{transcription}"
            )
        )

        intent_name = (
            intent.get(
                "intent",
                intent.get(
                    "command",
                    "UNKNOWN"
                )
            )
        )

        self.voice_intent_display.config(
            text=f"Intent: {intent_name}"
        )

        # ------------------------------------------------------------
        # Execute
        # ------------------------------------------------------------

        self.execute_voice_intent(
            intent
        )

    # ================================================================
    # VOICE INTENT EXECUTION
    # ================================================================

    def execute_voice_intent(
        self,
        intent
    ):

        if not isinstance(
            intent,
            dict
        ):

            return

        command = intent.get(
            "command",
            intent.get(
                "intent",
                "UNKNOWN"
            )
        )

        # ------------------------------------------------------------
        # START SESSION
        # ------------------------------------------------------------

        if command == "START_SESSION":

            duration = intent.get(
                "duration",
                25
            )

            goal = intent.get(
                "goal",
                "general"
            )

            try:

                duration = int(
                    duration
                )

            except Exception:

                duration = 25

            self.goal_entry.delete(
                0,
                tk.END
            )

            self.goal_entry.insert(
                0,
                str(goal)
            )

            self.duration_entry.delete(
                0,
                tk.END
            )

            self.duration_entry.insert(
                0,
                str(duration)
            )

            self.start_session(
                goal_override=goal,
                minutes_override=duration
            )

            return

        # ------------------------------------------------------------
        # ALLOW WEBSITE
        # ------------------------------------------------------------

        if command == "ALLOW_WEBSITE":

            website = intent.get(
                "website",
                "website"
            )

            duration = intent.get(
                "duration",
                None
            )

            if duration:

                message = (
                    f"{website} temporarily allowed "
                    f"for {duration} minutes."
                )

            else:

                message = (
                    f"{website} temporary access requested."
                )

            self.voice_status_label.config(
                text=message,
                fg=self.green
            )

            return

        # ------------------------------------------------------------
        # FOCUS STATUS
        # ------------------------------------------------------------

        if command == "FOCUS_STATUS":

            status = self.current_focus_status

            if status == "FOCUSED":

                message = (
                    "You are currently focused."
                )

            elif status == "DISTRACTION":

                message = (
                    "A distraction has been detected."
                )

            else:

                message = (
                    "Your current activity is unknown."
                )

            self.voice_status_label.config(
                text=message,
                fg=self.text
            )

            return

        # ------------------------------------------------------------
        # STOP SESSION
        # ------------------------------------------------------------

        if command == "STOP_SESSION":

            self.stop_session()

            self.voice_status_label.config(
                text="Focus session stopped.",
                fg=self.text
            )

            return

        # ------------------------------------------------------------
        # UNKNOWN
        # ------------------------------------------------------------

        self.voice_status_label.config(
            text="I couldn't understand that command.",
            fg=self.red
        )

    # ================================================================
    # RUN
    # ================================================================


def main():

    # Start local browser bridge
    start_browser_monitor()

    root = tk.Tk()

    app = FocusOS(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()