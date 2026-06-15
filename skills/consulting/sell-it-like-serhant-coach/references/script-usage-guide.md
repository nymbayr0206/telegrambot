# Sell It Like Serhant — Script Usage Guide

## On-Demand Invocation

All scripts in `scripts/` output Telegram-formatted text to stdout. Run them directly:

```bash
python3 /path/to/skill/scripts/<name>.py
```

## Per-Script Details

### `morning-kick.py`
**When:** User says "morning kick", "start my day", "motivate me"
**Outputs:** Serhant quote of the day + FKD planner template + Balls Up count prompt
**No args needed**

### `evening-fkd-score.py`
**When:** User says "evening score", "end of day review", "FKD score"
**Outputs:** Daily self-assessment template — Finder/Keeper/Doer counts, balls dropped, win of the day
**No args needed**

### `weekly-balls-up.py`
**When:** User says "weekly review", "scoreboard", "balls up this week"
**Outputs:** 7-question weekly scoreboard with blank fields for user to fill in + Serhant-style gut check questions
**No args needed**

### `deal-stage-diagnosis.py`
**When:** User is stuck on a specific deal, asks "what stage is my client in"
**Two modes:**
1. By stage number: `python3 scripts/deal-stage-diagnosis.py 3` (prints Stage 3: Fear)
2. By text description (via stdin): `echo "my client keeps saying they're worried about overpaying" | python3 scripts/deal-stage-diagnosis.py`
   → Auto-detects "worried" + "overpaying" → Stage 3: Fear
3. No args: prints all 7 stages as a reference

### `the-wall-checkin.py`
**When:** User lacks motivation, feels stuck, needs "the Wall" reminder
**Outputs:** Weekly Wall reflection — what are you running FROM, how far are you now
**No args needed**
Changes Serhant quote rotation based on day of week

### `four-tenets-worksheet.py`
**When:** User needs to redefine their Why/Work/Wall/Win, or at quarterly/yearly reset
**Two modes:**
1. No args: prints Ryan's examples + blank fields for each tenet
2. `--fill`: prints a fill-in-the-blanks worksheet form

### `pipeline-review.py`
**When:** End of month, or user says "pipeline check", "how's my pipeline"
**Outputs:** Pipeline health assessment — hot/warm/cold counts, revenue coverage, Three F's audit, next month targets
**No args needed**

## Knowledge Base

Full book framework reference at `/opt/data/knowledge_bases/sell_it_like_serhant/README.md`
