# Technical Writer Agent Guide
## Best Practices, Examples, and Anti-Patterns

---

## 1. Core Principles of Technical Writing

### The Foundation
Technical writing serves to **communicate complex information clearly, concisely, and accurately** to a specific audience. It prioritizes:
- **Clarity** - Easy to understand
- **Accuracy** - Factually correct
- **Concision** - No unnecessary words
- **Organization** - Logical flow
- **Accessibility** - Appropriate for audience level

---

## 2. Audience Analysis

### ✅ GOOD: Audience-Specific Writing

**For Developers (API Documentation):**
```
Authentication uses JWT tokens with a 30-minute expiration. Include the token 
in the Authorization header:

Authorization: Bearer <your_jwt_token>

Example:
curl -H "Authorization: Bearer eyJhbGc..." https://api.example.com/users
```

**Why it's good:**
- Provides concrete example with real header format
- Shows actual API endpoint
- Includes working code snippet
- Assumes technical knowledge

---

**For Non-Technical Users (User Guide):**
```
To add a new client:

1. Click the "New Client" button (top right corner)
2. Fill in the client name and contact email
3. Click "Save"

Your client is now created and can be assigned to projects.
```

**Why it's good:**
- Step-by-step format
- Uses button labels (what they see)
- No technical jargon
- Explains the outcome

---

### ❌ BAD: Generic/Wrong Audience

```
The system instantiates a client object and persists it to the relational database 
via asynchronous ORM operations, triggering webhook events for downstream consumer 
microservices.
```

**Why it's bad:**
- Unclear who this is for (developer? manager? user?)
- Jargon-heavy without explanation
- No actionable steps
- No concrete example
- Assumes advanced knowledge of entire architecture

---

## 3. Clarity & Concision

### ✅ GOOD: Clear and Concise

**Original (68 words - unclear):**
```
It is important to note that the system has the capability to handle, process, 
and manage multiple types of invoicing scenarios including but not limited to 
recurring invoices, one-time invoices, and invoices that may be subject to 
various tax conditions and special payment terms.
```

**Revised (18 words - clear):**
```
The system handles recurring invoices, one-time invoices, and invoices with 
custom tax and payment terms.
```

**Why the revision is better:**
- Cut 73% of the words
- Removed redundancy ("handle, process, and manage" → just state facts)
- Removed qualifiers ("important to note," "capability to")
- Direct subject-verb-object structure
- Still conveys all essential information

---

### ❌ BAD: Verbose & Unclear

```
In accordance with the operational requirements and business logic that have been 
established and defined within the system architecture documentation, there exists 
a requirement that necessitates the necessity for users to ensure that at such 
time as they are initiating the process of creating an invoice, the aforementioned 
users must verify and validate that all of the required fields are appropriately 
and completely filled in with valid data.
```

**Why it's bad:**
- 67 words to say: "When creating an invoice, fill in all required fields"
- Circular language ("necessity for the need")
- Passive voice ("there exists a requirement")
- Multiple qualifiers and hedges
- Obfuscates simple concept

---

## 4. Active vs. Passive Voice

### ✅ GOOD: Active Voice (Direct & Clear)

```
The system validates the invoice amount before sending it to the client.
```

vs.

```
Before the invoice is sent to the client, validation of the invoice amount 
is performed by the system.
```

**Active version is better because:**
- Identifies who/what takes action (subject: "system")
- More concise (10 words vs. 17 words)
- Clearer cause-and-effect
- Easier to scan

---

### ❌ BAD: Excessive Passive Voice

```
It was determined by the engineering team that improvements could be made to 
the performance metrics. These improvements were implemented, and a reduction 
in latency was observed by the operations team.
```

**Why it's bad:**
- Hides who did what
- Wordy and hard to follow
- Weak action verbs ("was determined," "was observed")
- Readers must mentally convert to active

**Better (Active):**
```
The engineering team improved performance and reduced latency.
```

---

## 5. Technical Jargon Handling

