#!/usr/bin/env python3
"""
Serhant Balls Up Weekly Scoreboard — Sunday review with tough love
Run every Sunday at 9PM for weekly performance review.
Output is suitable for Telegram delivery.
"""
import sys
from datetime import datetime, date

today = date.today()
week_num = today.isocalendar()[1]

# Weekly review quotes — Serhant tough love
grades = {
    "A": [
        "You're a selling machine. But machines need maintenance. What broke this week? Fix it.",
        "Shaun White already won before he hit the half-pipe. You rode like you'd already won this week. Now do it again.",
    ],
    "B": [
        "Good week. But good isn't great. What's ONE thing that would have made this an A week? Do that next week.",
        "You're juggling. But are you juggling enough? Add one more ball next week.",
    ],
    "C": [
        "You're coasting. You know who coasts? People who end up broke on the subway crying. Remember your Wall.",
        "Your approach is getting stale. Shake it up. Swap a listing. Try a new pitch. Do something DIFFERENT.",
    ],
    "F": [
        "STOP BEING A LITTLE BITCH. You've been doing this for how long? Suck it up. If your competitors can do it, you can too. Call someone who didn't hire you. RIGHT NOW.",
        "You dropped balls this week. Fine. But did you pick any back up? No? Then you're not a salesperson. You're a spectator. Ready, set, MOVE.",
    ]
}

msg = f"""📊 **BALLS UP WEEKLY SCOREBOARD**
Week {week_num} — {today.strftime("%b %d, %Y")}

**ДОЛОО ХОНОГИЙН ДҮН:**

🔵 Шинэ lead: ___
🔵 Follow-up илгээсэн: ___
🔵 Meeting/Show: ___
🔵 Close хийсэн: ___
🔵 Pipeline deals: ___
🔵 Унасан ball: ___
🔵 Орлого: ___

**🔥 SERHANT RATING:** __ (A/B/C/F)

**🏆 ЭНЭ ДОЛОО ХОНОГИЙН WIN:**
___

**💀 ХАМГИЙН ТОМ ALBATROSS (унасан ball):**
___

**🎯 ДАРАА ДОЛОО ХОНОГТ 1 ЗҮЙЛГЭРӨХ:**
___

**⚡ Gut Check:**
1. 1 deal унахад чамайг аврах 5 deal байна уу?
2. Cold lead-уудтайгаа хэзээ холбогдсон бэ?
3. Өнгөрсөн client-үүдээсээ referral асуусан уу?
4. Tomorrow's #1 priority тодорхой уу?

**⛔ What fence are you avoiding climbing?**
___

Ready, set, GO! 🚀
"""
print(msg)
