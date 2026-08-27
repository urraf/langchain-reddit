"""LangChain retrievers for Reddit data.

This module provides three retrievers for fetching Reddit data
as LangChain Document objects:

- RedditSearchRetriever: Search posts by keyword.
- RedditSubredditRetriever: Fetch posts from a subreddit feed.
- RedditCommentsRetriever: Fetch the comment tree for a post.
"""

from __future__ import annotations

from typing import Any

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field, PrivateAttr

from langchain_reddit._client import RedditClient


class RedditSearchRetriever(BaseRetriever):
    """Search Reddit posts by keyword. Requires Reddit app credentials."""
    
    client_id: str = Field(description="Reddit app client ID")
    client_secret: str = Field(description="Reddit app client secret")
    user_agent: str = Field(default="langchain-reddit:v0.1.0 (by /u/langchain)")
    
    subreddit: str = Field(
        default="all",
        description="Subreddit name to search in, or 'all'."
    )
    max_results: int = Field(
        default=10,
        description="Maximum number of search results to return (1-100)."
    )
    sort: str = Field(
        default="relevance",
        description="Sort order. Options: 'relevance', 'hot', 'top', 'new', 'comments'."
    )
    time_filter: str = Field(
        default="all",
        description="Time filter. Options: 'all', 'day', 'hour', 'month', 'week', 'year'."
    )
    
    _client: RedditClient = PrivateAttr()
    
    def model_post_init(self, __context: Any) -> None:
        """Initialize the Reddit API client."""
        super().model_post_init(__context)
        self._client = RedditClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )
        
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        """Search Reddit and return matching posts as Documents."""
        submissions = self._client.search_posts(
            query=query,
            subreddit=self.subreddit,
            max_results=self.max_results,
            sort=self.sort,
            time_filter=self.time_filter,
        )
        
        documents: list[Document] = []
        for post in submissions:
            content = f"Title: {post.title}\n"
            if getattr(post, "selftext", None):
                content += f"\nBody:\n{post.selftext}\n"
                
            metadata = {
                "source": "reddit_search",
                "post_id": post.id,
                "subreddit": str(post.subreddit),
                "author": str(post.author) if post.author else "[deleted]",
                "score": getattr(post, "score", 0),
                "upvote_ratio": getattr(post, "upvote_ratio", 0.0),
                "num_comments": getattr(post, "num_comments", 0),
                "created_utc": getattr(post, "created_utc", 0),
                "is_self": getattr(post, "is_self", False),
                "permalink": f"https://www.reddit.com{getattr(post, 'permalink', '')}",
                "url": getattr(post, "url", ""),
            }
            documents.append(Document(page_content=content.strip(), metadata=metadata))
            
        return documents


class RedditSubredditRetriever(BaseRetriever):
    """Fetch posts from a subreddit. Requires Reddit app credentials."""
    
    client_id: str = Field(description="Reddit app client ID")
    client_secret: str = Field(description="Reddit app client secret")
    user_agent: str = Field(default="langchain-reddit:v0.1.0 (by /u/langchain)")
    
    subreddit_name: str = Field(description="Subreddit name without 'r/'.")
    listing: str = Field(
        default="hot",
        description="Feed type. Options: 'hot', 'new', 'top', 'rising'."
    )
    max_results: int = Field(
        default=10,
        description="Maximum number of posts to fetch."
    )
    time_filter: str = Field(
        default="week",
        description="Time filter for 'top' listing. Options: 'all', 'day', 'hour', 'month', 'week', 'year'."
    )
    
    _client: RedditClient = PrivateAttr()
    
    def model_post_init(self, __context: Any) -> None:
        """Initialize the Reddit API client."""
        super().model_post_init(__context)
        self._client = RedditClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )
        
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        """Fetch posts from a subreddit and return as Documents. Query is ignored."""
        submissions = self._client.get_subreddit_posts(
            subreddit_name=self.subreddit_name,
            listing=self.listing,
            max_results=self.max_results,
            time_filter=self.time_filter,
        )
        
        documents: list[Document] = []
        for post in submissions:
            content = f"Title: {post.title}\n"
            if getattr(post, "selftext", None):
                content += f"\nBody:\n{post.selftext}\n"
                
            metadata = {
                "source": f"reddit_subreddit_{self.listing}",
                "post_id": post.id,
                "subreddit": str(post.subreddit),
                "author": str(post.author) if post.author else "[deleted]",
                "score": getattr(post, "score", 0),
                "num_comments": getattr(post, "num_comments", 0),
                "created_utc": getattr(post, "created_utc", 0),
                "permalink": f"https://www.reddit.com{getattr(post, 'permalink', '')}",
            }
            documents.append(Document(page_content=content.strip(), metadata=metadata))
            
        return documents


class RedditCommentsRetriever(BaseRetriever):
    """Fetch comments from a Reddit post. Requires Reddit app credentials."""
    
    client_id: str = Field(description="Reddit app client ID")
    client_secret: str = Field(description="Reddit app client secret")
    user_agent: str = Field(default="langchain-reddit:v0.1.0 (by /u/langchain)")
    
    max_results: int = Field(
        default=50,
        description="Maximum number of comments to return."
    )
    sort: str = Field(
        default="best",
        description="Comment sorting. Options: 'best', 'top', 'new', 'controversial', 'q&a'."
    )
    
    _client: RedditClient = PrivateAttr()
    
    def model_post_init(self, __context: Any) -> None:
        """Initialize the Reddit API client."""
        super().model_post_init(__context)
        self._client = RedditClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )
        
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        """Fetch comments for a post and return as Documents."""
        post_id = self._client.extract_post_id(query)
        comments = self._client.get_post_comments(
            post_id=post_id,
            max_results=self.max_results,
            sort=self.sort,
        )
        
        documents: list[Document] = []
        for i, comment in enumerate(comments):
            metadata = {
                "source": "reddit_comments",
                "comment_id": comment["id"],
                "post_id": post_id,
                "author": comment["author"],
                "score": comment["score"],
                "created_utc": comment["created_utc"],
                "parent_id": comment["parent_id"],
                "is_submitter": comment["is_submitter"],
                "permalink": comment["permalink"],
                "comment_index": i,
            }
            
            documents.append(Document(page_content=comment["body"], metadata=metadata))
            
        return documents
