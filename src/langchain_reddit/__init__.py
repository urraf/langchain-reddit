"""LangChain Reddit integration.

Retrievers for searching posts, fetching subreddit feeds, and reading comment trees.

Install:
    pip install langchain-reddit

Usage:
    from langchain_reddit import RedditSearchRetriever, RedditSubredditRetriever

    # Search posts
    retriever = RedditSearchRetriever(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        max_results=5
    )
    docs = retriever.invoke("machine learning")

    # Get subreddit feed
    sub_retriever = RedditSubredditRetriever(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        subreddit_name="python",
        listing="hot"
    )
    docs = sub_retriever.invoke("fetch")
"""

from langchain_reddit.retrievers import (
    RedditSearchRetriever,
    RedditSubredditRetriever,
    RedditCommentsRetriever,
)

__all__ = [
    "RedditSearchRetriever",
    "RedditSubredditRetriever",
    "RedditCommentsRetriever",
]

__version__ = "0.1.0"
