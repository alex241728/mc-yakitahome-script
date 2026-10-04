import argparse

from manifest import get_manifest
from story import StoryType, get_story_ids


def parse_args():
    parser = argparse.ArgumentParser(
        description="瑝珑类书（mc.yakitahome.com）任务归档工具"
    )

    # 参数
    parser.add_argument(
        "--name", "-n", type=str, default=None, help="按任务名称下载故事"
    )
    parser.add_argument(
        "--type",
        "-t",
        type=StoryType.from_token,
        default=None,
        help="按任务种类下载故事",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=None,
        help="限制下载的故事数量 (可与 -n, -g 搭配使用)",
    )
    parser.add_argument(
        "--refresh",
        "-r",
        action="store_true",
        help="强制从远端重新下载并刷新本地 manifest.json",
    )

    return parser.parse_args()


def main():
    # 解析参数 (todo)
    args = parse_args()

    print("--- 命令行参数解析结果 ---")
    print(f"目标名称 (-n): {args.name}")
    print(f"目标分组 (-t): {args.type}")
    print(f"数量限制 (-l): {args.limit}")

    manifest_data = get_manifest("manifest.json", refresh=args.refresh)

    stories = get_story_ids(manifest_data, args)

    total_tasks = sum(len(ids) for ids in stories.values())
    print(f"\n匹配到待下载任务共 {total_tasks} 个:")
    for group, ids in stories.items():
        print(
            f"  [{group}]: {len(ids)} 个任务 (ID: {ids[:3]}{'...' if len(ids) > 3 else ''})"
        )


if __name__ == "__main__":
    main()
