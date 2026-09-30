
import re
import threading

import sounddevice as sd
from faster_whisper import WhisperModel


class VoiceEngine:

    def __init__(self, microphone_device=1):

        self.microphone_device = microphone_device
        self.sample_rate = 16000
        self.last_transcription = ""
        self.is_listening = False

        print("Loading local Whisper model...")

        self.model = WhisperModel(
            "base.en",
            device="cpu",
            compute_type="int8"
        )

        print("Whisper model ready.")

    # ============================================================
    # AUDIO RECORDING
    # ============================================================

    def record_audio(self, duration=8):

        print()
        print("=" * 55)
        print("🎤 Listening...")
        print("=" * 55)
        print()
        print(f"Speak now... ({duration} seconds)")

        try:

            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                device=self.microphone_device
            )

            sd.wait()

            return audio.flatten()

        except Exception as error:

            print("Microphone error:")
            print(error)

            return None

    # ============================================================
    # TRANSCRIPTION
    # ============================================================

    def transcribe(self, audio):

        if audio is None or len(audio) == 0:
            return ""

        print()
        print("Transcribing...")

        try:

            segments, info = self.model.transcribe(
                audio,
                language="en",
                beam_size=5,
                vad_filter=True,
                condition_on_previous_text=False
            )

            text_parts = []

            for segment in segments:

                text = segment.text.strip()

                if text:
                    text_parts.append(text)

            transcription = " ".join(
                text_parts
            ).strip()

            self.last_transcription = transcription

            print()
            print("Transcription:")
            print(transcription)

            return transcription

        except Exception as error:

            print("Whisper transcription error:")
            print(error)

            return ""

    # ============================================================
    # LISTEN
    # ============================================================

    def listen(self, duration=8):

        self.is_listening = True

        try:

            audio = self.record_audio(
                duration=duration
            )

            return self.transcribe(audio)

        finally:

            self.is_listening = False

    # ============================================================
    # ASYNC LISTENING
    # ============================================================

    def listen_async(self, callback, duration=8):

        if self.is_listening:
            return None

        def worker():

            result = self.listen(
                duration=duration
            )

            if callback:
                callback(result)

        thread = threading.Thread(
            target=worker,
            daemon=True
        )

        thread.start()

        return thread

    # ============================================================
    # TEXT NORMALIZATION
    # ============================================================

    def normalize_text(self, text):

        if not text:
            return ""

        # Convert to lowercase
        text = text.lower().strip()

        # Normalize punctuation
        text = text.replace("–", "-")
        text = text.replace("—", "-")
        text = text.replace("_", " ")

        # Remove unnecessary punctuation
        text = re.sub(
            r"[^\w\s.+#-]",
            " ",
            text
        )

        # Collapse multiple spaces
        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        # --------------------------------------------------------
        # COMMON WHISPER MISHEARINGS
        # --------------------------------------------------------

        replacements = {

            # -------------------------
            # VERILOG
            # -------------------------

            "readylog": "verilog",
            "ready log": "verilog",
            "very log": "verilog",
            "verylog": "verilog",
            "very long": "verilog",
            "veri log": "verilog",
            "veri-log": "verilog",
            "where log": "verilog",
            "where is log": "verilog",
            "very lock": "verilog",
            "verylock": "verilog",
            "veri lock": "verilog",
            "veri-lock": "verilog",
            "system very log": "system verilog",
            "system verilog": "system verilog",

            # -------------------------
            # DSA
            # -------------------------

            "data structures and algorithms": "dsa",
            "data structure and algorithms": "dsa",
            "data structures algorithms": "dsa",
            "data structure algorithms": "dsa",
            "data structures": "dsa",

            # -------------------------
            # MACHINE LEARNING
            # -------------------------

            "machine learning": "machine learning",
            "machine learn": "machine learning",
            "machine learnt": "machine learning",
            "machine learnings": "machine learning",
            "machinelearning": "machine learning",
            "ml": "machine learning",

            # -------------------------
            # C++
            # -------------------------

            "see plus plus": "c++",
            "c plus plus": "c++",
            "cplusplus": "c++",
            "c plus": "c++",

            # -------------------------
            # MATLAB
            # -------------------------

            "mat lab": "matlab",
            "matlab": "matlab",

            # -------------------------
            # PYTHON
            # -------------------------

            "pie thon": "python",
            "pie-thon": "python",
            "python": "python",

            # -------------------------
            # ECE
            # -------------------------

            "e c e": "ece",
            "e c": "ece",

            # -------------------------
            # GITHUB
            # -------------------------

            "get hub": "github",
            "git hub": "github",

            # -------------------------
            # STACK OVERFLOW
            # -------------------------

            "stack overflow": "stackoverflow",
            "stackover flow": "stackoverflow",

            # -------------------------
            # YOUTUBE
            # -------------------------

            "you tube": "youtube",
            "you-tube": "youtube",

            # -------------------------
            # INSTAGRAM
            # -------------------------

            "insta gram": "instagram",
            "insta": "instagram",

            # -------------------------
            # FACEBOOK
            # -------------------------

            "face book": "facebook",

            # -------------------------
            # REDDIT
            # -------------------------

            "read it": "reddit",
            "red it": "reddit",

            # -------------------------
            # TWITTER / X
            # -------------------------

            "ex dot com": "x.com",
            "x dot com": "x.com",

            # -------------------------
            # NVIDIA
            # -------------------------

            "in video": "nvidia",
            "en video": "nvidia",

            # -------------------------
            # ARDUINO
            # -------------------------

            "are we know": "arduino",
            "arduino": "arduino"
        }

        # Apply replacements repeatedly.
        # This allows multi-stage normalization.
        for _ in range(3):

            old_text = text

            for wrong, correct in replacements.items():

                text = re.sub(
                    r"\b" + re.escape(wrong) + r"\b",
                    correct,
                    text
                )

            if text == old_text:
                break

        # Normalize spaces again
        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        print()
        print("Normalized voice text:")
        print(text)

        return text

    # ============================================================
    # DURATION EXTRACTION
    # ============================================================

    def extract_duration(self, text):

        if not text:
            return None

        # Examples:
        # 45 minutes
        # 45 minute
        # 45 mins
        # 45 min
        # for 45
        # 45-minute

        patterns = [

            r"(\d+)\s*minutes?",
            r"(\d+)\s*mins?",
            r"(\d+)\s*min\b",
            r"for\s+(\d+)\b",

        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text
            )

            if match:

                try:

                    duration = int(
                        match.group(1)
                    )

                    # Keep duration reasonable
                    if 1 <= duration <= 1440:
                        return duration

                except ValueError:
                    pass

        return None

    # ============================================================
    # GOAL DETECTION
    # ============================================================

    def detect_goal(self, text):

        if not text:
            return "general"

        # Order matters.
        # More specific goals come first.

        goal_patterns = [

            # ----------------------------------------------------
            # VERILOG
            # ----------------------------------------------------

            (
                "verilog",
                [
                    "verilog",
                    "system verilog",
                    "systemverilog"
                ]
            ),

            # ----------------------------------------------------
            # DSA
            # ----------------------------------------------------

            (
                "dsa",
                [
                    "dsa",
                    "data structures",
                    "algorithms",
                    "algorithm"
                ]
            ),

            # ----------------------------------------------------
            # MACHINE LEARNING
            # ----------------------------------------------------

            (
                "machine learning",
                [
                    "machine learning",
                    "machine learn",
                    "ml"
                ]
            ),

            # ----------------------------------------------------
            # PYTHON
            # ----------------------------------------------------

            (
                "python",
                [
                    "python"
                ]
            ),

            # ----------------------------------------------------
            # C++
            # ----------------------------------------------------

            (
                "c++",
                [
                    "c++",
                    "cplusplus"
                ]
            ),

            # ----------------------------------------------------
            # C
            # ----------------------------------------------------

            (
                "c",
                [
                    " c "
                ]
            ),

            # ----------------------------------------------------
            # MATLAB
            # ----------------------------------------------------

            (
                "matlab",
                [
                    "matlab"
                ]
            ),

            # ----------------------------------------------------
            # ECE
            # ----------------------------------------------------

            (
                "electronics",
                [
                    "electronics",
                    "electronic"
                ]
            ),

            (
                "ece",
                [
                    "ece",
                    "electronics engineering"
                ]
            ),

            # ----------------------------------------------------
            # CODING
            # ----------------------------------------------------

            (
                "coding",
                [
                    "coding",
                    "code",
                    "programming",
                    "program"
                ]
            ),

            # ----------------------------------------------------
            # RESEARCH
            # ----------------------------------------------------

            (
                "research",
                [
                    "research",
                    "researching"
                ]
            ),

            # ----------------------------------------------------
            # STUDY
            # ----------------------------------------------------

            (
                "study",
                [
                    "study",
                    "studying",
                    "revision",
                    "revise"
                ]
            )
        ]

        for goal, patterns in goal_patterns:

            for pattern in patterns:

                if pattern in text:

                    return goal

        return "general"

    # ============================================================
    # WEBSITE DETECTION
    # ============================================================

    def detect_website(self, text):

        if not text:
            return None

        websites = {

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

        for spoken_name, domain in websites.items():

            if spoken_name in text:

                return domain

        return None

    # ============================================================
    # COMMAND PARSER
    # ============================================================

    def parse_command(self, text):

        if not text:

            return {
                "command": "UNKNOWN"
            }

        # Normalize first
        text = self.normalize_text(text)

        if not text:

            return {
                "command": "UNKNOWN"
            }

        # ========================================================
        # STOP SESSION
        # ========================================================

        stop_phrases = [

            "stop session",
            "end session",
            "finish session",
            "stop focus",
            "end focus",
            "finish focus",
            "cancel session",
            "cancel focus",

        ]

        if any(
            phrase in text
            for phrase in stop_phrases
        ):

            return {
                "command": "STOP_SESSION"
            }

        if text in {
            "stop",
            "end",
            "finish",
            "cancel"
        }:

            return {
                "command": "STOP_SESSION"
            }

        # ========================================================
        # FOCUS STATUS
        # ========================================================

        status_phrases = [

            "how focused am i",
            "how focused",
            "focus status",
            "am i focused",
            "what is my focus",
            "what's my focus",
            "check my focus",
            "check focus",
            "focus level",
            "focus score",
            "my focus status"

        ]

        if any(
            phrase in text
            for phrase in status_phrases
        ):

            return {
                "command": "FOCUS_STATUS"
            }

        # ========================================================
        # ALLOW WEBSITE
        # ========================================================

        allow_phrases = [

            "allow",
            "let me watch",
            "let me use",
            "allow me",
            "temporarily allow",
            "give me access",
            "allow access"

        ]

        if any(
            phrase in text
            for phrase in allow_phrases
        ):

            website = self.detect_website(
                text
            )

            duration = self.extract_duration(
                text
            )

            return {
                "command": "ALLOW_WEBSITE",
                "website": website,
                "duration": duration,
                "temporary": True,
                "reason": text
            }

        # ========================================================
        # START SESSION
        # ========================================================

        start_phrases = [

            "start",
            "begin",
            "beginning",
            "focus for",
            "start focusing",
            "start focus",
            "start a focus",
            "start my focus",
            "i want to focus",
            "let's focus",
            "lets focus",
            "focus on"

        ]

        if any(
            phrase in text
            for phrase in start_phrases
        ):

            duration = self.extract_duration(
                text
            )

            if duration is None:
                duration = 25

            goal = self.detect_goal(
                text
            )

            return {
                "command": "START_SESSION",
                "duration": duration,
                "goal": goal
            }

        # ========================================================
        # UNKNOWN
        # ========================================================

        return {
            "command": "UNKNOWN",
            "text": text
        }


# ================================================================
# DIRECT TEST
# ================================================================

if __name__ == "__main__":

    print()
    print("=" * 55)
    print("FOCUS OS VOICE ENGINE TEST")
    print("=" * 55)

    engine = VoiceEngine(
        microphone_device=1
    )

    transcription = engine.listen(
        duration=8
    )

    print()
    print("=" * 55)
    print("RESULT")
    print("=" * 55)

    print(
        "Transcription:",
        transcription
    )

    command = engine.parse_command(
        transcription
    )

    print()
    print("Parsed command:")
    print(command)

