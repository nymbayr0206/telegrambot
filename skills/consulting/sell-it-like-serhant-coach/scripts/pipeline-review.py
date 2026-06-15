#!/usr/bin/env python3
"""
Serhant Pipeline Review — Monthly Balls Up check
Run on the last day of each month.
Assess pipeline health, deal counts, and revenue coverage.
"""
import sys
from datetime import datetime, date

today = date.today()
month = today.strftime("%B %Y")

msg = f"""📈 **MONTHLY PIPELINE REVIEW — {month}**
*Serhant: "Sales is a volume business. Balls Up."*

**🏀 CURRENT PIPELINE:**

🟢 Hot leads (daily contact): ___
🟡 Warm leads (weekly contact): ___
🔵 Cold leads (monthly contact): ___
⚪ Past clients (follow-back due): ___

**💰 REVENUE COVERAGE:**
• Target: ___
• Closed this month: ___
• Pipeline total value: ___
• Coverage ratio: ___x

**✅ THE THREE F'S AUDIT:**
• Follow-up: Last cold lead contacted on: ___
• Follow-through: Promises kept? Y/N ___
• Follow-back: Last past client reached: ___

**🔥 SERHANT GUT CHECK:**
1️⃣ If your biggest deal died today, would you survive? Y/N
2️⃣ Do you have 5+ active deals right now? Y/N
3️⃣ Have you asked for referrals this month? Y/N
4️⃣ Have you met 3+ new people every day? Y/N
5️⃣ Is your approach fresh or stale? ___

**🎯 NEXT MONTH'S TARGET:**
Revenue goal: ___
New leads needed: ___
Deals to close: ___

**💀 What's the ONE thing that WILL kill your pipeline if you don't fix it?**
___

---
*"If you want to have a successful sales track record, you must understand that sales is a volume business. It's that simple. If you want to make it, you have to sell more of your product than anyone else."*

Ready, set, GO! 🚀
"""
print(msg)