### ✅ GOOD: Define or Avoid Jargon

**Option 1 - Define on first use:**
```
The API uses JWT (JSON Web Tokens) for authentication. JWTs are encoded strings 
that contain user information and expire after 30 minutes.
```

**Option 2 - Provide context:**
```
To authenticate requests, include a token in the Authorization header. The token 
expires after 30 minutes, so you'll need to request a new one when making 
subsequent calls.
```

**Option 3 - Use analogy for non-technical audience:**
```
A JWT token works like a concert ticket. It proves you've paid and are allowed 
entry. After the concert (30 minutes), the ticket expires and you need a new one.
```

---

### ❌ BAD: Unexplained Jargon

```
The CORS policy must be configured to whitelist your domain in the 
preflight CSRF validation middleware. Ensure your Content-Type header 
is application/json to avoid CORS preflight requests due to custom headers.
```

**Why it's bad:**
- Multiple undefined terms (CORS, CSRF, preflight, middleware, whitelisting)
- Assumes reader knows all these concepts
- No explanation of why these matter
- Creates confusion rather than clarity

**Better:**
```
To allow your website to access our API:

1. We need to know which websites can access our API (your domain)
2. Send requests with Content-Type: application/json
3. This prevents a security check that would slow down your requests

Contact us to add your domain to our allowed list.
```

---

## 6. Structure & Organization

### ✅ GOOD: Logical Organization

**API Endpoint Documentation:**
```
## POST /api/v1/invoices

Create a new invoice for a client.

### Request
Content-Type: application/json

```json
{
  "client_id": "c123",
  "amount": 5000,
  "due_date": "2024-03-15",
  "description": "Website redesign services"
}
```
```

### Response (201 Created)
```json
{
  "id": "inv456",
  "client_id": "c123",
  "status": "draft",
  "created_at": "2024-02-02T10:30:00Z"
}
```
```

### Error Responses
- 400 Bad Request - Invalid client_id
- 401 Unauthorized - Missing authentication token
- 422 Validation Error - Amount must be positive number

### Example

## Creating an invoice
curl -X POST https://api.example.com/api/v1/invoices \
  -H "Authorization: Bearer token123" \
  -H "Content-Type: application/json" \
  -d '{"client_id":"c123","amount":5000}'
```
```

**Why it's good:**
- Clear heading hierarchy
- Request/response separated
- Error codes with explanations
- Concrete example at the end
- Easy to scan and find information

---

### ❌ BAD: Disorganized Documentation

```
This API endpoint creates invoices and is located at the v1 path and 
accepts POST requests. You can pass a client ID, amount, due date and 
description. It returns an invoice object with an ID and status and 
other fields. If there's an error it might return a 400 or 401 or 422. 
The client ID must be valid. The amount must be greater than zero. Here's 
an example: POST /api/v1/invoices with {"client_id":"c123","amount":5000}. 
If it works you get back {"id":"inv456","status":"draft"}.
```

**Why it's bad:**
- No structure or hierarchy
- Mixes request, response, and errors together
- No proper formatting
- Hard to find specific information
- Error codes buried without explanation
- Example not separated or properly formatted

---

## 7. Examples & Code Samples

### ✅ GOOD: Complete, Runnable Examples

```markdown
## Example: Calculate Project Profitability

This example shows how to get all invoices for a project and calculate 
total revenue.

### Python

```python
import requests

# Get all invoices for project ID p789
response = requests.get(
    'https://api.example.com/api/v1/invoices',
    params={'project_id': 'p789'},
    headers={'Authorization': 'Bearer your_token'}
)

invoices = response.json()['items']

# Calculate total revenue
total_revenue = sum(inv['amount'] for inv in invoices if inv['status'] == 'paid')
print(f"Total Revenue: ${total_revenue}")
```
```

### cURL

```bash
curl -H "Authorization: Bearer your_token" \
  "https://api.example.com/api/v1/invoices?project_id=p789" | \
  jq '[.items[] | select(.status=="paid") | .amount] | add'
