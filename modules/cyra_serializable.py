from base.modules.serializable_object import JsonEntry
from modules.cyra_converter import hero_and_secret
import logging

logger = logging.getLogger(__name__)

class LeaderboardEntry(JsonEntry):

  @classmethod
  def from_data(cls, data):
    params = {}
    params["season"] = data["season"]
    params["week"] = data["week"]
    params["messages"] = {}
    for guildid, messages in data["messages"].items():
      if not messages:
        continue
      params["messages"][int(guildid)] ={
        "all": {"channel": messages["all"]["channel"], "message":messages["all"]["message"]},
        "season": {"channel": messages["season"]["channel"], "message":messages["season"]["message"]},
        "week": {"channel": messages["week"]["channel"], "message":messages["week"]["message"]},
      }
    return params
    

class TransformListEntry(JsonEntry):

  @classmethod
  def from_data(cls, data):
    transform_list = []
    for hero in data["list"]:
      try:
        hero = hero_and_secret(hero)
        if hero not in transform_list:
          transform_list.append(hero)
      except:
        pass
    assert(len(transform_list) >= 2)
    transform_interval = data["interval"]
    return {"list": transform_list, "interval": transform_interval}
