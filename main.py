import argparse
import json
import urllib
from pathlib import Path

from export_md import save_markdown_file
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
        help="按分组名称筛选故事 (支持 '潮汐', '伴星', '潮汐任务' 等)",
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
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="output",
        help="Markdown文件输出目录 (默认: output)",
    )

    return parser.parse_args()


def fetch_and_export_story(story_id: int, output_dir: Path) -> str:
    """单个故事的拉取与转存任务（在线程池中运行）"""

    # time.sleep(1)

    url = f"https://mc.yakitahome.com/api/story-archive/detail/{story_id}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    saved_path = save_markdown_file(data, output_dir)
    return saved_path.name


def main():
    # 解析参数
    args = parse_args()

    print("--- 命令行参数解析结果 ---")
    print(f"目标名称 (-n): {args.name}")
    print(f"目标分组 (-t): {args.type}")
    print(f"数量限制 (-l): {args.limit}")

    # 取得manifest.json
    manifest_data = get_manifest("manifest.json", refresh=args.refresh)

    # 取得story IDs
    stories = get_story_ids(manifest_data, args)

    for story_type in stories:
        story_ids = stories.get(story_type)
        total_tasks = len(story_ids)

        if total_tasks == 0:
            print(f"\n[!] 在{story_type}中未匹配到任何待下载的故事任务。")
            continue

        output_dir = Path(args.output, story_type)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(
            f"\n[*] 在{story_type}中，共匹配到 {total_tasks} 个任务，准备启动多线程抓取并导出到 `{output_dir}/`..."
        )

        success_count = 0
        for idx, sid in enumerate(story_ids, 1):
            try:
                file_name = fetch_and_export_story(sid, output_dir)
                print(f"[{idx}/{total_tasks}] [✓] {file_name} (ID: {sid})")
                success_count += 1
            except (
                urllib.error.URLError,
                json.JSONDecodeError,
                UnicodeDecodeError,
                OSError,
            ) as e:
                print(
                    f"[{idx}/{total_tasks}] [x] ID {sid} 处理失败 ({story_type(e).__name__}): {e}"
                )

        print(f"\n[🎉] 处理完毕！成功导出 {success_count}/{total_tasks} 个剧情剧本。")


if __name__ == "__main__":
    main()
