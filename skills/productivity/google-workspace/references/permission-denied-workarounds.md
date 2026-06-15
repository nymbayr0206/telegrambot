# Permission-Denied Workarounds for Document Creation

When the Google Drive/Docs API is unavailable because the user's agent-level permission prompt was rejected (not a Google OAuth issue), use these fallbacks.

## Pattern: Creating a Google Doc from drafted content

1. **Draft the full content** (document text, formatting notes) in your response
2. **State what you need**: tell the user exactly what permission was needed (e.g., "Google Drive file creation permission") and ask them to re-approve the prompt
3. **Resubmit on approval**: once they say "yes," retry the exact same operation — don't start over, don't re-draft

## Workflow

```
1. User describes terms → you render a structured document (contract, agreement, etc.)
2. Try: create Google Doc via $GAPI docs create or Drive upload
3. If rejected (tool permission, not OAuth):
   a. Show the full document text in your response (save as plain text)
   b. Explain WHAT permission was blocked and WHERE the user should expect the prompt
   c. Offer options: (1) retry with approval, (2) receive as text to paste manually
4. On user's "yes" / re-approval → retry immediately
```

## Key Principles

- **Don't silently fail** — a rejected tool call means "the user needs to understand what's blocking." Explain what was needed (Drive write, local file create, etc.) and what the user should do (look for an Allow/Reject prompt).
- **Don't abandon the content** — if the document can't be created, present the full drafted text in your reply anyway. The user can copy-paste into Google Docs manually.
- **Don't re-draft** — once the content is written, cache it for retry. On approval, use it immediately.
- **For Google Drive, distinguish:**
  - *Tool-level rejection* (this reference): the agent/assistant itself was denied permission to call the Drive API. Fix: user approves the permission prompt.
  - *OAuth rejection* (google_token.json missing/expired): Google itself doesn't recognize the token. Fix: re-run OAuth setup (see main skill SKILL.md setup steps).
