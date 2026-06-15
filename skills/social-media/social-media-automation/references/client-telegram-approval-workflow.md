# Client Telegram Approval Workflow

When the user has clients who need to review and approve generated social content before publishing, use this Telegram-based approval pattern.

## Architecture

- **One shared bot** — the same @HermesAgent_bot handles both the user and their clients
- **Client identification** — each client is identified by their Telegram user ID or @username
- **Brand mapping** — each client is associated with one or more brand workspaces
- **Approval routing** — content approval responses are sent back to the agent; the user is notified of the outcome

## Prerequisites

- `telegram.allowed_chats` in `config.yaml` must be empty (`''`) — empty = all chats allowed. If restricted, new clients cannot reach the agent.
- The user must introduce each client first so the agent knows the mapping.

## Registration Pattern

When the user says something like: "This is my client for AI Global, his Telegram is @client_name":

1. Store the mapping in memory: `Client @client_name → brand(s)`
2. Ask the user for the client's full name and any context about their approval authority
3. Confirm: "I'll recognize @client_name as the reviewer for AI Global content."

## Sending Content for Client Approval

1. Generate the content as usual (carousel, video, etc.) under the brand's workspace
2. Identify the client's Telegram chat ID (the one the client used to message the bot)
3. Send a preview via `send_message(target="telegram:<chat_id>", message="...")` 
4. Include: the asset(s) as media, a short description, and clear approval options

### Approval Prompt Template

```
👋 Сайн уу, [Client Name]!

[Brand] -ийн шинэ контент бэлэн боллоо:

[Topic/Title]
[Format: 4-slide carousel / Reel video / Post]

Харж үзээд батална уу:
✅ /approve — нийтлэхэд бэлэн
🔁 /revise — засвар хийх
❌ /cancel — цуцлах

Эсвэл сэтгэгдэл бичиж болно.
```

## Client Response Handling

| Client Response | Action |
|---|---|
| `approve`, `zuvshuurluu`, `approved`, `yes`, `✅` | Publish content (Make.com webhook or direct post). Notify user: "[Client] approved [brand] [content]." |
| `revise`, `zasvarlah`, `change`, `edit`, `not quite` | Ask for specifics: "What would you like changed?" Then regenerate, re-preview, re-send. |
| `cancel`, `cancel`, `delete` | Archive content (move to `canceled/` subfolder). Notify user: "[Client] canceled [brand] [content]." |
| Free-form feedback | Parse for actionable edits. Apply and re-preview. |

## Notifying the User

After the client responds, always inform the user (not just the client):

- On approve: *"✅ [Client] approved [brand] carousel/video. Published via Make.com."*
- On revise: *"🔄 [Client] requested changes to [brand] content. Asking for specifics."*
- On cancel: *"❌ [Client] canceled [brand] content. Archived."*

## Edge Cases

- **Client hasn't messaged the bot yet** — the agent has no chat context for them. Ask the user to have the client send any message to @HermesAgent_bot first, then retry.
- **Multiple clients for one brand** — store as a list. Send to all reviewers; first "approve" or "cancel" wins.
- **Client sends unrelated messages** — treat every message from a known client as a potential approval. If ambiguous, ask.
- **Client mentions a different brand** — check if they're mapped to multiple brands. Ask for clarification.
