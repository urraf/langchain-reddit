import pytest
from langchain_reddit import (
    RedditSearchRetriever,
    RedditSubredditRetriever,
    RedditCommentsRetriever
)

def test_initialization():
    client_id = "test_id"
    client_secret = "test_secret"
    
    # Test Search Retriever
    search_retriever = RedditSearchRetriever(
        client_id=client_id,
        client_secret=client_secret,
        subreddit="python",
        max_results=5
    )
    assert search_retriever.subreddit == "python"
    assert search_retriever.max_results == 5
    
    # Test Subreddit Retriever
    sub_retriever = RedditSubredditRetriever(
        client_id=client_id,
        client_secret=client_secret,
        subreddit_name="machinelearning",
        listing="hot"
    )
    assert sub_retriever.subreddit_name == "machinelearning"
    assert sub_retriever.listing == "hot"
    
    # Test Comments Retriever
    comments_retriever = RedditCommentsRetriever(
        client_id=client_id,
        client_secret=client_secret,
        max_results=50
    )
    assert comments_retriever.max_results == 50
