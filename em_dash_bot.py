#!/usr/bin/env python3
"""
Em-Dash Scanner Bot
A Reddit bot that can be summoned to scan users for em dash usage.
Responds to username mentions and analyzes the requested user.
"""

import praw
import argparse
import configparser
import sys
import time
import re
from datetime import datetime
from em_dash_scanner import scan_user


def load_config(config_path='config.ini'):
    """Load Reddit API credentials from config file."""
    config = configparser.ConfigParser()
    try:
        config.read(config_path)
        # Validate bot credentials are present
        if 'username' not in config['reddit'] or 'password' not in config['reddit']:
            print("Error: Bot mode requires 'username' and 'password' in config.ini")
            sys.exit(1)
        return config
    except Exception as e:
        print(f"Error reading config file: {e}")
        print(f"Please create a config.ini file. See config.ini.example for template.")
        sys.exit(1)


def create_reddit_instance(config):
    """Create and return an authenticated Reddit instance for bot mode."""
    try:
        reddit = praw.Reddit(
            client_id=config['reddit']['client_id'],
            client_secret=config['reddit']['client_secret'],
            user_agent=config['reddit']['user_agent'],
            username=config['reddit']['username'],
            password=config['reddit']['password']
        )
        return reddit
    except Exception as e:
        print(f"Error creating Reddit instance: {e}")
        print("Please check your config.ini file has valid credentials.")
        sys.exit(1)


def extract_username(comment_body):
    """
    Extract username to scan from comment body.
    Looks for patterns like: u/username or /u/username
    """
    # Look for u/username or /u/username pattern
    patterns = [
        r'(?:^|\s)u/(\w+)',
        r'(?:^|\s)/u/(\w+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, comment_body, re.IGNORECASE)
        if matches:
            # Return first username found that's not the bot itself
            for match in matches:
                return match
    
    return None


def format_bot_reply(results):
    """Format scan results for bot reply (Reddit comment format)."""
    if 'error' in results:
        return f"Sorry, I encountered an error: {results['error']}"
    
    reply = []
    reply.append(f"## Em-Dash Scan Results for u/{results['username']}\n")
    
    # Overall statistics
    reply.append("### 📊 Statistics\n")
    reply.append(f"* **Total posts scanned:** {results['total_posts']}")
    reply.append(f"* **Total comments scanned:** {results['total_comments']}")
    reply.append(f"* **Posts with em dashes:** {results['posts_with_em_dash']}")
    reply.append(f"* **Comments with em dashes:** {results['comments_with_em_dash']}")
    reply.append(f"* **Total em dashes found:** {results['total_em_dashes']}\n")
    
    # Pre/Post ChatGPT analysis
    reply.append("### 🤖 ChatGPT Timeline Analysis\n")
    reply.append(f"*ChatGPT was released on November 30, 2022*\n")
    reply.append(f"**Before ChatGPT:**")
    reply.append(f"* Em dashes: {results['em_dashes_pre_chatgpt']}")
    reply.append(f"* Posts: {results['posts_pre_chatgpt']}")
    reply.append(f"* Comments: {results['comments_pre_chatgpt']}\n")
    reply.append(f"**After ChatGPT:**")
    reply.append(f"* Em dashes: {results['em_dashes_post_chatgpt']}")
    reply.append(f"* Posts: {results['posts_post_chatgpt']}")
    reply.append(f"* Comments: {results['comments_post_chatgpt']}\n")
    
    # Analysis
    reply.append("### 💡 Analysis\n")
    if results['total_em_dashes'] > 0:
        if results['em_dashes_pre_chatgpt'] > 0:
            reply.append(f"This user has a history of using em dashes before ChatGPT was released.")
            if results['em_dashes_post_chatgpt'] > results['em_dashes_pre_chatgpt']:
                reply.append(f"Their usage has increased after ChatGPT's release.")
            else:
                reply.append(f"Their usage pattern appears consistent.")
        else:
            reply.append(f"All em dashes found are from after ChatGPT's release. ")
            reply.append(f"This could indicate AI usage, but isn't conclusive.")
    else:
        reply.append(f"No em dashes found in scanned content.")
    
    reply.append("\n---")
    reply.append("\n^(I'm a bot that scans Reddit users for em dash usage patterns. ) "
                "^[Source](https://github.com/dandol328/Em-Dash-Scanner)")
    
    return '\n'.join(reply)


def process_mention(reddit, comment, processed_ids):
    """Process a mention of the bot."""
    # Skip if already processed
    if comment.id in processed_ids:
        return False
    
    try:
        # Extract username from comment
        username = extract_username(comment.body)
        
        if not username:
            # If no username found, reply with help
            help_text = ("Hi! To use me, mention a Reddit user in your comment. "
                        "For example: `u/BotName u/targetusername`\n\n"
                        "I'll scan that user's posts and comments for em dash usage.")
            comment.reply(help_text)
            processed_ids.add(comment.id)
            print(f"Replied to {comment.author} with help text")
            return True
        
        print(f"Processing request from u/{comment.author} to scan u/{username}")
        
        # Scan the user
        results = scan_user(reddit, username, limit=1000)  # Limit to 1000 for bot mode
        
        # Format and reply
        reply_text = format_bot_reply(results)
        comment.reply(reply_text)
        
        processed_ids.add(comment.id)
        print(f"Successfully replied to u/{comment.author} about u/{username}")
        return True
        
    except praw.exceptions.RedditAPIException as e:
        print(f"Reddit API error: {e}")
        # Check if it's a rate limit error
        if 'RATELIMIT' in str(e):
            print("Rate limited. Waiting before retrying...")
            time.sleep(60)
        return False
    except Exception as e:
        print(f"Error processing mention: {e}")
        # Try to reply with error message
        try:
            comment.reply(f"Sorry, I encountered an error while processing your request: {str(e)}")
            processed_ids.add(comment.id)
        except:
            pass
        return False


def run_bot(reddit):
    """Main bot loop that monitors for mentions."""
    print(f"Starting Em-Dash Scanner Bot as u/{reddit.user.me()}")
    print("Monitoring for mentions... (Press Ctrl+C to stop)\n")
    
    processed_ids = set()
    
    try:
        while True:
            try:
                # Check mentions
                for mention in reddit.inbox.mentions(limit=25):
                    if mention.id not in processed_ids:
                        # Mark as read
                        mention.mark_read()
                        process_mention(reddit, mention, processed_ids)
                        
                        # Sleep to avoid rate limits
                        time.sleep(2)
                
                # Clean up old IDs (keep last 1000)
                if len(processed_ids) > 1000:
                    processed_ids = set(list(processed_ids)[-1000:])
                
                # Sleep before checking again
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checked mentions. Sleeping for 60 seconds...")
                time.sleep(60)
                
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"Error in main loop: {e}")
                print("Sleeping for 60 seconds before retrying...")
                time.sleep(60)
                
    except KeyboardInterrupt:
        print("\n\nBot stopped by user.")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description='Run the Em-Dash Scanner as a Reddit bot that responds to mentions.'
    )
    parser.add_argument('--config', default='config.ini', 
                       help='Path to config file (default: config.ini)')
    
    args = parser.parse_args()
    
    # Load config and create Reddit instance
    config = load_config(args.config)
    reddit = create_reddit_instance(config)
    
    # Run the bot
    run_bot(reddit)


if __name__ == '__main__':
    main()
