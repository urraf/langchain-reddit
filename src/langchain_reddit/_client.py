"""Reddit API client wrapper.

Provides a clean interface for interacting with the Reddit API using PRAW,
handling authentication, fetching posts, and flattening comment trees.
"""

from __future__ import annotations

from typing import Any
import re
import praw
from praw.models import Submission

class RedditClient:
    """Wrapper around PRAW (Python Reddit API Wrapper)."""
    
    # Regex to extract post ID from a reddit.com URL
    REDDIT_URL_PATTERN = re.compile(r"comments/([a-z0-9]+)")
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str) -> None:
        if not client_id or not client_secret:
            raise ValueError("Reddit client_id and client_secret are required.")
            
        self._reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        # Verify read-only access is working
        self._reddit.read_only = True

    def search_posts(
        self,
        query: str,
        subreddit: str = "all",
        max_results: int = 10,
        sort: str = "relevance",
        time_filter: str = "all"
    ) -> list[Submission]:
        """Search posts via subreddit.search().
        
        Args:
            query: Search query string.
            subreddit: Subreddit name (or 'all').
            max_results: Maximum number of results to fetch.
            sort: 'relevance', 'hot', 'top', 'new', 'comments'.
            time_filter: 'all', 'day', 'hour', 'month', 'week', 'year'.
            
        Returns:
            List of PRAW Submission objects.
        """
        sub = self._reddit.subreddit(subreddit)
        results = []
        for submission in sub.search(query, sort=sort, time_filter=time_filter, limit=max_results):
            results.append(submission)
        return results

    def get_subreddit_posts(
        self,
        subreddit_name: str,
        listing: str = "hot",
        max_results: int = 10,
        time_filter: str = "all"
    ) -> list[Submission]:
        """Fetch posts from a subreddit (hot/new/top/rising).
        
        Args:
            subreddit_name: Subreddit name (without 'r/').
            listing: 'hot', 'new', 'top', 'rising'.
            max_results: Maximum number of posts to fetch.
            time_filter: Only applies to 'top' listing.
            
        Returns:
            List of PRAW Submission objects.
        """
        sub = self._reddit.subreddit(subreddit_name)
        results = []
        
        if listing == "hot":
            iterator = sub.hot(limit=max_results)
        elif listing == "new":
            iterator = sub.new(limit=max_results)
        elif listing == "top":
            iterator = sub.top(time_filter=time_filter, limit=max_results)
        elif listing == "rising":
            iterator = sub.rising(limit=max_results)
        else:
            raise ValueError(f"Invalid listing: {listing}")
            
        for submission in iterator:
            results.append(submission)
        return results

    def get_post_comments(
        self,
        post_id: str,
        max_results: int = 50,
        sort: str = "best"
    ) -> list[dict[str, Any]]:
        """Fetch comments via submission.comments. Handles replace_more().
        
        Args:
            post_id: The Reddit submission ID.
            max_results: Maximum number of comments to return.
            sort: 'best', 'top', 'new', 'controversial', 'q&a'.
            
        Returns:
            List of comment dictionaries, flattened from the tree.
        """
        submission = self._reddit.submission(id=post_id)
        submission.comment_sort = sort
        
        # Load all comments (removes the "load more comments" objects)
        # Using limit=0 means we don't fetch additional HTTP requests for deeply nested "more" comments
        # if max_results is small, otherwise we could use limit=None.
        limit = None if max_results > 100 else 0
        submission.comments.replace_more(limit=limit)
        
        comments_data = []
        # list() flattens the CommentForest into a flat list, ordered roughly by tree traversal
        for comment in submission.comments.list():
            if len(comments_data) >= max_results:
                break
                
            comments_data.append({
                "id": comment.id,
                "body": comment.body,
                "author": str(comment.author) if comment.author else "[deleted]",
                "score": comment.score,
                "created_utc": comment.created_utc,
                "parent_id": comment.parent_id,
                "is_submitter": comment.is_submitter,
                "permalink": f"https://www.reddit.com{comment.permalink}"
            })
            
        return comments_data

    @classmethod
    def extract_post_id(cls, url_or_id: str) -> str:
        """Extract post ID from a reddit.com URL or raw ID."""
        url_or_id = str(url_or_id).strip()
        
        match = cls.REDDIT_URL_PATTERN.search(url_or_id)
        if match:
            return match.group(1)
            
        if url_or_id.isalnum() and 5 <= len(url_or_id) <= 8:
            return url_or_id
            
        raise ValueError(f"Could not extract a Reddit post ID from: '{url_or_id}'")
