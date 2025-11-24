#!/usr/bin/env python3
"""
Em-Dash Scanner - Standalone Script
Scans a Reddit user's posts and comments for em dashes (—) to analyze AI usage patterns.
"""

import praw
import argparse
import configparser
import sys
from datetime import datetime


# ChatGPT was released on November 30, 2022
CHATGPT_RELEASE_DATE = datetime(2022, 11, 30)


def load_config(config_path='config.ini'):
    """Load Reddit API credentials from config file."""
    config = configparser.ConfigParser()
    try:
        config.read(config_path)
        return config
    except Exception as e:
        print(f"Error reading config file: {e}")
        print(f"Please create a config.ini file. See config.ini.example for template.")
        sys.exit(1)


def create_reddit_instance(config):
    """Create and return a Reddit instance using credentials from config."""
    try:
        reddit = praw.Reddit(
            client_id=config['reddit']['client_id'],
            client_secret=config['reddit']['client_secret'],
            user_agent=config['reddit']['user_agent']
        )
        return reddit
    except Exception as e:
        print(f"Error creating Reddit instance: {e}")
        print("Please check your config.ini file has valid credentials.")
        sys.exit(1)


def count_em_dashes(text):
    """Count em dashes in text. Checks for — (U+2014)."""
    if not text:
        return 0
    return text.count('—')


def scan_user(reddit, username, limit=None):
    """
    Scan a Reddit user's posts and comments for em dashes.
    
    Args:
        reddit: PRAW Reddit instance
        username: Reddit username to scan
        limit: Maximum number of posts/comments to check (None for all)
    
    Returns:
        Dictionary with scan results
    """
    try:
        user = reddit.redditor(username)
        
        # Test if user exists
        try:
            _ = user.id
        except Exception:
            return {'error': f"User '{username}' not found or is suspended/deleted"}
        
        results = {
            'username': username,
            'total_posts': 0,
            'total_comments': 0,
            'posts_with_em_dash': 0,
            'comments_with_em_dash': 0,
            'total_em_dashes': 0,
            'em_dashes_pre_chatgpt': 0,
            'em_dashes_post_chatgpt': 0,
            'posts_pre_chatgpt': 0,
            'posts_post_chatgpt': 0,
            'comments_pre_chatgpt': 0,
            'comments_post_chatgpt': 0,
            'examples': []
        }
        
        print(f"Scanning user: u/{username}")
        print("This may take a while depending on user activity...\n")
        
        # Scan submissions (posts)
        print("Scanning posts...")
        for submission in user.submissions.new(limit=limit):
            results['total_posts'] += 1
            
            # Check title and selftext
            text_to_check = f"{submission.title} {submission.selftext or ''}"
            em_dash_count = count_em_dashes(text_to_check)
            
            if em_dash_count > 0:
                results['posts_with_em_dash'] += 1
                results['total_em_dashes'] += em_dash_count
                
                post_date = datetime.fromtimestamp(submission.created_utc)
                
                if post_date < CHATGPT_RELEASE_DATE:
                    results['em_dashes_pre_chatgpt'] += em_dash_count
                    results['posts_pre_chatgpt'] += 1
                else:
                    results['em_dashes_post_chatgpt'] += em_dash_count
                    results['posts_post_chatgpt'] += 1
                
                # Store example (limit to 5 examples)
                if len(results['examples']) < 5:
                    results['examples'].append({
                        'type': 'post',
                        'date': post_date.strftime('%Y-%m-%d'),
                        'text': text_to_check[:200] + '...' if len(text_to_check) > 200 else text_to_check,
                        'url': f"https://reddit.com{submission.permalink}",
                        'em_dash_count': em_dash_count
                    })
        
        # Scan comments
        print("Scanning comments...")
        for comment in user.comments.new(limit=limit):
            results['total_comments'] += 1
            
            em_dash_count = count_em_dashes(comment.body)
            
            if em_dash_count > 0:
                results['comments_with_em_dash'] += 1
                results['total_em_dashes'] += em_dash_count
                
                comment_date = datetime.fromtimestamp(comment.created_utc)
                
                if comment_date < CHATGPT_RELEASE_DATE:
                    results['em_dashes_pre_chatgpt'] += em_dash_count
                    results['comments_pre_chatgpt'] += 1
                else:
                    results['em_dashes_post_chatgpt'] += em_dash_count
                    results['comments_post_chatgpt'] += 1
                
                # Store example (limit to 5 examples)
                if len(results['examples']) < 5:
                    results['examples'].append({
                        'type': 'comment',
                        'date': comment_date.strftime('%Y-%m-%d'),
                        'text': comment.body[:200] + '...' if len(comment.body) > 200 else comment.body,
                        'url': f"https://reddit.com{comment.permalink}",
                        'em_dash_count': em_dash_count
                    })
        
        return results
        
    except Exception as e:
        return {'error': f"Error scanning user: {str(e)}"}


