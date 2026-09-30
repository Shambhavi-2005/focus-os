class FocusEngine:

    def __init__(self):

        # Applications associated with productive work
        self.focused_apps = {
            "code",
            "devenv",
            "pycharm",
            "idea",
            "matlab",
            "notepad",
            "word",
            "excel",
            "powerpnt",
            "acrobat"
        }

        # Applications commonly associated with distractions
        self.distraction_apps = {
            "discord",
            "steam",
            "epicgameslauncher",
            "spotify"
        }

        # Websites commonly associated with focused work
        self.focused_domains = {
            "github.com",
            "gitlab.com",
            "stackoverflow.com",
            "stackexchange.com",
            "docs.google.com",
            "drive.google.com",
            "colab.research.google.com",
            "leetcode.com",
            "geeksforgeeks.org",
            "developer.mozilla.org",
            "w3schools.com"
        }

        # Websites commonly associated with distractions
        self.distraction_domains = {
            "youtube.com",
            "instagram.com",
            "facebook.com",
            "twitter.com",
            "x.com",
            "reddit.com",
            "netflix.com",
            "twitch.tv"
        }


    # =========================================================
    # APPLICATION EVALUATION
    # =========================================================

    def evaluate_app(self, application):

        if not application:
            return "UNKNOWN"

        app = application.lower().strip()

        if app in self.focused_apps:
            return "FOCUSED"

        if app in self.distraction_apps:
            return "DISTRACTION"

        return "UNKNOWN"


    # =========================================================
    # WEBSITE EVALUATION
    # =========================================================

    def evaluate_domain(self, domain):

        if not domain:
            return "UNKNOWN"

        domain = domain.lower().strip()

        # Remove www if present
        if domain.startswith("www."):
            domain = domain[4:]

        if domain in self.focused_domains:
            return "FOCUSED"

        if domain in self.distraction_domains:
            return "DISTRACTION"

        return "UNKNOWN"


    # =========================================================
    # COMBINED EVALUATION
    # =========================================================

    def evaluate(self, application, domain):

        app_status = self.evaluate_app(
            application
        )

        domain_status = self.evaluate_domain(
            domain
        )

        # Website gets priority when a browser is active
        if application.lower() in {
            "chrome",
            "msedge"
        }:

            if domain_status != "UNKNOWN":
                return domain_status

            return "UNKNOWN"

        # For normal desktop applications
        return app_status