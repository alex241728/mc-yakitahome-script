import argparse
from collections import defaultdict
from collections.abc import Iterable
from enum import Enum
from itertools import islice


class StoryType(str, Enum):
    """鸣潮任务种类枚举"""

    MAIN = "潮汐任务"
    COMPANION = "伴星任务"
    SIDE = "纪闻任务"
    EXPLORATION = "危行任务"
    TUTORIAL = "道引任务"
    EVENT = "活动任务"
    EPISODE = "异闻任务"
    DAILY = "日常任务"
    TALES = "奇谭任务"
    OTHER = "其他任务"

    def __str__(self):
        return self.value

    @classmethod
    def from_token(cls, token: str) -> "StoryType":
        """智能解析 CLI 参数：支持简称（如'伴星'）、全称（如'伴星任务'）"""
        t = token.strip()
        mapping = {
            "潮汐": cls.MAIN,
            "潮汐任务": cls.MAIN,
            "伴星": cls.COMPANION,
            "伴星任务": cls.COMPANION,
            "同行": cls.COMPANION,
            "同行任务": cls.COMPANION,
            "纪闻": cls.SIDE,
            "纪闻任务": cls.SIDE,
            "危行": cls.EXPLORATION,
            "危行任务": cls.EXPLORATION,
            "探索": cls.EXPLORATION,
            "探索任务": cls.EXPLORATION,
            "道引": cls.TUTORIAL,
            "道引任务": cls.TUTORIAL,
            "活动": cls.EVENT,
            "活动任务": cls.EVENT,
            "异闻": cls.EPISODE,
            "异闻任务": cls.EPISODE,
            "日常": cls.DAILY,
            "日常任务": cls.DAILY,
            "奇谭": cls.TALES,
            "奇谭任务": cls.TALES,
            "其他": cls.OTHER,
            "其他任务": cls.OTHER,
        }
        if t in mapping:
            return mapping[t]
        raise argparse.ArgumentTypeError(f"未知的任务类型: {token}")


DESC_TO_TYPE: dict[str, StoryType] = {
    "潮汐任务": StoryType.MAIN,
    "同行任务": StoryType.COMPANION,
    "纪闻任务": StoryType.SIDE,
    "探索任务": StoryType.EXPLORATION,
    "异闻独奏": StoryType.TUTORIAL,
    "活动任务": StoryType.EVENT,
    "联动任务": StoryType.EPISODE,
    "每日任务": StoryType.DAILY,
    "奇谭任务": StoryType.TALES,
    "其他任务": StoryType.OTHER,
}


def flatten_stories(manifest_data: dict) -> Iterable[tuple[StoryType, int, str]]:
    return (
        (
            DESC_TO_TYPE.get(st.get("typeDescription")),
            story.get("id"),
            story.get("name", ""),
        )
        for st in manifest_data.get("storyTypes", [])
        for grp in st.get("groups", [])
        for story in grp.get("stories", [])
    )


def filter_stories(
    stream: Iterable[tuple[StoryType, int, str]],
    type: StoryType | None,
    name: str | None,
):
    expected_name = name.lower() if name else None
    seen = set()

    return filter(
        lambda item: (
            item[0] is not None
            and (not type or item[0] == type)
            and (not name or expected_name in item[2].lower())
            and (item[1] is not None)
            and item[1] not in seen
            and not seen.add(item[1])
        ),
        stream,
    )


def get_story_ids(manifest_data: dict, args) -> dict[str, list[int]]:
    """根据过滤条件，将目标故事 ID 按分类存入字典返回：
    {
        "潮汐任务": [101, 102, ...],
        "伴星任务": [201, 202, ...],
        ...
    }
    """

    flattened = flatten_stories(manifest_data)
    filtered = filter_stories(flattened, args.type, args.name)

    # 截取
    if args.limit and args.limit > 0:
        filtered = islice(filtered, args.limit)

    # 聚合
    result: dict[str, list[int]] = defaultdict(list)
    for story_type, story_id, _ in filtered:
        result[story_type.value].append(story_id)

    return dict(result)