```
```

**Why it's good:**
- Real-world use case (profitability calculation)
- Multiple languages (Python + cURL)
- Shows authentication
- Shows parameter usage
- Shows filtering/processing data
- Can be copied and run

---

### ❌ BAD: Incomplete or Wrong Examples

```
To get invoices, use the GET endpoint with the project_id parameter. 
Here's code:

get("/invoices")
```

**Why it's bad:**
- Missing authentication
- Wrong HTTP method notation
- No parameter shown
- No endpoint URL
- Pseudocode that won't run
- No explanation of what it does
- Can't be copied and used

---

## 8. Error Messages & Troubleshooting

### ✅ GOOD: Helpful Error Documentation

```
### 401 Unauthorized

**What this means:** Your authentication token is missing, invalid, or expired.

**Common causes:**
1. Authorization header not included in request
2. Token was not copied completely
3. Token expired (tokens expire after 30 minutes)
4. Token is for a different environment (staging vs. production)

**How to fix:**
1. Verify Authorization header is present:
   Authorization: Bearer <your_token>

2. Get a new token by logging in:
   POST /api/v1/auth/login

3. If still failing, check the token timestamp in the response body.

**Example:**
Before (missing token):
GET /api/v1/invoices

After (with token):
GET /api/v1/invoices
Authorization: Bearer eyJhbGc...
```

**Why it's good:**
- Explains the error clearly
- Lists most common causes
- Provides step-by-step solutions
- Includes examples
- Differentiates between environment types
- Actionable steps

---

### ❌ BAD: Vague Error Documentation

```
401: Unauthorized

This error occurs when you don't have permission. Check your credentials.
```

**Why it's bad:**
- Doesn't explain what "credentials" means (token? username/password?)
- No troubleshooting steps
- No examples
- No common causes listed
- How do you "check" credentials?
- Reader is left confused

---

## 9. Lists & Procedures

### ✅ GOOD: Clear Step-by-Step

```
## Setting Up API Access

### Prerequisites
- [ ] You have a registered account
- [ ] You have admin access to your account
- [ ] You have curl or Postman installed (for testing)

### Steps

1. **Log in to your dashboard**
   Go to https://dashboard.example.com and enter your credentials

2. **Navigate to API Settings**
   Click your username (top right) → Settings → API Keys

3. **Create a new API key**
   Click "Generate New Key"
   - Name: "Development" (or your preferred name)
   - Environment: "Sandbox" (for testing)
   - Click "Create"

4. **Copy your API key**
   Your key appears on screen. Copy it immediately—you won't see it again.

5. **Test your key**
   ```bash
   curl -H "Authorization: Bearer your_key_here" \
     https://api.example.com/api/v1/health
   ```
   
   You should see: `{"status": "healthy"}`

### What's next?
Now you can start making API calls. See [Making Your First Request](./first-request.md).
```

**Why it's good:**
- Numbered steps (easy to follow)
- Prerequisite checklist
- Action verb starts each step ("Log in," "Navigate," "Create")
- Sub-bullets for context
- Exact UI labels ("your username," "Settings")
- Verification step at end
- Links to next steps
- Progressive disclosure (one thing per step)

---

### ❌ BAD: Confusing Instructions

```
To set up API access, you need to log in and go to settings where you can 
find API keys. Make sure you have admin access. Generate a new key in sandbox 
mode. Copy it and use it in the authorization header when making requests. 
You might need to test it first. The endpoint is /api/v1/health. If it works 
you'll get a response. Then you're ready to use the API.
```

**Why it's bad:**
- Run-on sentences
- No visual structure
- Steps not clearly delineated
- No "how to verify" step
- Missing exact UI navigation
- Unclear prerequisites
- No links to next resources
- Reader must mentally parse what to do

---

## 10. Visual Formatting

### ✅ GOOD: Effective Use of Formatting

