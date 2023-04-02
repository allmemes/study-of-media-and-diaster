import logging
from traceback import format_exc
from typing import Any, List, Optional

import pandas as pd

from tikapi import TikAPI, ValidationException, ResponseException
from tikapi.api import APIResponse


logger = logging.getLogger("TiktokAPI")


class TiktokAPI(object):
    def __init__(self, api_key: str):
        self.api = TikAPI(api_key)
        self.response = None

    def query(self,
              query: str,
              category: str = "videos",
              country: str = "us",
              session_id: Optional[str] = None):
        self.response = self.api.public.search(
            category=category,
            query=query,
            country=country,
            session_id=session_id
        )
        return self.fetch(self.response)

    def fetch(self, response: APIResponse) -> List[Any]:
        result = list()
        try:
            while response:
                result.append(response.json())
                cursor = response.json().get("cursor")
                logger.info(f"Getting next items {cursor}")
                self.response = response
                response = response.next_items()
        except ValidationException as e:
            logger.error(f"{format_exc(), e.field}")
        except ResponseException as e:
            logger.error(f"{format_exc(), e.response.status_code}")
        else:
            logger.error(f"{format_exc()}")
        return result

    @staticmethod
    def prase_video_result(videos: List[Any]) -> pd.DataFrame:
        df = list()
        for video in videos:
            df.append({
                "CreateTime": video["createTime"],
                "Title": video["desc"],
                "Comment": video["stats"]["commentCount"],
                "Play": video["stats"]["playCount"],
                "Share": video["stats"]["shareCount"],
                "Dig": video["stats"]["diggCount"],
                "Duration": video["video"]["duration"],
                "Id": video["id"],
                "AuthorId": video["author"]["id"],
                "AuthorFollower": video["authorStats"]["followerCount"],
                "AuthorHeart": video["authorStats"]["heartCount"],
                "AuthorVideoCount": video["authorStats"]["videoCount"]
            })
        df = pd.DataFrame(df)
        df["EST"] = pd.to_datetime(df["CreateTime"], unit="s") - pd.Timedelta(hours=5)
        df["Date"] = df["EST"].dt.strftime("%Y%m%d")
        return df.set_index(["Id"]).sort_index()
