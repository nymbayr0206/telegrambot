#!/usr/bin/env python3
"""
Serhant Evening FKD Score — Daily self-assessment closeout
Run this every evening (9PM) to track your day.
Output is suitable for Telegram delivery.
"""
import sys
from datetime import datetime, date

today = date.today()

# Random Serhant closer
closers = [
    "If you created the chaos today, you controlled it. If not — tomorrow's another shot.",
    "The closing is the BEGINNING of the relationship, not the end. What did you start today?",
    "Some balls fell today. That's fine. You still have others in the air. Keep juggling.",
    "Did you do the hardest thing first? If yes — you're ahead of 90% of salespeople. If no — why not?",
    "Remember: your Wall is still there. Keep running from it. Keep building your house.",
]

msg = f"""🌙 **SERHANT EVENING FKD SCORE** 🌙
{today.strftime("%b %d, %Y")}

**📊 ӨНӨӨДРИЙН ДҮН:**

🔍 **FINDER:** ___ шинэ хүн, ___ шинэ lead
💰 **KEEPER:** ___ ($/стратеги/төсөв)
⚙️ **DOER:** ___ (meeting/show/follow-up/close)

**🏀 BALLS UP:** ___ active deals
**✅ FOLLOW-UPS SENT:** ___
**❌ BALLS DROPPED:** ___
**🏆 WIN OF THE DAY:** ___

**🔥 Serhant Check:**
• "_{closers[today.day % len(closers)]}_"

**🌅 Tomorrow's #1 Priority:**
___

Ready, set, GO! 🚀
"""
print(msg)
