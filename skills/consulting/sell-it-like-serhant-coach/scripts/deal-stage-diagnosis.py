#!/usr/bin/env python3
"""
Serhant Deal Stage Diagnosis — Map your deal to the 7 Stages
Use this when a deal is stuck or you need coaching on a specific client.
Input: deal name + current situation
Output: stage + recommended tools
"""
import sys

STAGES = {
    1: {
        "name": "Excitement",
        "emoji": "🎉",
        "client_says": '"I love this!" "This is perfect!" "Oh my God"',
        "job": "Reinforce positives. Don't oversell. Don't rush. Let them fall in love naturally.",
        "warning": "Fear is coming next — prepare for it.",
        "tools": "Wow Moment, Store the excitement for later use",
    },
    2: {
        "name": "Frustration",
        "emoji": "😤",
        "client_says": '"Why is this taking so long?" "This isn\'t what I expected"',
        "job": "Empathy mode ON. 'We've all been there.' Don't argue. Validate their feelings.",
        "warning": "If you argue, they'll walk. Stay patient.",
        "tools": '"We\'ve All Been There", Listen first, Don\'t reply — respond',
    },
    3: {
        "name": "Fear",
        "emoji": "😨",
        "client_says": '"What if I find something better?" "Did I spend too much?" "Can I afford this?"',
        "job": "Assurance. 'We are in this together.' Remind them WHY they wanted this.",
        "warning": "This is where most deals die. The tornado has touched down.",
        "tools": '"We Are In This Together", Play the fears (Not Buying Wall), Element of Surprise',
    },
    4: {
        "name": "Disappointment",
        "emoji": "😞",
        "client_says": '"I should have waited" "I could have gotten a better deal"',
        "job": "Element of Surprise positive sandwich. Bad news → good news → relief.",
        "warning": "They might ghost you. Stay present. Keep communication open.",
        "tools": "Positive Sandwich, 'Someone paid more than you', Small wins",
    },
    5: {
        "name": "Acceptance",
        "emoji": "😌",
        "client_says": '"Well, I did it. Life is short."',
        "job": "Nudge toward close. They've made peace. Don't reopen the wound.",
        "warning": "One wrong word can push them back to stage 3.",
        "tools": "Calm confidence, Affirmation, Move forward fast",
    },
    6: {
        "name": "Happiness",
        "emoji": "🥳",
        "client_says": '"This is going to be AWESOME!"',
        "job": "ASK FOR REFERRALS NOW. Best time. They're floating.",
        "warning": "This window closes fast. Don't wait.",
        "tools": '"Who else needs what I sold you?" "Connect me to your friends"',
    },
    7: {
        "name": "Relief",
        "emoji": "😮‍💨",
        "client_says": '"Best decision I ever made" "I\'m so glad I did it"',
        "job": "Stay top-of-mind. Follow-back. Next deal starts here.",
        "warning": "Don't disappear! Closing is the BEGINNING of the relationship.",
        "tools": "F-3 Follow-back, Birthday emails, 'How's the product working?'",
    },
}

def diagnose(stage_num):
    s = STAGES.get(stage_num)
    if not s:
        return "❌ Wrong stage number (1-7)"
    
    return f"""🎯 **DEAL STAGE DIAGNOSIS: {s['emoji']} {s['name']} (Stage {stage_num}/7)**

**Client sounds like:** {s['client_says']}

**💼 Your job right now:** {s['job']}

**⚡ Tools to use:**
{s['tools']}

**⚠️ Warning:** {s['warning']}

---
*Map your deal to the right stage. Wrong tool = dead deal.*
"""
```

if __name__ == "__main__":
    try:
        stage = int(sys.argv[1]) if len(sys.argv) > 1 else None
    except:
        stage = None

    if stage:
        print(diagnose(stage))
        sys.exit(0)

import re
from pathlib import Path

# If asked via stdin
if not sys.stdin.isatty():
    query = sys.stdin.read().strip()
    if query.isdigit():
        print(diagnose(int(query)))
    else:
        # Try to detect stage from keywords
        q = query.lower()
        if any(w in q for w in ["love", "perfect", "amazing", "excited", "pumped"]):
            print(diagnose(1))
        elif any(w in q for w in ["frustrat", "annoy", "slow", "taking too long", "angry"]):
            print(diagnose(2))
        elif any(w in q for w in ["scared", "afraid", "overpay", "what if", "worried", "anxious"]):
            print(diagnose(3))
        elif any(w in q for w in ["disappoint", "regret", "should have", "remorse", "sad"]):
            print(diagnose(4))
        elif any(w in q for w in ["okay", "fine", "accept", "whatever"]):
            print(diagnose(5))
        elif any(w in q for w in ["happy", "awesome", "great", "can't wait", "refer"]):
            print(diagnose(6))
        elif any(w in q for w in ["relief", "glad", "good deal", "worth it"]):
            print(diagnose(7))
        else:
            print("🔍 Describe your client's current emotional state and I'll diagnose the stage.")
            print("Or pass a stage number (1-7) as an argument.")
