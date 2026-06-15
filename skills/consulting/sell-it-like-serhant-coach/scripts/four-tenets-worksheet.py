#!/usr/bin/env python3
"""
Serhant Four Tenets Worksheet — Define your Why, Work, Wall, Win
Serhant: "If you do anything from this book, do this. It will change your life."
"""
import sys

TENETS = """
═══════════════════════════════════════════
  THE FOUR TENETS — SERHANT'S LIFE FRAMEWORK
═══════════════════════════════════════════

**TENET #1: THE WHY**
*Why do you do what you do?*

Ryan's WHY: "I'm a born competitor and sales has zero ceiling.
There is always more to reach for."

→ Ask yourself: What keeps you going when EVERYTHING goes wrong?
→ Your WHY must be powerful enough to sustain you on bad days.
→ It's not "to make money." Go deeper.

✍️ YOUR WHY: _________________________________

**TENET #2: THE WORK**
*What do you REALLY do every day?*

Ryan's WORK: "Every day is about working to expand my thriving
sales business. I must constantly seek new projects, discover new
strategies for marketing myself."

→ You're not selling a product. You're brokering people's wants and desires.
→ The real Work is bigger than opening doors and flipping light switches.

✍️ YOUR WORK: _________________________________

**TENET #3: YOUR WALL**
*What are you running FROM?*

Ryan's WALL: "Years ago — having my credit card declined at a grocery store.
Now — wasted potential. Leaving leftovers on the table."

→ What time in your life do you NEVER want to return to?
→ Bring that feeling to the surface. Let it fuel you.

✍️ YOUR WALL: _________________________________

**TENET #4: THE WIN**
*What are you doing this ALL for? The legacy.*

Ryan's WIN: "Changing the way people view sales so that everyone
will want to work in a job that offers limitless possibilities."

→ This is NOT a reward (car, suit, vacation). This is your LEGACY.
→ What do you want people to say about you when you're not in the room?

✍️ YOUR WIN: _________________________________

---
*"As long as I'm alive, I will do everything in my power to use every ounce of my potential."*
— Ryan Serhant

Ready, set, GO! 🚀
"""

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fill":
        print("""
=== FOUR TENETS — FILL THIS OUT ===

TENET #1: THE WHY
Why do I do what I do? (What keeps me going?)
→ 

TENET #2: THE WORK
What is my real Work? (Beyond the daily tasks)
→ 

TENET #3: MY WALL
What am I running from? (The moment I never want to return to)
→ 

TENET #4: THE WIN
What is my legacy? (What do I want to be remembered for?)
→ 
""")
    else:
        print(TENETS)
