import argparse

from manifest import get_manifest


def parse_args():
  parser = argparse.ArgumentParser(description="瑝珑类书（mc.yakitahome.com）任务归档工具")
  
  # 参数
  parser.add_argument("--name", "-n", type=str, default=None, help="按任务名称下载故事")
  
  parser.add_argument("--group", "-g", type=str, default=None, help="按分组名称下载故事") 
  
  parser.add_argument("--limit", "-l", type=int, default=None, help="限制下载的故事数量 (可与 -n, -g 搭配使用)")
  
  parser.add_argument("--refresh", "-r", action="store_true", help="强制从远端重新下载并刷新本地 manifest.json",
)
  
  return parser.parse_args()

def main():
  # 解析参数 (todo)
  args = parse_args()
  
  print("--- 命令行参数解析结果 ---")
  print(f"目标名称 (-n): {args.name}")
  print(f"目标分组 (-g): {args.group}")
  print(f"数量限制 (-l): {args.limit}")
  
  manifest_data = get_manifest("manifest.json", refresh=args.refresh)
  
  if not args.name and not args.group and args.limit is None:
    print("\n模式: 默认模式 (准备下载全部任务)")
  else:
    print("\n模式: 自定义过滤模式")

if __name__ == "__main__":
  main()