# Drive Import as Google Doc (when Docs API is unavailable)

When the Google Docs API returns `HttpError 403: Google Docs API has not been used in project...`, you **cannot** use `docs create` or `docs append` commands. However, you can still create Google Docs by using the **Drive API's import feature** — upload a text/markdown file with `mimeType: application/vnd.google-apps.document`.

## Technique

The Drive API's `files.create` accepts a `mimeType` parameter telling it to convert the uploaded file into a native Google Doc. The source file can be plain text, markdown, HTML, or other supported formats.

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

creds = Credentials.from_authorized_user_file(
    '/path/to/google_token.json',
    ['https://www.googleapis.com/auth/drive']
)

drive = build('drive', 'v3', credentials=creds)

file_metadata = {
    'name': 'My Document Title',
    'mimeType': 'application/vnd.google-apps.document'
}

media = MediaFileUpload('/path/to/source.txt', mimetype='text/plain')
file = drive.files().create(
    body=file_metadata,
    media_body=media,
    fields='id,name,webViewLink'
).execute()

doc_id = file['id']
doc_url = file['webViewLink']
```

## Key Details

| Parameter | Value | Purpose |
|-----------|-------|---------|
| target `mimeType` | `application/vnd.google-apps.document` | Tells Drive to convert to Google Doc |
| source `mimetype` | `text/plain`, `text/markdown`, `text/html` | Format of your source file |
| `fields` | `id,name,webViewLink` | Returns the doc ID and editable URL |

## Limitations

- The resulting Doc has **no styling** by default — content appears as plain paragraphs
- To format the Doc (headings, bold, tables), you still need the Docs API (`docs.documents.batchUpdate`)
- However, the Doc is already accessible and editable via the Google Docs web UI at the `webViewLink`
- Markdown headings (`#`, `##`) are NOT converted to Google Docs headings — they remain as plain text

## When to Use This

1. **Docs API returns 403 (disabled)** — you can still create the doc and the user can edit it in the web UI
2. **User needs content delivered fast** — upload first, format later once Docs API is enabled
3. **Bulk doc creation from templates** — Drive import is faster than Docs API for simple documents

## Full Recipe: Create Doc with Content

```python
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_PATH = '/path/to/google_token.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
drive = build('drive', 'v3', credentials=creds)

# Write source content to temp file
source_path = '/tmp/doc_source.txt'
with open(source_path, 'w') as f:
    f.write("""Your document content here.
Multiple paragraphs work fine.
Each line becomes a paragraph in the doc.""")

# Upload as Google Doc
meta = {
    'name': 'Document Title',
    'mimeType': 'application/vnd.google-apps.document'
}
media = MediaFileUpload(source_path, mimetype='text/plain')
doc = drive.files().create(body=meta, media_body=media, fields='id,webViewLink').execute()

print(json.dumps({
    'documentId': doc['id'],
    'url': doc['webViewLink']
}))
```
