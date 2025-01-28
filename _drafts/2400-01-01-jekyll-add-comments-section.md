---
title:  "Jekyll Add Comments for the Homelabs"
layout: post
published: false
---

Adding comments sections to the posts of a Jekyll website are a nice way to engage readers. This is especially true for the posts I write where someone may want to ask questions. People asking questions often are useful for other readers as well. Right now, they only have the option to send me email which isn't shared to the readers.

<!-- excerpt-end -->

## Add Comments

[Add Comments to Jekyll with the GitHub Issues API](https://www.aleksandrhovhannisyan.com/blog/jekyll-comment-system-github-issues/)

[ChatGPT conversion of Netlify nodeJS code to Python](https://chatgpt.com/c/67804dbd-2d38-8010-8074-f43b50bee567)

``` python
def get_comments_for_post(event, context):
    """
    Lambda function to fetch comments for a GitHub issue dynamically.
    """

    try:
        # Extract query parameters
        query_params = event.get("queryStringParameters", {})
        issue_number = query_params.get("id")
        github_url = query_params.get("url")

        if not issue_number or not issue_number.isdigit():
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "You must specify a valid issue ID."}),
            }

        # Determine owner and repo
        if github_url:
            owner, repo = extract_owner_and_repo(github_url)
        else:
            owner = query_params.get("owner")
            repo = query_params.get("repo")

        if not owner or not repo:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "You must specify 'owner' and 'repo' or provide a valid GitHub URL."}),
            }

        issue_number = int(issue_number)

        # Check API rate limit
        rate_limit = octokit.request("GET /rate_limit")["rate"]
        remaining_requests = rate_limit["remaining"]
        print(f"GitHub API requests remaining: {remaining_requests}")
        if remaining_requests == 0:
            return {
                "statusCode": 503,
                "body": json.dumps({"error": "API rate limit exceeded."}),
            }

        # Fetch comments for the given issue
        comments_response = octokit.paginate(
            "GET /repos/{owner}/{repo}/issues/{issue_number}/comments",
            {"owner": owner, "repo": repo, "issue_number": issue_number},
        )

        # Process comments
        response = []
        for comment in comments_response:
            response.append({
                "user": {
                    "avatarUrl": comment["user"]["avatar_url"],
                    "name": escape(comment["user"]["login"]),
                    "isAuthor": comment["author_association"] == "OWNER",
                },
                "dateTime": comment["created_at"],
                "dateRelative": str((datetime.now() - datetime.fromisoformat(comment["created_at"].replace("Z", ""))).days) + " days ago",
                "isEdited": comment["created_at"] != comment["updated_at"],
                "body": escape(markdown(comment["body"])),
            })

        return {
            "statusCode": 200,
            "body": json.dumps({"data": response}),
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Unable to fetch comments for this post."}),
        }
```

## Header Links

[Jekyll heading links](https://remarkablemark.org/blog/2020/04/04/jekyll-heading-anchor-links/)
