import datetime
import os
from http import HTTPStatus
import requests

from dotenv import load_dotenv

def get_comment_count(after: datetime.date, before: datetime.date):
    template = """
    query {
      viewer {
        issueComments(last: 100, before: $before) {
          pageInfo {
            hasPreviousPage
            startCursor
          }
          edges {
            node {
              id
              createdAt
              repository {
                id
                nameWithOwner
              }
            }
          }
        }
      }
    }
    """
    before = before.strftime("%Y-%m-%d")
    after = after.strftime("%Y-%m-%d")

    prev = "null"
    count = 0
    token = os.getenv("GITHUB_PAT")
    while prev is not None:
        response = requests.post(
            url="https://api.github.com/graphql",
            json={"query": template.replace("$before", prev)},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == HTTPStatus.OK

        result = response.json()
        comments = result["data"]["viewer"]["issueComments"]
        comments_in_time_period = [1 for c in comments["edges"] if before > c["node"]["createdAt"] > after]
        count += len(comments_in_time_period)
        if any(c["node"]["createdAt"] < after for c in comments["edges"]):
            return count
        prev = comments["pageInfo"]["startCursor"]
    return count

load_dotenv()
count = get_comment_count(after=datetime.date(2024, 10, 1), before=datetime.date(2024, 11, 1))
print(count)
