#!/usr/bin/env python3
"""
Serhant The Wall Check-In — Weekly reminder of what you're running from
Serhant says: "Know your Wall. It's your fuel."
Run every Monday morning or Sunday evening.
"""
import sys
from datetime import datetime

today = datetime.now()

walls = [
    "Your credit card was declined once. Don't let that happen again. EVER.",
    "Someone told you 'you can't do this.' Prove them wrong. Every. Single. Day.",
    "You've been broke. You know what that feels like. Keep running from it.",
    "There's a version of you that gave up. That guy is weak. You're not him.",
    "Your family counts on you. That's not pressure — that's purpose.",
    "The competition is outworking you right now. While you read this, they're dialing.",
]

wall = walls[today.weekday() % len(walls)]

msg = f"""🧱 **THE WALL CHECK-IN** 🧱
*Serhant says: Know your Wall. Distance yourself from it. Use it as fuel.*

**⛰️ YOUR WALL RIGHT NOW:**
___

**🔥 Remember:**
*"{wall}"*

**📏 How far are you from that Wall today?**
(1 = right against it, 10 = miles away)
___

**💪 What did you do THIS WEEK to push further from your Wall?**
___

**🎯 What will you do NEXT WEEK to keep running?**
___

---
*Serhant Secret #21: "When you don't get a deal, ask why. But some factors you can't control. Move on and go for other balls."*

Ready, set, GO! 🚀
"""
print(msg)