```markdown
## Rate Limiting

Our API enforces rate limits to ensure fair usage.

| Tier | Requests/Minute | Best For |
|------|-----------------|----------|
| Free | 60 | Development & testing |
| Pro | 300 | Production applications |
| Enterprise | Custom | High-volume operations |

### How Rate Limiting Works

When you exceed your limit:
1. You receive a **429 Too Many Requests** response
2. Response includes `Retry-After` header (wait time in seconds)
3. Your request counter resets each minute

### Example Response

```json
HTTP/1.1 429 Too Many Requests
Retry-After: 45
Content-Type: application/json

{
  "error": "Rate limit exceeded",
  "retry_after": 45,
  "current_minute_requests": 301
}
```

### Best Practices

✅ **Do:**
- Implement exponential backoff for retries
- Cache responses when possible
- Batch requests to reduce API calls

❌ **Don't:**
- Ignore Retry-After header
- Make requests in a tight loop
- Request same data multiple times per second
```

**Why it's good:**
- Table for comparison
- Clear numbered explanation
- Code blocks for JSON
- ✅/❌ checklist for best practices
- Real example response
- Specific, actionable guidance

---

### ❌ BAD: Poor Formatting

```
Rate limiting is when we limit how many requests you can make. There's a free 
tier with 60 requests per minute and a pro tier with 300 and enterprise is custom. 
If you go over the limit you get a 429 error and you should wait before trying 
again. The response tells you how long to wait. You should implement backoff logic 
and cache responses. Don't make a lot of requests really fast. You can batch requests 
to use fewer API calls.
```

**Why it's bad:**
- No table or structure
- Information scattered throughout paragraph
- No code example
- No distinction between error response format
- No visual emphasis on important points
- Hard to scan or reference

---

## 11. Common Technical Writing Mistakes

### ❌ MISTAKE 1: Assuming Too Much Knowledge

**Bad:**
```
Initialize the ORM with async connection pooling and configure the SQLAlchemy 
session maker with scoped_session to manage transaction context propagation.
```

**Better:**
```
To use the database:

1. Create a connection pool (manages multiple database connections)
2. Create a session manager (handles database transactions)

This ensures your application can handle multiple simultaneous requests safely.
```

---

### ❌ MISTAKE 2: Over-Explaining Obvious Points

**Bad:**
```
The word "GET" is an HTTP method. HTTP stands for HyperText Transfer Protocol. 
It is a protocol used for transferring data on the web. GET is used to retrieve 
data. When you retrieve data, you are requesting information from the server.
```

**Better:**
```
Use GET to retrieve data from the server.
```

---

### ❌ MISTAKE 3: Mixing Multiple Audiences

**Bad (mixing beginner and expert):**
```
To configure CORS, you'll need to whitelist your domain in the middleware 
configuration by modifying the CORS_ORIGINS environment variable with a 
comma-separated list of fully qualified domain names that corresponds to 
your service deployments.
```

**Better for beginners:**
```
Tell us which websites can access your API:

Set the CORS_ORIGINS variable to your domain:
CORS_ORIGINS=https://myapp.com,https://staging.myapp.com
```

**Better for experts:**
```
Configure CORS_ORIGINS in .env:
CORS_ORIGINS=https://myapp.com,https://staging.myapp.com

The API will reject requests from other domains.
```

---

### ❌ MISTAKE 4: Not Providing Context

**Bad:**
```
Call the endpoint with a POST request and include the required parameters.
```

**Better:**
```
To create a new invoice, POST to /api/v1/invoices with these parameters:

- client_id (required): The ID of the client being billed
- amount (required): Invoice total in cents (e.g., 5000 = $50.00)
- due_date (optional): Payment due date in YYYY-MM-DD format
```

---

### ❌ MISTAKE 5: No Error Handling Documentation

**Bad:**
```
Get all clients with GET /api/v1/clients
```

