
import time

from app.power_manager import get_power_status


class AdaptiveOptimizer:
    """
    Focus OS adaptive PC optimization engine.

    This MVP does not directly modify Windows power plans.
    Instead, it continuously determines the recommended
    optimization mode based on:

    - Focus goal
    - Active application
    - Battery level
    - Charging state
    - CPU utilization
    - Session duration
    """

    def __init__(self):

        self.current_mode = "BALANCED"
        self.reason = "Waiting for focus session"

        self.cpu_usage = 0.0
        self.last_update = 0

    # ============================================================
    # GOAL CLASSIFICATION
    # ============================================================

    def classify_goal(self, goal):

        if not goal:
            return "GENERAL"

        goal = str(goal).lower().strip()

        heavy_goals = {
            "verilog",
            "system verilog",
            "vivado",
            "simulation",
            "compilation",
            "fpga",
            "embedded",
            "c++",
            "cpp"
        }

        reading_goals = {
            "reading",
            "theory",
            "lecture",
            "research",
            "study"
        }

        coding_goals = {
            "coding",
            "programming",
            "python",
            "matlab",
            "dsa",
            "machine learning",
            "ml"
        }

        if goal in heavy_goals:
            return "HEAVY"

        if goal in reading_goals:
            return "READING"

        if goal in coding_goals:
            return "CODING"

        return "GENERAL"

    # ============================================================
    # APPLICATION CLASSIFICATION
    # ============================================================

    def classify_application(self, application):

        if not application:
            return "UNKNOWN"

        app = str(application).lower().strip()

        heavy_apps = {
            "vivado",
            "quartus",
            "modelsim",
            "questa",
            "matlab",
            "devenv",
            "code",
            "clion",
            "pycharm"
        }

        reading_apps = {
            "acrobat",
            "word",
            "onenote",
            "powerpnt"
        }

        browser_apps = {
            "chrome",
            "msedge",
            "firefox"
        }

        if app in heavy_apps:
            return "HEAVY"

        if app in reading_apps:
            return "READING"

        if app in browser_apps:
            return "BROWSER"

        return "GENERAL"

    # ============================================================
    # CPU UTILIZATION
    # ============================================================

    def get_cpu_usage(self):

        try:

            import psutil

            usage = psutil.cpu_percent(
                interval=0.1
            )

            self.cpu_usage = usage

            return usage

        except Exception:

            return self.cpu_usage

    # ============================================================
    # POWER STATUS
    # ============================================================

    def get_power(self):

        try:

            power = get_power_status()

            battery = power.get(
                "battery",
                "Unknown"
            )

            charging = power.get(
                "charging",
                False
            )

            return battery, charging

        except Exception:

            return "Unknown", False

    # ============================================================
    # MAIN OPTIMIZATION ENGINE
    # ============================================================

    def evaluate(
        self,
        goal="general",
        application="Unknown",
        session_minutes=0
    ):

        goal_type = self.classify_goal(
            goal
        )

        app_type = self.classify_application(
            application
        )

        battery, charging = self.get_power()

        cpu = self.get_cpu_usage()

        # --------------------------------------------------------
        # LOW BATTERY
        # --------------------------------------------------------

        if isinstance(battery, int):

            if battery <= 15 and not charging:

                self.current_mode = "BATTERY SAVER"

                self.reason = (
                    f"Battery critically low ({battery}%). "
                    "Reducing background workload."
                )

                return self._result(
                    battery,
                    charging,
                    cpu,
                    goal_type,
                    app_type
                )

            if battery <= 30 and not charging:

                self.current_mode = "BATTERY SAVER"

                self.reason = (
                    f"Battery at {battery}%. "
                    "Prioritizing battery life."
                )

                return self._result(
                    battery,
                    charging,
                    cpu,
                    goal_type,
                    app_type
                )

        # --------------------------------------------------------
        # HEAVY WORK + PLUGGED IN
        # --------------------------------------------------------

        if (
            charging
            and (
                goal_type == "HEAVY"
                or app_type == "HEAVY"
                or cpu >= 70
            )
        ):

            self.current_mode = "PERFORMANCE"

            self.reason = (
                "Heavy workload detected while "
                "the PC is plugged in."
            )

            return self._result(
                battery,
                charging,
                cpu,
                goal_type,
                app_type
            )

        # --------------------------------------------------------
        # HEAVY WORK ON BATTERY
        # --------------------------------------------------------

        if (
            goal_type == "HEAVY"
            or app_type == "HEAVY"
        ):

            self.current_mode = "BALANCED"

            self.reason = (
                "Heavy workload detected. "
                "Balancing performance and battery usage."
            )

            return self._result(
                battery,
                charging,
                cpu,
                goal_type,
                app_type
            )

        # --------------------------------------------------------
        # READING / THEORY
        # --------------------------------------------------------

        if goal_type == "READING":

            self.current_mode = "EFFICIENCY"

            self.reason = (
                "Reading or theory session detected. "
                "Prioritizing power efficiency."
            )

            return self._result(
                battery,
                charging,
                cpu,
                goal_type,
                app_type
            )

        # --------------------------------------------------------
        # NORMAL CODING
        # --------------------------------------------------------

        if goal_type == "CODING":

            self.current_mode = "BALANCED"

            self.reason = (
                "Normal coding/study workload. "
                "Maintaining balanced resource usage."
            )

            return self._result(
                battery,
                charging,
                cpu,
                goal_type,
                app_type
            )

        # --------------------------------------------------------
        # LONG SESSION
        # --------------------------------------------------------

        if session_minutes >= 90 and not charging:

            self.current_mode = "EFFICIENCY"

            self.reason = (
                "Long session detected while on battery. "
                "Prioritizing sustained battery life."
            )

            return self._result(
                battery,
                charging,
                cpu,
                goal_type,
                app_type
            )

        # --------------------------------------------------------
        # DEFAULT
        # --------------------------------------------------------

        self.current_mode = "BALANCED"

        self.reason = (
            "Normal workload detected."
        )

        return self._result(
            battery,
            charging,
            cpu,
            goal_type,
            app_type
        )

    # ============================================================
    # RESULT
    # ============================================================

    def _result(
        self,
        battery,
        charging,
        cpu,
        goal_type,
        app_type
    ):

        actions = []

        if self.current_mode == "PERFORMANCE":

            actions = [
                "Prioritize CPU performance",
                "Minimize unnecessary background workload",
                "Keep the system responsive for heavy tasks"
            ]

        elif self.current_mode == "EFFICIENCY":

            actions = [
                "Reduce unnecessary background activity",
                "Prioritize battery efficiency",
                "Maintain sufficient performance for the task"
            ]

        elif self.current_mode == "BATTERY SAVER":

            actions = [
                "Prioritize battery life",
                "Reduce background workload",
                "Avoid unnecessary high-performance activity"
            ]

        else:

            actions = [
                "Maintain balanced resource usage",
                "Preserve responsiveness",
                "Avoid unnecessary background workload"
            ]

        return {
            "mode": self.current_mode,
            "reason": self.reason,
            "actions": actions,
            "battery": battery,
            "charging": charging,
            "cpu": round(cpu, 1),
            "goal_type": goal_type,
            "application_type": app_type,
            "timestamp": time.time()
        }

    # ============================================================
    # HUMAN-READABLE DESCRIPTION
    # ============================================================

    def describe(self, result):

        if not result:
            return "No optimization data available."

        mode = result.get(
            "mode",
            "BALANCED"
        )

        reason = result.get(
            "reason",
            ""
        )

        return f"{mode}: {reason}"


