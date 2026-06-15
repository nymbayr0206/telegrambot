#!/usr/bin/env python3
"""
Serhant Morning Kick — Daily Motivation + FKD Prompt
Run this every morning to get your mindset right.
Output is suitable for Telegram delivery.
"""
import sys
from datetime import datetime, date

today = date.today()
day_name = today.strftime("%A")

# Serhant-style rotation
quotes = [
    ("Ready, set, GO!", "Your morning should always start the night before. You ready?"),
    ("Choose success first — then back yourself into a career.", "Today is another day to climb. What are you selling TODAY?"),
    ("If I'm not growing, I'm dying.", "What's your growth move today? One call. One meeting. One follow-up."),
    ("From chaos comes sales.", "You create the chaos. You control the chaos. Now get after it."),
    ("Your hardest thing = do it FIRST.", "What's the one thing you're avoiding? Do that. Right now. 8am."),
    ("Sales is a volume business.", "How many balls are you juggling today? If it's less than 5, get more."),
    ("Don't wait for perfection. Do it NOW.", "You don't need the perfect pitch. You need ACTION."),
]

# Pick quote based on day of week
q = quotes[today.weekday()]

msg = f"""🔥 **SERHANT MORNING KICK** 🔥
{day_name.upper()} — {today.strftime("%b %d, %Y")}

"_{q[0]}_"

{q[1]}

⚡ **Today's FKD Plan:**
• **FINDER** — Хэдэн шинэ хүн танилцах вэ? ___
• **KEEPER** — Өнөөдөр ямар санхүүгийн шийдвэр гаргах вэ? ___
• **DOER** — Хэдэн meeting / follow-up / close? ___

🏀 **Balls Up Count:** Өнөөдөр хэдэн ball жонглёрлож байна? ___

📋 **3 Follow-up-аа нэрлэ:**
1. ___
2. ___
3. ___

Ready, set, GO! 🚀
"""
print(msg)