**Better:**
```
Get all clients with GET /api/v1/clients

**Response (200 OK):**
Returns a list of client objects

**Possible Errors:**
- 401 Unauthorized: Missing or invalid authentication token
- 500 Server Error: Internal server error (contact support)
```

---

## 12. Technical Writing Checklist

### Before Publishing

- [ ] **Audience identified** - Who is this for? (beginners, experts, both?)
- [ ] **Jargon explained** - Every technical term defined or avoided
- [ ] **Active voice** - Subjects perform actions (not passive sentences)
- [ ] **Concise** - No unnecessary words (can I cut 20%?)
- [ ] **Examples included** - Code samples, screenshots, or walkthroughs
- [ ] **Steps numbered** - Procedures are sequential with clear steps
- [ ] **Errors documented** - Common problems and solutions listed
- [ ] **Scanned easily** - Headings, lists, and formatting aid scanning
- [ ] **Accurate** - Tested code examples, current information
- [ ] **Organized** - Logical flow from simple to complex
- [ ] **Verified links** - All cross-references are current
- [ ] **No assumptions** - Don't assume reader knows prerequisites
- [ ] **Readable format** - Proper grammar, short sentences, clear language
- [ ] **Actionable** - Reader knows what to do after reading

---

## 13. Template Examples

### API Documentation Template

```markdown
## Endpoint Name

Brief description of what this endpoint does.

### HTTP Method & Path
POST /api/v1/resource

### Authentication
Required: Bearer token in Authorization header

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | Yes | Resource name |
| status | string | No | Resource status (active, inactive) |

### Request Example
```json
{
  "name": "Example",
  "status": "active"
}
```
```

### Response
**Status 201 Created**
```json
{
  "id": "res123",
  "name": "Example",
  "status": "active",
  "created_at": "2024-02-02T10:30:00Z"
}
```

### Error Responses
- 400 Bad Request - Invalid parameters
- 401 Unauthorized - Missing authentication
- 422 Validation Error - name field required

### Common Use Case
[Describe when/why to use this endpoint]
```

---

### Setup Guide Template

```markdown
## Getting Started: [Feature Name]

### What You'll Learn
- How to [action 1]
- How to [action 2]
- How to [action 3]

### Prerequisites
- [ ] Item 1
- [ ] Item 2
- [ ] Item 3

### Step 1: [First Action]
Explanation of this step...

```
code example
```

What you should see:
> Expected output

### Step 2: [Second Action]
...

### Verification
To confirm it's working:
```
verification command
```

### Next Steps
- [Link to advanced feature]
- [Link to troubleshooting]
- [Link to examples]
```

---

## 14. Real-World Example: Before & After

### BEFORE (Poor Technical Writing)

**Title:** API Documentation

```
The API provides various endpoints that can be used to interact with the system. 
Authentication is required for most endpoints and uses JWT tokens. Requests should 
be made to https://api.example.com/api/v1/. 

There are resources like clients, projects, timesheets, and invoices. You can 
perform CRUD operations on these resources. The response format is JSON. Error 
responses will indicate what went wrong.

To get started, you'll need an API key. You can generate one from the dashboard. 
Then include it in requests like Authorization: Bearer token. 

Here's a quick example:
curl https://api.example.com/api/v1/clients

This will return a list of clients if you're authenticated. If you get a 401 error, 
it means your token is wrong or missing.

The rate limit is 60 requests per minute for free tier. The endpoints have different 
methods like GET for retrieving, POST for creating, PUT for updating, and DELETE for 
deleting. Parameters can be passed in the URL or in the request body depending on the 
method.

For more information see the full documentation.
```

---

### AFTER (Good Technical Writing)

**Title:** Getting Started with the API

```markdown
## Welcome to the Votra.io API

The API lets you automate your consulting workflow—manage clients, projects, 
timesheets, and invoices programmatically.

**What you can do:**
- Create and manage clients
- Track projects and budgets
- Log time entries
- Generate invoices and payments
- Pull business reports

**API Base URL:** `https://api.example.com/api/v1`

