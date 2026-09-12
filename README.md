<div align="center">

# Reddit Bot

### A feature-rich Reddit automation bot using Selenium

![Python Versions](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

</div>

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Input Formats](#input-formats)
- [Supported Actions](#supported-actions)
- [Anti-Detection](#anti-detection)
- [Orchestration](#orchestration)
- [Credentials & Security](#credentials--security)
- [Reporting & Notifications](#reporting--notifications)
- [Database Tracking](#database-tracking)
- [Docker](#docker)
- [CLI Reference](#cli-reference)
- [Testing](#testing)
- [Architecture](#architecture)
- [Contributing](#contributing)

---

## Features

### Core Actions
- **Upvote / Downvote** posts
- **Comment** under posts
- **Join / Leave** communities
- **Save / Hide** posts
- **Direct Message** users
- **Post Submission** — text, link, image posts
- **Crosspost** content to other subreddits
- **Follow / Unfollow** users
- **Update Profile** bio

### Reliability & Error Handling
- **Retry logic with exponential backoff** — failed actions automatically retry up to 3 times with increasing delays (2s, 4s, 8s)
- **Action verification** — checks DOM state after actions to confirm success (e.g., `aria-pressed` on vote buttons)
- **Screenshot on failure** — captures a browser screenshot when an action fails, saved to `screenshots/` directory
- **Graceful degradation** — if one action or account fails, the bot continues with the remaining work

### Anti-Detection
- **Proxy support** — load a list of proxies and rotate them per account session
- **User-Agent rotation** — randomize the browser fingerprint with realistic Chrome UA strings
- **Headless mode** — run without a visible browser window (`--headless`)
- **Rate limiting** — configurable random delays between actions and between accounts
- **Randomized action ordering** — shuffle the action list per account so each executes a unique sequence
- **Human-like mouse movement** — move the cursor along Bezier curves before clicking elements
- **Anti-automation flags** — disables `navigator.webdriver` and Chrome automation indicators

### Input & Configuration
- **YAML config file** — store all settings in a `config.yaml` instead of CLI flags
- **Multiple input formats** — pipe-delimited (`|`), CSV, and JSON for both accounts and action files
- **Environment variable credentials** — read accounts from `REDDIT_ACCOUNT_1`, `REDDIT_ACCOUNT_2`, etc.
- **Credential encryption** — encrypt account files at rest with a passphrase, decrypt at runtime
- **URL validation** — validates that links are actual Reddit URLs before attempting actions

### Orchestration
- **Scheduled execution** — run on a cron-like schedule (e.g., every 6 hours)
- **Staggered account switching** — configurable random delays between accounts
- **Daily action quotas** — limit the number of actions per account per day
- **Parallel accounts** — run multiple browser instances concurrently
- **Session persistence** — save and restore browser cookies between runs to avoid repeated logins

### Reporting & Observability
- **Structured logging** — JSON log output option for machine parsing, with colored terminal output
- **Execution summary** — ASCII table printed at the end showing success/failure per action
- **Progress bar** — visual progress indicator via `tqdm` for long runs
- **Webhook notifications** — send results to Discord, Slack, or any generic JSON webhook on completion or failure

### Database Tracking
- **SQLite action log** — every action is logged with timestamp, account, result, and optional screenshot path
- **Duplicate prevention** — skips actions already successfully performed by the same account
- **Daily stats** — tracks action counts per account per day for quota enforcement
- **Summary queries** — query aggregated success/failure stats from the database

### Developer Experience
- **Unit tests** — comprehensive test suite for config, parsing, validation, database, proxy, and reporting
- **Docker support** — `Dockerfile` with Chrome pre-installed for portable execution
- **CI pipeline** — GitHub Actions workflow for automated testing on Python 3.9-3.12
- **Plugin architecture** — actions are modular classes; add new actions without modifying core bot logic
- **Installable package** — `pyproject.toml` for `pip install .` support

---

## Installation

### Standard Installation

```bash
git clone https://github.com/markmelnic/Reddit-Bot
cd Reddit-Bot
pip install -r requirements.txt
```

### Development Installation

```bash
pip install -e ".[dev]"
```

### Docker Installation

```bash
docker build -t reddit-bot .
```

> **Note:** Chrome and chromedriver are automatically managed by `webdriver-manager` — no manual download required.

---

## 🔑 Bypassing Cloudflare & Captchas (Manual Session Export)

If Cloudflare or Reddit CAPTCHA blocks automated login on Render/Railway, you can log in manually on your local computer once and export your session cookies:

1. Run the helper script on your local machine:
   ```bash
   python export_session.py
   ```
2. Enter your Reddit username (e.g., `AppropriateChance699`).
3. A visible browser window will open. Log into Reddit manually and solve any captchas within 90 seconds.
4. The script will automatically save your session cookies to `sessions/AppropriateChance699.cookies`.
5. Commit and push the `sessions/` directory to GitHub:
   ```bash
   git add sessions/
   git commit -m "Add pre-authenticated session cookies"
   git push origin main
   ```
6. Render will deploy with your cookies pre-installed, and the bot will authenticate instantly without needing password login or triggering Cloudflare!

---

### Minimal Example

```bash
python main.py --accounts accounts.txt --links links.txt --verbose
```

### With Config File

```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your settings
python main.py --config config.yaml
```

### Dry Run (Preview Without Executing)

```bash
python main.py -a accounts.txt -l links.txt --dry-run --verbose
```

---

## Configuration

Settings can be provided via YAML config file, CLI flags, or environment variables. Priority order (highest to lowest):

1. **CLI arguments** — override everything
2. **Environment variables** — override config file
3. **YAML config file** — base configuration

### Example `config.yaml`

```yaml
accounts_path: "accounts.txt"
links_path: "links.txt"

verbose: true
headless: false
dry_run: false

rotate_user_agent: true
randomize_actions: true
human_mouse: false

proxy:
  enabled: true
  proxy_list_path: "proxies.txt"
  rotate_per_account: true

rate_limit:
  min_action_delay: 2.0
  max_action_delay: 8.0
  min_account_delay: 5.0
  max_account_delay: 15.0
  daily_action_quota: 50

parallel_accounts: 1
session_persistence: true

screenshot_on_failure: true
db_path: "reddit_bot.db"

webhook:
  enabled: true
  url: "https://discord.com/api/webhooks/..."
  on_completion: true
  on_failure: true
```

See [`config.example.yaml`](config.example.yaml) for the full template with comments.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `REDDIT_ACCOUNT_1` | Account credentials as `username\|password` |
| `REDDIT_ACCOUNT_2` | Second account, and so on |
| `REDDIT_BOT_KEY` | Passphrase for encrypted credential files |
| `REDDIT_BOT_ACCOUNTS` | Path to accounts file |
| `REDDIT_BOT_LINKS` | Path to links file |
| `REDDIT_BOT_HEADLESS` | Enable headless mode (`true`/`false`) |
| `REDDIT_BOT_DRY_RUN` | Enable dry run (`true`/`false`) |
| `REDDIT_BOT_DB_PATH` | Path to SQLite database |
| `REDDIT_BOT_WEBHOOK_URL` | Webhook URL for notifications |

---

## Input Formats

Both accounts and actions files support three formats:

### Accounts

**Pipe-delimited** (default):
```
username1|password1
username2|password2
```

**CSV:**
```csv
username,password
username1,password1
username2,password2
```

**JSON:**
```json
[
  {"username": "username1", "password": "password1"},
  {"username": "username2", "password": "password2"}
]
```

### Actions / Links

**Pipe-delimited** (default):
```
https://www.reddit.com/r/ProgrammerHumor/comments/abc123/title|upvote
https://www.reddit.com/r/ProgrammerHumor/comments/xyz789/title|comment|Great post!
https://www.reddit.com/r/ProgrammerHumor/|join
https://www.reddit.com/r/ProgrammerHumor/comments/abc123/title|save
https://www.reddit.com/user/someone|follow
```

**CSV:**
```csv
link,action,comment,title,subreddit,body,recipient,message
https://reddit.com/r/test/comments/abc,upvote,,,,,,
https://reddit.com/r/test/comments/abc,comment,Hello!,,,,,
https://reddit.com/r/test,join,,,,,,
,dm,,,,,targetuser,Hello from the bot!
,post_text,,,My Post Title,ProgrammerHumor,Post body text,,
```

**JSON:**
```json
[
  {"link": "https://reddit.com/r/test/comments/abc", "action": "upvote"},
  {"link": "https://reddit.com/r/test/comments/abc", "action": "comment", "comment": "Hello!"},
  {"action": "dm", "recipient": "targetuser", "title": "Subject", "message": "Hello!"},
  {"action": "post_text", "subreddit": "ProgrammerHumor", "title": "My Post", "body": "Content here"}
]
```

---

## Supported Actions

| Action | Description | Required Fields |
|--------|-------------|-----------------|
| `upvote` | Upvote a post | `link` |
| `downvote` | Downvote a post | `link` |
| `comment` | Post a comment | `link`, `comment` |
| `join` | Join a subreddit | `link` |
| `leave` | Leave a subreddit | `link` |
| `save` | Save a post | `link` |
| `hide` | Hide a post | `link` |
| `dm` | Send a direct message | `recipient`, `message` (optional: `title`) |
| `post_text` | Create a text post | `subreddit`, `title` (optional: `body`, `flair`) |
| `post_link` | Create a link post | `subreddit`, `title`, `body` (the URL) |
| `post_image` | Create an image post | `subreddit`, `title`, `body` (image file path) |
| `crosspost` | Crosspost to another sub | `link`, `subreddit` (optional: `title`) |
| `follow` | Follow a user | `link` (user profile URL) |
| `unfollow` | Unfollow a user | `link` (user profile URL) |
| `update_bio` | Update profile bio | `body` (bio text) |

---

## Anti-Detection

### Proxy Rotation

Create a `proxies.txt` file:
```
host1:port1
host2:port2
host3:port3:username:password
```

```bash
python main.py -a accounts.txt -l links.txt --proxy-list proxies.txt
```

Proxies rotate round-robin for each new account session.

### User-Agent Rotation

```bash
python main.py -a accounts.txt -l links.txt --rotate-ua
```

Each browser session starts with a random Chrome user agent from a pool of realistic UA strings.

### Human-Like Mouse Movement

```bash
python main.py -a accounts.txt -l links.txt --human-mouse
```

Uses Bezier curves to generate natural cursor paths before clicking elements. Requires the `bezier` and `numpy` packages.

### Headless Mode

```bash
python main.py -a accounts.txt -l links.txt --headless
```

Runs Chrome without a visible window. Useful for servers and Docker.

### Action Randomization

```bash
python main.py -a accounts.txt -l links.txt --randomize-actions
```

Shuffles the action list for each account so they don't all perform the same sequence.

---

## Orchestration

### Parallel Execution

Run multiple accounts simultaneously:

```bash
python main.py -a accounts.txt -l links.txt --parallel 3
```

### Scheduled Execution

Run on a schedule (simple interval-based):

```bash
python main.py -a accounts.txt -l links.txt --schedule "0 */6 * * *"
```

The bot will run every 6 hours and repeat indefinitely.

### Session Persistence

Save cookies between runs to avoid re-logging in:

```bash
python main.py -a accounts.txt -l links.txt --session-persistence
```

Sessions are stored in `.sessions/` as JSON cookie files.

### Daily Quotas

Set in config:

```yaml
rate_limit:
  daily_action_quota: 50
```

Once an account reaches 50 actions in a day, remaining actions are skipped.

---

## Credentials & Security

### Encrypt Credentials

First, encrypt your accounts file:

```python
from bot.utils.credentials import encrypt_file
encrypt_file("accounts.txt", "accounts.bin", "your-secret-passphrase")
```

Then run with the encrypted file:

```bash
export REDDIT_BOT_KEY="your-secret-passphrase"
python main.py -a accounts.bin -l links.txt --encrypt-credentials
```

### Environment Variable Accounts

```bash
export REDDIT_ACCOUNT_1="username1|password1"
export REDDIT_ACCOUNT_2="username2|password2"
python main.py -l links.txt
```

---

## Reporting & Notifications

### Execution Summary

With `--verbose`, a summary table is printed after completion:

```
================================================================================
EXECUTION SUMMARY
================================================================================
Duration: 142.3s | Total: 12 | Success: 10 | Failed: 2
--------------------------------------------------------------------------------
Status   Action          Link                                Message
--------------------------------------------------------------------------------
OK       upvote          https://reddit.com/r/test/comme..   Vote registered
OK       comment         https://reddit.com/r/test/comme..   Comment posted
FAIL     join            https://reddit.com/r/private        Message: NoSuchElem..
OK       follow          https://reddit.com/user/someone     User followed
================================================================================
```

### Webhook Notifications

#### Discord

```yaml
webhook:
  enabled: true
  url: "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

Sends a rich embed with color-coded success/failure status.

#### Slack

```yaml
webhook:
  enabled: true
  url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
```

#### Generic JSON

Any other URL receives the full execution summary as JSON.

### Screenshots on Failure

```bash
python main.py -a accounts.txt -l links.txt --screenshot-on-failure
```

Screenshots are saved to `screenshots/` with descriptive filenames including the action name and timestamp.

---

## Database Tracking

All actions are logged to a SQLite database (`reddit_bot.db` by default):

```sql
-- View all actions
SELECT * FROM action_log ORDER BY timestamp DESC;

-- View failures
SELECT * FROM action_log WHERE success = 0;

-- View daily stats per account
SELECT * FROM account_stats WHERE action_date = date('now');
```

The database prevents duplicate actions — if an account has already successfully upvoted a post, it will be skipped on subsequent runs.

---

## Docker

### Build and Run

```bash
docker build -t reddit-bot .

docker run -v $(pwd)/accounts.txt:/app/accounts.txt \
           -v $(pwd)/links.txt:/app/links.txt \
           reddit-bot -a accounts.txt -l links.txt --verbose
```

### With Config File

```bash
docker run -v $(pwd)/config.yaml:/app/config.yaml \
           -v $(pwd)/accounts.txt:/app/accounts.txt \
           -v $(pwd)/links.txt:/app/links.txt \
           reddit-bot --config config.yaml
```

The Docker image automatically runs in headless mode.

---

## CLI Reference

```
usage: reddit-bot [-h] [-a ACCOUNTS] [-l LINKS] [-c CONFIG] [-v]
                  [--headless] [--dry-run] [--proxy-list PROXY_LIST]
                  [--rotate-ua] [--randomize-actions] [--human-mouse]
                  [--parallel PARALLEL] [--schedule SCHEDULE]
                  [--session-persistence] [--encrypt-credentials]
                  [--screenshot-on-failure] [--webhook-url WEBHOOK_URL]

A feature-rich Reddit automation bot using Selenium.

options:
  -h, --help            Show this help message and exit
  -a, --accounts        Path to accounts file (pipe, CSV, or JSON)
  -l, --links           Path to actions file (pipe, CSV, or JSON)
  -c, --config          Path to YAML configuration file
  -v, --verbose         Enable verbose logging to stdout
  --headless            Run browser in headless mode
  --dry-run             Log actions without executing them
  --proxy-list          Path to proxy list file (host:port per line)
  --rotate-ua           Randomize User-Agent per session
  --randomize-actions   Shuffle action order per account
  --human-mouse         Use Bezier curve mouse movements
  --parallel N          Number of parallel browser instances
  --schedule CRON       Cron expression for scheduled runs
  --session-persistence Save/restore browser sessions
  --encrypt-credentials Accounts file is encrypted
  --screenshot-on-failure Capture screenshots on action failure
  --webhook-url URL     Webhook URL for notifications
```

---

## Testing

Run the test suite:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_config.py -v
pytest tests/test_database.py -v
```

Tests cover:
- Configuration loading, merging, and env var parsing
- Input file parsing (pipe-delimited, CSV, JSON)
- URL validation
- Credential encryption/decryption
- Proxy loading and rotation
- Database action logging and queries
- Execution summary reporting

---

## Architecture

```
reddit-bot/
├── main.py                    # Entry point and orchestration
├── args.py                    # CLI argument parser
├── config.example.yaml        # Example configuration file
├── pyproject.toml             # Package configuration
├── requirements.txt           # Dependencies
├── Dockerfile                 # Docker support
├── bot/
│   ├── __init__.py
│   ├── bot.py                 # Core RedditBot class
│   ├── config.py              # BotConfig dataclass with YAML/env support
│   ├── database.py            # SQLite action tracking
│   ├── ghost_logger.py        # No-op logger for silent mode
│   ├── reporting.py           # Summary, structured logging, webhooks
│   ├── actions/               # Plugin-based action system
│   │   ├── base.py            # BaseAction ABC and ActionResult
│   │   ├── registry.py        # Action name -> class mapping
│   │   ├── vote.py            # Upvote/downvote
│   │   ├── comment.py         # Comment on post
│   │   ├── community.py       # Join/leave subreddit
│   │   ├── save_hide.py       # Save/hide post
│   │   ├── post.py            # Text/link/image post, crosspost
│   │   ├── dm.py              # Direct messages
│   │   ├── follow.py          # Follow/unfollow users
│   │   └── profile.py         # Update bio
│   └── utils/                 # Shared utilities
│       ├── timeouts.py        # Randomized delays
│       ├── retry.py           # Exponential backoff decorator
│       ├── mouse.py           # Bezier curve mouse movement
│       ├── user_agents.py     # UA string rotation
│       ├── credentials.py     # Account parsing and encryption
│       ├── input_parser.py    # Action file parsing
│       ├── validators.py      # URL validation
│       └── proxy.py           # Proxy loading and rotation
├── tests/                     # Test suite
│   ├── test_config.py
│   ├── test_credentials.py
│   ├── test_input_parser.py
│   ├── test_validators.py
│   ├── test_database.py
│   ├── test_proxy.py
│   └── test_reporting.py
└── .github/
    └── workflows/
        └── ci.yml             # GitHub Actions CI pipeline
```

### Adding Custom Actions

Create a new action by extending `BaseAction`:

```python
# bot/actions/my_action.py
from bot.actions.base import BaseAction, ActionResult

class MyCustomAction(BaseAction):
    name = "my_action"

    def execute(self, link="", **kwargs):
        self.logger.info(f"Running my action on {link}")
        if self.config.dry_run:
            return ActionResult(success=True, action="my_action", link=link, message="Dry run")

        # Your Selenium logic here
        self._navigate(link)
        element = self._find_with_fallbacks(
            (By.CSS_SELECTOR, "button.my-button"),
            (By.XPATH, "//button[text()='Click Me']"),
        )
        self._click(element)

        return ActionResult(success=True, action="my_action", link=link, message="Done")
```

Register it in `bot/actions/registry.py`:

```python
from .my_action import MyCustomAction

# In ActionRegistry._action_map:
"my_action": MyCustomAction,
```

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/new-action`)
3. Write tests for any new functionality
4. Run the test suite (`pytest tests/ -v`)
5. Commit your changes
6. Push to your branch
7. Open a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) for details.