# ================================================================
# DIRECT TEST
# ================================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("FOCUS OS ADAPTIVE OPTIMIZER")
    print("=" * 60)

    optimizer = AdaptiveOptimizer()

    test_cases = [

        {
            "goal": "verilog",
            "application": "vivado",
            "session_minutes": 45
        },

        {
            "goal": "reading",
            "application": "acrobat",
            "session_minutes": 30
        },

        {
            "goal": "coding",
            "application": "code",
            "session_minutes": 60
        },

        {
            "goal": "machine learning",
            "application": "chrome",
            "session_minutes": 45
        }
    ]

    for test in test_cases:

        result = optimizer.evaluate(
            goal=test["goal"],
            application=test["application"],
            session_minutes=test["session_minutes"]
        )

        print()
        print("-" * 60)

        print(
            "Goal:",
            test["goal"]
        )

        print(
            "Application:",
            test["application"]
        )

        print(
            "Mode:",
            result["mode"]
        )

        print(
            "Reason:",
            result["reason"]
        )

        print(
            "CPU:",
            result["cpu"],
            "%"
        )

        print(
            "Battery:",
            result["battery"]
        )

        print(
            "Charging:",
            result["charging"]
        )

        print("Actions:")

        for action in result["actions"]:
            print(
                "  •",
                action
            )