---

## 1. Get an API Key

1. Log in to [your dashboard](https://dashboard.example.com)
2. Click **Settings** (top right) → **API Keys**
3. Click **Generate New Key**
4. Name it (e.g., "Development") and select environment
5. **Copy the key immediately**—you won't see it again

---

## 2. Make Your First Request

Every request needs your API key in the Authorization header:

```bash
curl -H "Authorization: Bearer your_key_here" \
  https://api.example.com/api/v1/clients
```

**Success response:**
```json
{
  "items": [
    {
      "id": "c123",
      "name": "Client Name",
      "email": "contact@client.com"
    }
  ],
  "total": 1
}
```

**Common errors:**
- `401 Unauthorized` → Token missing or expired. Generate a new one.
- `403 Forbidden` → Your token doesn't have permission for this action.
- `429 Too Many Requests` → You've exceeded the rate limit (60 req/min).

---

## 3. Common Tasks

### Get a Specific Client
```bash
curl -H "Authorization: Bearer your_key_here" \
  https://api.example.com/api/v1/clients/c123
```

### Create a New Invoice
```bash
curl -X POST https://api.example.com/api/v1/invoices \
  -H "Authorization: Bearer your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "c123",
    "amount": 5000,
    "due_date": "2024-03-15",
    "description": "Development services"
  }'
```

---

## 4. Key Concepts

**Resources:** Objects you can work with (clients, projects, invoices, etc.)

**Methods:**
- `GET` - Retrieve data
- `POST` - Create new resource
- `PUT` - Update existing resource
- `DELETE` - Remove resource

**Rate Limits:**
- Free tier: 60 requests/minute
- Pro tier: 300 requests/minute
- Upgrade in settings if needed

---

## Next Steps
- [View All Endpoints](./endpoints.md)
- [Authentication Guide](./auth.md)
- [Code Examples](./examples.md)
- [Troubleshooting](./troubleshooting.md)
```

**What improved:**
- ✅ Clear, scannable structure
- ✅ Step-by-step setup
- ✅ Working code examples
- ✅ Expected output shown
- ✅ Error documentation
- ✅ Common tasks highlighted
- ✅ Key concepts explained simply
- ✅ Links to next resources
- ✅ Starts simple, builds complexity
- ✅ Actionable from the first section

---

## 15. Writing Tools & Techniques

### ✅ Effective Techniques

**Technique 1: The "So What" Test**
For every paragraph, ask "So what? Why should the reader care?"

Bad: "The API uses JSON format"
Better: "Responses are in JSON format, which most programming languages can parse easily"

**Technique 2: The Buddy Read**
Have someone unfamiliar with the topic read it. If they're confused, rewrite.

**Technique 3: The Read-Aloud Test**
Read your writing aloud. If you stumble or sound awkward, simplify.

**Technique 4: The Skim Test**
Scan your document. Can a reader understand it by reading only headings and first sentences?

**Technique 5: Cut Ruthlessly**
First draft, cut 20%. It's almost always better.

---

### Tools

**Grammar & Style:**
- Hemingway Editor - Highlights complex sentences
- Grammarly - Grammar and clarity
- ProWritingAid - Comprehensive writing analysis

**Markdown:**
- VS Code with Markdown Preview
- Notion or Confluence - Collaborative editing
- MkDocs - Static documentation site

**Diagramming:**
- Excalidraw - Hand-drawn diagrams
- Mermaid - Code-based diagrams
- Lucidchart - Professional diagrams

---

## 16. Quick Reference: Good vs. Bad

| Aspect | ❌ Avoid | ✅ Use Instead |
|--------|---------|-----------------|
| **Passive** | "It is known that..." | "We've found that..." |
| **Unclear** | "The thing needs to be done" | "You must verify the data" |
| **Wordy** | "In light of the fact that" | "Because" |
| **Jargon** | "Utilize the authentication mechanism" | "Log in" |
| **Vague** | "Might cause issues" | "Will prevent the API call" |
| **Hedging** | "Arguably, it could be said..." | "This happens because..." |
| **Assumption** | "Obviously, you'll want to..." | "You'll want to [because X]..." |
| **Buried** | "The API, which uses REST, which means..." | "The API uses REST (a standard way to structure APIs)" |
| **No context** | "Use method X" | "Use GET to retrieve client data" |
| **No example** | "Include parameters" | "Include `?status=active` to filter results" |

---

## 17. Summary: Technical Writing Principles

### The Golden Rules

1. **Know Your Audience** - Write for them specifically
2. **Be Clear** - Use simple words and short sentences
3. **Be Accurate** - Verify all facts and code examples
4. **Be Organized** - Use headings, lists, and formatting
5. **Be Concise** - Every word should earn its place
6. **Show, Don't Tell** - Use examples and code
7. **Anticipate Problems** - Document errors and solutions
8. **Make It Scannable** - Readers skim, not read
9. **Test It** - Have someone unfamiliar with topic read it
10. **Revise It** - First drafts are never final

### The Mindset

Think of yourself as a **translator**, not a reporter. Your job is to:
- Translate complex ideas into simple language
- Translate theory into practice
- Translate confusion into clarity
- Translate readers' problems into solutions

---

## 18. Practice Exercises

### Exercise 1: Clarity
**Rewrite this in 20 words or fewer:**
```
The system has been designed and implemented with the capability to process 
a large volume of concurrent requests while maintaining a high level of 
performance and reliability.
```

**Answer:** The system handles many simultaneous requests reliably and fast.

---

### Exercise 2: Remove Jargon
**Rewrite without technical terms:**
```
Implement exponential backoff with configurable retry logic in your client 
to gracefully handle transient 5xx errors and rate-limit responses.
```

**Answer:** When a request fails, wait longer before retrying (start with 1 second, 
then 2 seconds, then 4 seconds). Stop retrying after X attempts.

---

### Exercise 3: Add Examples
**Add a concrete example:**
```
Pass query parameters to filter results.
```

**Answer:** Pass query parameters to filter results. For example:

```
GET /api/v1/invoices?status=paid&client_id=c123
```

Returns only paid invoices for client c123.

---

### Exercise 4: Structure
**Reorganize into sections:**
```
The API supports pagination using limit and offset parameters. You can retrieve 
data in chunks. The default limit is 50 items. Maximum is 100. To get the next 
page, increase offset by the limit value. For example, first call uses offset=0, 
second uses offset=50.
```

**Answer:**
```markdown
## Pagination

Get large datasets in manageable chunks using `limit` and `offset` parameters.

| Parameter | Default | Maximum |
|-----------|---------|---------|
| limit | 50 | 100 |
| offset | 0 | Unlimited |

### Example

**Page 1:**
```
GET /api/v1/clients?limit=50&offset=0
```

**Page 2:**
```
GET /api/v1/clients?limit=50&offset=50
```
```

---

## 19. Resources for Technical Writers

### Books
- "Thinking with Type" - Ellen Lupton
- "The Sense of Style" - Steven Pinker
- "On Writing Well" - William Zinsser
- "Technical Communication Today" - Richard Johnson-Sheehan

### Online References
- Google's Technical Writing Course (free)
- Microsoft Writing Style Guide
- Apple Style Guide
- The Chicago Manual of Style

### Communities
- Write the Docs - Community and conferences
- Technical Writers HQ - Slack community
- Society for Technical Communication (STC)

---

## 20. Final Thoughts

Good technical writing is **invisible**. Readers don't think about the writing—they just understand the concept, follow the steps, and get things done.

Poor technical writing is **visible and frustrating**. Readers think about the writing, get confused, and give up.

Your job is to make the complex simple, the confusing clear, and the difficult manageable.

**Every word should move the reader closer to understanding and action.**

---

*This guide is your reference for writing clear, accurate, and helpful technical documentation.*
