# Em-Dash-Scanner

Crawls a Reddit account for em dashes — to see if they are using AI, or if they were using them before ChatGPT existed.

## Overview

Em-Dash Scanner is a Python tool that analyzes Reddit users' posts and comments for em dash (—) usage patterns. Em dashes are often used by AI language models like ChatGPT, so detecting their usage before and after ChatGPT's release (November 30, 2022) can provide insights into potential AI-generated content.

The tool provides two modes:
1. **Standalone Script**: Analyze any Reddit user from the command line
2. **Reddit Bot**: A bot that responds to mentions and scans requested users

## Features

- 📊 Scans all posts and comments from a specified Reddit user
- 🤖 Analyzes em dash usage before and after ChatGPT's release date
- 📈 Provides detailed statistics and timeline analysis
- 💬 Shows examples of em dash usage with links
- 🤖 Can run as a Reddit bot that responds to mentions

## Requirements

- Python 3.7 or higher
- Reddit API credentials (free from Reddit)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dandol328/Em-Dash-Scanner.git
   cd Em-Dash-Scanner
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Reddit API credentials:**

   a. Go to https://www.reddit.com/prefs/apps
   
   b. Click "create an app" or "create another app"
   
   c. Fill in the form:
      - Name: Em-Dash-Scanner (or any name you prefer)
      - Type: Select "script"
      - Description: (optional)
      - About URL: (optional)
      - Redirect URI: http://localhost:8080
   
   d. Click "create app"
   
   e. Note your credentials:
      - `client_id`: The string under "personal use script"
      - `client_secret`: The "secret" value

4. **Create configuration file:**
   ```bash
   cp config.ini.example config.ini
   ```

5. **Edit config.ini** with your credentials:
   ```ini
   [reddit]
   client_id = YOUR_CLIENT_ID_HERE
   client_secret = YOUR_CLIENT_SECRET_HERE
   user_agent = Em-Dash-Scanner by /u/YOUR_USERNAME

   # Only needed for bot mode
   username = YOUR_BOT_USERNAME
   password = YOUR_BOT_PASSWORD
   ```

## Usage

### Standalone Mode

The standalone script allows you to scan any Reddit user from the command line.

**Basic usage:**
```bash
python em_dash_scanner.py USERNAME
```

**Examples:**
```bash
# Scan a specific user
python em_dash_scanner.py spez

# Limit the scan to 100 most recent posts/comments
python em_dash_scanner.py spez --limit 100

# Use a custom config file
python em_dash_scanner.py spez --config /path/to/config.ini
```

**Command-line options:**
- `username` (required): Reddit username to scan (without u/ prefix)
- `--limit`: Limit number of posts/comments to scan (default: all)
- `--config`: Path to config file (default: config.ini)

**Sample output:**
```
Scanning user: u/example_user
This may take a while depending on user activity...

Scanning posts...
Scanning comments...

======================================================================
Em-Dash Scan Results for u/example_user
======================================================================

📊 Overall Statistics:
  • Total posts scanned: 150
  • Total comments scanned: 1250
  • Posts with em dashes: 5
  • Comments with em dashes: 23
  • Total em dashes found: 32

🤖 ChatGPT Timeline Analysis (Released: Nov 30, 2022):
  Before ChatGPT:
    • Em dashes: 3
    • Posts: 1
    • Comments: 2
  After ChatGPT:
    • Em dashes: 29
    • Posts: 4
    • Comments: 21

💡 Analysis:
  This user has a history of using em dashes before ChatGPT was released.
  Their usage has increased after ChatGPT's release.

📝 Examples of em dash usage:
  1. [COMMENT] 2023-05-15 - 2 em dash(es)
     "This is a great point — I hadn't considered that perspective..."
     https://reddit.com/r/example/comments/abc123/...

======================================================================
```

### Bot Mode

The bot mode runs continuously and responds to username mentions on Reddit.

**Setup for bot mode:**

1. Create a dedicated Reddit account for your bot
2. Add the bot's username and password to your `config.ini`:
   ```ini
   [reddit]
   client_id = YOUR_CLIENT_ID
   client_secret = YOUR_CLIENT_SECRET
   user_agent = Em-Dash-Scanner by /u/YOUR_USERNAME
   username = YOUR_BOT_USERNAME
   password = YOUR_BOT_PASSWORD
   ```

**Running the bot:**
```bash
python em_dash_bot.py
```

**Using the bot on Reddit:**

1. Mention the bot in a comment with the username you want to scan:
   ```
   /u/YourBotName u/targetusername
   ```

2. The bot will reply with a formatted analysis of the target user

**Example bot reply:**
```markdown
## Em-Dash Scan Results for u/targetusername

### 📊 Statistics

* **Total posts scanned:** 150
* **Total comments scanned:** 1250
* **Posts with em dashes:** 5
* **Comments with em dashes:** 23
* **Total em dashes found:** 32

### 🤖 ChatGPT Timeline Analysis

*ChatGPT was released on November 30, 2022*

**Before ChatGPT:**
* Em dashes: 3
* Posts: 1
* Comments: 2

**After ChatGPT:**
* Em dashes: 29
* Posts: 4
* Comments: 21

### 💡 Analysis

This user has a history of using em dashes before ChatGPT was released.
Their usage has increased after ChatGPT's release.

---

^(I'm a bot that scans Reddit users for em dash usage patterns. ) ^[Source](https://github.com/dandol328/Em-Dash-Scanner)
```

## How It Works

The scanner:
1. Uses the Reddit API (via PRAW) to fetch all posts and comments from a user
2. Searches for em dashes (—, Unicode U+2014) in the text
3. Categorizes findings by date (before/after ChatGPT's release on Nov 30, 2022)
4. Provides statistical analysis and examples

**Note:** The presence or absence of em dashes is not definitive proof of AI usage. Many people naturally use em dashes in their writing, and AI-generated content doesn't always contain them. This tool is meant to provide interesting data points, not conclusive evidence.

## Troubleshooting

**"Error reading config file"**
- Make sure you've created `config.ini` from the example file
- Check that the file is in the same directory as the scripts

**"Error creating Reddit instance"**
- Verify your Reddit API credentials are correct
- Make sure you created a "script" type application, not "web app"
- Check that your user agent string is descriptive

**"User not found or is suspended/deleted"**
- The username might be spelled incorrectly
- The user account may be suspended or deleted
- The user account might be shadowbanned

**Rate limiting errors**
- Reddit has rate limits on API calls
- The bot automatically handles rate limits by waiting
- For large scans, consider using the `--limit` option

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes. Always respect Reddit's Terms of Service and API usage guidelines. Be respectful of other users' privacy and don't harass or spam users based on the results of this tool.

The presence or absence of em dashes does not prove whether content is AI-generated or human-written. This tool provides data points for analysis, not definitive conclusions.
