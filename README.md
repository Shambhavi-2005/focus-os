# Focus OS

Technology Stack
Python
Tkinter — Desktop UI
Distil-Whisper / faster-whisper — Speech-to-text
Windows APIs — Active application and power-state detection
Chrome/Edge Extension — Browser domain awareness
JavaScript — Browser monitoring
Rule-based Intent Engine — Natural-language command interpretation
Adaptive Optimization Engine — Context-aware PC optimization

### An Adaptive, Privacy-First Productivity Layer for Snapdragon-Powered PCs

Focus OS is a context-aware productivity system designed for next-generation AI PCs.

Instead of simply blocking distracting applications and websites, Focus OS understands the user's **goal, active application, website, and system state** to provide adaptive focus assistance and PC optimization.

---

## 🚀 Key Features

### 🎯 Focus Sessions
- Start customizable focus sessions
- Set a specific goal such as Verilog, coding, reading, DSA, or research
- Automatic session timer and completion feedback
- Earn **Focus Coins** for completed focus time

### 🎙️ Voice Commands
Focus OS supports natural-language commands using **Distil-Whisper** for speech-to-text.

Example:

> "Start a 45-minute Verilog session."

The command is converted into a structured action by the Intent Engine.

Supported actions include:
- Start a focus session
- Stop a session
- Check focus status
- Temporarily allow a website

---

## 🧠 Focus Engine

The Focus Engine combines:

- Active Windows application
- Active browser domain
- User's session goal
- Session duration
- System state

Activities are classified as:

| Status | Meaning |
|---|---|
| 🟢 Focused | Activity supports the current task |
| 🔴 Distraction | Activity is likely unrelated to the task |
| ⚪ Unknown | Activity cannot be confidently classified |

For example:

**Goal:** Verilog

**Active application:** VS Code  
→ Focused

**Active website:** GitHub  
→ Focused

**Active website:** Instagram  
→ Distraction

**Active website:** YouTube  
→ Can be temporarily allowed when the user is watching a relevant tutorial.

---

## ⚡ Adaptive PC Optimization

Focus OS adapts the optimization strategy according to the user's workload.

### Performance
Used for heavy workloads such as:
- Verilog
- Coding
- Development

Actions:
- Prioritize CPU performance
- Minimize unnecessary background workload
- Maintain responsiveness

### Balanced
Used for normal study and productivity workloads.

Actions:
- Maintain balanced resource usage
- Preserve responsiveness
- Avoid unnecessary background workload

### Efficiency
Used for reading, theory, and lighter workloads.

Actions:
- Reduce unnecessary background activity
- Prioritize power efficiency
- Maintain sufficient performance

The optimizer considers:

```text
User Goal
    +
Active Application
    +
CPU Utilization
    +
Battery Level
    +
Charging State
    +
Session Duration
        ↓
Adaptive Optimization Mode
