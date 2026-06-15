# CRM Leaderboard — Working Example

Used to rank real estate agents by calls, leads, opportunities, requests, and properties.

## Where it lives

| File | Path |
|------|------|
| Production script | `~/.hermes/scripts/leaderboard.sh` |
| Cron job ID | `66f3d661cb5d` (name: "leaderboard") |

## How to trigger

```python
# On demand:
cronjob(action="run", job_id="66f3d661cb5d")

# Auto schedule: daily 00:00 UTC = 08:00 Ulaanbaatar
# Already configured in the cron job above
```

## Script structure

1. **Fetch all entities**: User, Call, Lead, Opportunity, RealEstateRequest, RealEstateProperty
2. **Build agent dict** from User list — key all users by ID
3. **Count metrics** per user:
   - Calls → count by `assignedUserId`
   - Leads → count by `createdById`
   - Opportunities + total value → count + sum `amount` by `createdById`
   - Requests → count by `createdById`, check `status=="New"` for active count
   - Properties → count by `createdById`, check `status in ("New", "Assigned")` for active count
4. **Compute score**: `calls*10 + leads*15 + opportunities*25 + requests*5 + properties*5`
5. **Sort descending** by score, format with Telegram markdown and emoji

## Known entities at this CRM instance

| Entity | API path | Records | Key field |
|--------|----------|---------|-----------|
| User | /User | 3 (admin + agent + api) | id, type, isActive |
| Call | /Call | 6 | assignedUserId, direction |
| Lead | /Lead | 4 | createdById, status |
| Opportunity | /Opportunity | 1 | createdById, amount |
| RealEstateRequest | /RealEstateRequest | 4 | createdById, status |
| RealEstateProperty | /RealEstateProperty | 4 | createdById, status |

## Pitfalls

- Records created by the API (via `X-Api-Key`) have `createdById` pointing to an `api`-type user, not a real agent
- The "Leaderboard" UI tab in EspoCRM Settings is NOT a real API entity — `GET /api/v1/Leaderboard` returns 404
- Calls are tracked by `assignedUserId` (the agent who made the call), but other entities use `createdById`
- Some records may be unassigned (`assignedUserId: null`) — they still count toward `createdById`
- The `admin` type user is the CRM owner (Battushig); real agents are `regular` type
- Opp value: `Opportunity.amount` field — always check `amountCurrency` for currency context
