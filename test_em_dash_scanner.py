#!/usr/bin/env python3
"""
Simple tests for em_dash_scanner functionality
"""

from em_dash_scanner import count_em_dashes, format_results
from em_dash_bot import extract_username


def test_count_em_dashes():
    """Test em dash counting function."""
    print("Testing em dash counting...")
    
    # Test basic counting
    assert count_em_dashes("This is a test — with one em dash") == 1
    assert count_em_dashes("Two dashes — here and — here") == 2
    assert count_em_dashes("No dashes here") == 0
    assert count_em_dashes("") == 0
    assert count_em_dashes(None) == 0
    
    # Test with multiple consecutive em dashes
    assert count_em_dashes("Multiple —— dashes") == 2
    
    # Make sure we're only counting em dashes, not hyphens or en dashes
    assert count_em_dashes("Hyphen - and en dash – should not count") == 0
    
    print("✓ Em dash counting tests passed")


def test_extract_username():
    """Test username extraction from comments."""
    print("\nTesting username extraction...")
    
    # Test basic patterns
    assert extract_username("Please scan u/testuser") == "testuser"
    assert extract_username("Check out /u/testuser") == "testuser"
    assert extract_username("u/testuser is interesting") == "testuser"
    assert extract_username("/u/testuser123") == "testuser123"
    
    # Test with multiple usernames (should return first)
    assert extract_username("Check u/user1 and u/user2") == "user1"
    
    # Test with no username
    assert extract_username("No username here") is None
    assert extract_username("") is None
    
    print("✓ Username extraction tests passed")


def test_format_results():
    """Test result formatting."""
    print("\nTesting result formatting...")
    
    # Test with error
    error_result = {'error': 'User not found'}
    output = format_results(error_result)
    assert "❌" in output
    assert "User not found" in output
    
    # Test with valid results
    valid_result = {
        'username': 'testuser',
        'total_posts': 100,
        'total_comments': 500,
        'posts_with_em_dash': 5,
        'comments_with_em_dash': 10,
        'total_em_dashes': 20,
        'em_dashes_pre_chatgpt': 5,
        'em_dashes_post_chatgpt': 15,
        'posts_pre_chatgpt': 2,
        'posts_post_chatgpt': 3,
        'comments_pre_chatgpt': 3,
        'comments_post_chatgpt': 7,
        'examples': []
    }
    
    output = format_results(valid_result)
    assert "testuser" in output
    assert "100" in output  # total posts
    assert "500" in output  # total comments
    assert "20" in output   # total em dashes
    
    print("✓ Result formatting tests passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running Em-Dash Scanner Tests")
    print("=" * 60)
    
    try:
        test_count_em_dashes()
        test_extract_username()
        test_format_results()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


if __name__ == '__main__':
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
