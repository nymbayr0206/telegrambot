# Codex CLI Prompt: EspoCRM Bot Setup

Use this self-contained prompt with Codex CLI (`codex exec '...'`) to generate a Python bot that connects to the Dream Team CRM EspoCRM instance. The only variable per bot is `CRM_USERNAME`.

## Prompt Template

```
Build a Python CLI bot that connects to EspoCRM REST API for real estate operations.

## FIXED CONNECTION (same for all bots)
- Base URL: http://187.77.140.62:32769/api/v1
- API Key: e9a86a254bf03ff29c220e2c63c9b0f1
- Auth: X-Api-Key header
- Timezone: Asia/Ulaanbaatar (UTC+8)

## VARIABLE (change this per bot)
CRM_USERNAME = "hermes"

## STEPS

1. Lookup user ID: GET /User?filter[0][type]=equals&filter[0][attribute]=userName&filter[0][value]=CRM_USERNAME -> extract "id" field. All created records use this as assignedUserId.

2. CRUD Methods (all use requests library):

create_call(name, dateStart, durationMinutes, status="Held", direction, description, parentType, parentId):
  POST /Call - dateEnd IS REQUIRED, set it as dateStart + durationMinutes

create_lead(firstName, lastName, phoneNumber, description):
  POST /Lead - firstName=phone, lastName=district, phoneNumber MUST have +976 prefix, status="New", source="Call"

create_request(type, propertyType, fromBedroom, toBedroom, fromPrice, priceCurrency, description):
  POST /RealEstateRequest - currency fields: set BOTH fromPrice AND fromPriceCurrency in same request. Check Settings.currencyList for allowed currencies. If desired currency not available, omit price and store in description.

create_property(name, type, requestType, bedroomCount, price, priceCurrency, addressStreet, description):
  POST /RealEstateProperty - same currency rule: BOTH price AND priceCurrency

create_task(name, dateStart, status="Not Started", priority="Normal", parentType, parentId):
  POST /Task

find_matches():
  GET /RealEstateProperty - check matchingRequestCount
  GET /RealEstateRequest - check matchingPropertyCount
  Print properties that match open requests by type/bedrooms/district

get_today_tasks():
  GET /Task?filter[0][type]=today&filter[0][attribute]=dateStart&maxSize=20
  Print all tasks due today for this user

3. CLI Interface: python bot.py <command> [args]
Commands:
  call-inbound <phone> <name> <district> <notes>         # Log inbound call + create lead + request
  call-outbound <phone> <name> <notes>                    # Log outbound call
  add-request <type> <propertyType> <bedrooms> <notes>    # Create client request
  add-property <name> <type> <bedrooms> <price> <area>    # Create property listing
  add-task <name> <date>                                  # Create follow-up task
  today                                                    # Show today's tasks
  match                                                    # Find matches

## Entity field reference:
RealEstateProperty: name, type(Apartment/House/Land), requestType(Sale/Rent), status, bedroomCount, bathroomCount, price, priceCurrency, addressStreet, description, matchingRequestCount
RealEstateRequest: name(auto-numbered), type(Sale/Rent), propertyType, fromPrice/toPrice, fromPriceCurrency, fromBedroomCount/toBedroomCount, status, description, matchingPropertyCount
Call: name, dateStart, dateEnd, durationMinutes, status, direction(Inbound/Outbound), description, parentType, parentId, assignedUserId
Lead: firstName(phone), lastName(district), phoneNumber(+976...), status, source(Call), description
Task: name, dateStart, dateEnd, status, priority, parentType, parentId, assignedUserId

## Output
Create a single file: /opt/bot.py
Use Python + requests library. Make it production-ready with error handling.
Auto-lookup user ID on init from CRM_USERNAME.
```

## Usage

```bash
# For each bot container:
codex exec '...(paste the prompt above with CRM_USERNAME changed)...'
```

Change only `CRM_USERNAME = "..."` per bot. All other connection settings stay identical.