def format_results(results):
    """Format scan results for display."""
    if 'error' in results:
        return f"\n❌ {results['error']}\n"
    
    output = []
    output.append(f"\n{'=' * 70}")
    output.append(f"Em-Dash Scan Results for u/{results['username']}")
    output.append(f"{'=' * 70}\n")
    
    # Overall statistics
    output.append("📊 Overall Statistics:")
    output.append(f"  • Total posts scanned: {results['total_posts']}")
    output.append(f"  • Total comments scanned: {results['total_comments']}")
    output.append(f"  • Posts with em dashes: {results['posts_with_em_dash']}")
    output.append(f"  • Comments with em dashes: {results['comments_with_em_dash']}")
    output.append(f"  • Total em dashes found: {results['total_em_dashes']}\n")
    
    # Pre/Post ChatGPT analysis
    output.append("🤖 ChatGPT Timeline Analysis (Released: Nov 30, 2022):")
    output.append(f"  Before ChatGPT:")
    output.append(f"    • Em dashes: {results['em_dashes_pre_chatgpt']}")
    output.append(f"    • Posts: {results['posts_pre_chatgpt']}")
    output.append(f"    • Comments: {results['comments_pre_chatgpt']}")
    output.append(f"  After ChatGPT:")
    output.append(f"    • Em dashes: {results['em_dashes_post_chatgpt']}")
    output.append(f"    • Posts: {results['posts_post_chatgpt']}")
    output.append(f"    • Comments: {results['comments_post_chatgpt']}\n")
    
    # Analysis
    if results['total_em_dashes'] > 0:
        if results['em_dashes_pre_chatgpt'] > 0:
            output.append("💡 Analysis:")
            output.append(f"  This user has a history of using em dashes before ChatGPT was released.")
            if results['em_dashes_post_chatgpt'] > results['em_dashes_pre_chatgpt']:
                output.append(f"  Their usage has increased after ChatGPT's release.")
            else:
                output.append(f"  Their usage pattern appears consistent.")
        else:
            output.append("💡 Analysis:")
            output.append(f"  All em dashes found are from after ChatGPT's release.")
            output.append(f"  This could indicate AI usage, but isn't conclusive.")
    else:
        output.append("💡 Analysis:")
        output.append(f"  No em dashes found in scanned content.")
    
    output.append("")
    
    # Examples
    if results['examples']:
        output.append("📝 Examples of em dash usage:")
        for i, example in enumerate(results['examples'], 1):
            output.append(f"  {i}. [{example['type'].upper()}] {example['date']} - {example['em_dash_count']} em dash(es)")
            output.append(f"     \"{example['text']}\"")
            output.append(f"     {example['url']}\n")
    
    output.append(f"{'=' * 70}\n")
    
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Scan a Reddit user for em dash usage to analyze potential AI usage patterns.'
    )
    parser.add_argument('username', help='Reddit username to scan (without u/ prefix)')
    parser.add_argument('--config', default='config.ini', help='Path to config file (default: config.ini)')
    parser.add_argument('--limit', type=int, default=None, 
                       help='Limit number of posts/comments to scan (default: all)')
    
    args = parser.parse_args()
    
    # Load config and create Reddit instance
    config = load_config(args.config)
    reddit = create_reddit_instance(config)
    
    # Scan user
    results = scan_user(reddit, args.username, args.limit)
    
    # Display results
    print(format_results(results))


if __name__ == '__main__':
    main()
