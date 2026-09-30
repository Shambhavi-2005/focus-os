import re


class IntentEngine:
    """
    Focus OS Intent Engine

    Converts parsed voice commands into structured
    Focus OS actions.

    Designed so a local LLM can replace/augment this
    engine later without changing the rest of Focus OS.
    """

    def __init__(self):

        self.website_aliases = {

            "youtube": "youtube.com",
            "youtube.com": "youtube.com",

            "instagram": "instagram.com",
            "instagram.com": "instagram.com",

            "facebook": "facebook.com",
            "facebook.com": "facebook.com",

            "reddit": "reddit.com",
            "reddit.com": "reddit.com",

            "twitter": "twitter.com",
            "twitter.com": "twitter.com",

            "x": "x.com",
            "x.com": "x.com",

            "netflix": "netflix.com",
            "netflix.com": "netflix.com",

            "twitch": "twitch.tv",
            "twitch.tv": "twitch.tv",

            "github": "github.com",
            "github.com": "github.com",

            "stackoverflow": "stackoverflow.com",
            "stackoverflow.com": "stackoverflow.com"
        }

        self.focus_goals = {
            "verilog",
            "system verilog",
            "python",
            "c",
            "c++",
            "programming",
            "coding",
            "dsa",
            "data structures",
            "algorithms",
            "matlab",
            "machine learning",
            "digital electronics",
            "analog electronics",
            "electronics",
            "embedded",
            "embedded systems",
            "robotics",
            "research",
            "assignment",
            "project",
            "reading",
            "lecture",
            "study",
            "studying"
        }

    # =========================================================
    # MAIN ENTRY POINT
    # =========================================================

    def understand(self, parsed_command):

        if not parsed_command:

            return {
                "intent": "UNKNOWN",
                "confidence": 0.0
            }

        command = parsed_command.get(
            "command",
            "UNKNOWN"
        )

        if command == "START_SESSION":

            return self._start_session(
                parsed_command
            )

        if command == "ALLOW_WEBSITE":

            return self._allow_website(
                parsed_command
            )

        if command == "FOCUS_STATUS":

            return self._focus_status(
                parsed_command
            )

        if command == "STOP_SESSION":

            return self._stop_session(
                parsed_command
            )

        return {
            "intent": "UNKNOWN",
            "confidence": 0.0,
            "text": parsed_command.get(
                "text",
                ""
            )
        }

    # =========================================================
    # START SESSION
    # =========================================================

    def _start_session(self, command):

        duration = command.get(
            "duration"
        )

        goal = command.get(
            "goal",
            "General Focus"
        )

        if not goal:
            goal = "General Focus"

        goal = self.normalize_goal(
            goal
        )

        if duration is not None:

            try:
                duration = int(duration)

            except (TypeError, ValueError):
                duration = None

        confidence = 0.95

        if duration is None:
            confidence = 0.85

        return {
            "intent": "START_SESSION",
            "duration": duration,
            "goal": goal,
            "confidence": confidence,
            "source": "voice"
        }

    # =========================================================
    # WEBSITE ACCESS
    # =========================================================

    def _allow_website(self, command):

        website = command.get(
            "website",
            "unknown"
        )

        duration = command.get(
            "duration"
        )

        website = self.normalize_website(
            website
        )

        if duration is not None:

            try:
                duration = int(duration)

            except (TypeError, ValueError):
                duration = None

        confidence = 0.92

        if website == "unknown":
            confidence = 0.50

        return {
            "intent": "ALLOW_WEBSITE",
            "website": website,
            "duration": duration,
            "temporary": command.get(
                "temporary",
                True
            ),
            "reason": command.get(
                "reason",
                "user_requested"
            ),
            "confidence": confidence,
            "source": "voice"
        }

    # =========================================================
    # FOCUS STATUS
    # =========================================================

    def _focus_status(self, command):

        return {
            "intent": "FOCUS_STATUS",
            "confidence": 0.98,
            "source": "voice"
        }

    # =========================================================
    # STOP SESSION
    # =========================================================

    def _stop_session(self, command):

        return {
            "intent": "STOP_SESSION",
            "confidence": 0.98,
            "source": "voice"
        }

    # =========================================================
    # WEBSITE NORMALIZATION
    # =========================================================

    def normalize_website(self, website):

        if not website:
            return "unknown"

        website = (
            str(website)
            .lower()
            .strip()
        )

        website = website.rstrip(
            ".,!?;"
        )

        if website in self.website_aliases:

            return self.website_aliases[
                website
            ]

        if website.startswith("www."):

            website = website[4:]

        if "." not in website:

            return website + ".com"

        return website

    # =========================================================
    # GOAL NORMALIZATION
    # =========================================================

    def normalize_goal(self, goal):

        if not goal:
            return "General Focus"

        goal = (
            str(goal)
            .lower()
            .strip()
        )

        goal = re.sub(
            r"\s+",
            " ",
            goal
        )

        # Common Whisper errors
        corrections = {
            "readylog": "verilog",
            "verylog": "verilog",
            "very log": "verilog",
            "system very log": "system verilog"
        }

        if goal in corrections:

            goal = corrections[goal]

        for known_goal in sorted(
            self.focus_goals,
            key=len,
            reverse=True
        ):

            if known_goal in goal:

                return known_goal

        return goal

    # =========================================================
    # HUMAN-READABLE SUMMARY
    # =========================================================

    def describe(self, intent):

        if not intent:
            return "No intent detected."

        intent_type = intent.get(
            "intent"
        )

        if intent_type == "START_SESSION":

            duration = intent.get(
                "duration"
            )

            goal = intent.get(
                "goal",
                "General Focus"
            )

            if duration:

                return (
                    f"Start a {duration}-minute "
                    f"focus session for {goal}."
                )

            return (
                f"Start a focus session "
                f"for {goal}."
            )

        if intent_type == "ALLOW_WEBSITE":

            website = intent.get(
                "website",
                "unknown"
            )

            duration = intent.get(
                "duration"
            )

            if duration:

                return (
                    f"Allow {website} "
                    f"for {duration} minutes."
                )

            return (
                f"Allow {website}."
            )

        if intent_type == "FOCUS_STATUS":

            return (
                "Show the current Focus OS status."
            )

        if intent_type == "STOP_SESSION":

            return (
                "Stop the current focus session."
            )

        return "Command not understood."


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    engine = IntentEngine()

    tests = [

        {
            "command": "START_SESSION",
            "duration": 45,
            "goal": "Verilog"
        },

        {
            "command": "START_SESSION",
            "duration": 30,
            "goal": "Python"
        },

        {
            "command": "ALLOW_WEBSITE",
            "website": "YouTube",
            "duration": 15
        },

        {
            "command": "ALLOW_WEBSITE",
            "website": "GitHub",
            "duration": 10
        },

        {
            "command": "FOCUS_STATUS"
        },

        {
            "command": "STOP_SESSION"
        }
    ]

    print("=" * 60)
    print("FOCUS OS INTENT ENGINE TEST")
    print("=" * 60)

    for test in tests:

        result = engine.understand(
            test
        )

        print()
        print("Input:")
        print(test)

        print()
        print("Intent:")
        print(result)

        print()
        print("Description:")
        print(
            engine.describe(result)
        )

        print("-" * 60)