# 🚀 langchain-reddit

[![PyPI version](https://badge.fury.io/py/langchain-reddit.svg)](https://badge.fury.io/py/langchain-reddit)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**LangChain retrievers for Reddit** — search posts, fetch subreddit feeds, and retrieve full comment trees as LangChain `Document` objects using PRAW.

Perfect for building RAG applications that can analyze sentiment on Reddit, read trending news, and summarize discussion threads.

## ✨ Features

| Retriever | What it does | API Key Required? |
|---|---|---|
| `RedditSearchRetriever` | Search Reddit posts by keyword | ✅ Yes |
| `RedditSubredditRetriever` | Fetch hot/new/top posts from a subreddit | ✅ Yes |
| `RedditCommentsRetriever` | Fetch a full discussion thread for a post | ✅ Yes |

## 🔑 Getting Reddit Credentials

You need a free Reddit App to get your `client_id` and `client_secret`.
1. Go to https://www.reddit.com/prefs/apps
2. Click **"create another app..."** at the bottom.
3. Fill in the details:
   - **name:** `langchain-reddit`
   - **type:** Select **script**
   - **redirect uri:** `http://localhost:8080` (Not used, but required)
4. Click **Create app**.
5. Your **client_id** is under the app name, and **client_secret** is in the details.

## 📦 Installation

```bash
pip install langchain-reddit
```

## 🚀 Quick Start

### Search Reddit Posts

```python
from langchain_reddit import RedditSearchRetriever

retriever = RedditSearchRetriever(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    subreddit="python",     # Optional: default is "all"
    max_results=5,
    sort="relevance",
)

docs = retriever.invoke("langchain")

for doc in docs:
    print(f"📰 {doc.page_content.splitlines()[0]}")
    print(f"   👍 {doc.metadata['score']} upvotes | 💬 {doc.metadata['num_comments']} comments")
```

### Fetch Subreddit Feed

```python
from langchain_reddit import RedditSubredditRetriever

retriever = RedditSubredditRetriever(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    subreddit_name="machinelearning",
    listing="hot",  # "hot", "new", "top", "rising"
    max_results=10,
)

# The query is ignored for subreddit feeds
docs = retriever.invoke("fetch")
```

### Fetch a Comment Thread

```python
from langchain_reddit import RedditCommentsRetriever

retriever = RedditCommentsRetriever(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    max_results=50,
)

# Pass the post URL or ID
docs = retriever.invoke("https://www.reddit.com/r/Python/comments/1f2a3b4/example_post/")

for doc in docs:
    print(f"💬 {doc.metadata['author']}: {doc.page_content[:80]}...")
```

## 📄 License

MIT — see [LICENSE](LICENSE) for details.
