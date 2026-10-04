import json
import os

import urllib.request


MANIFEST_URL = "https://mc.yakitahome.com/api/story-archive/manifest"


def fetch_manifest(url: str = MANIFEST_URL) -> dict:
  """从网络接口抓取 manifest 数据"""
  print(f"[*] 正在从远端下载 Manifest: {url} ...")
  req = urllib.request.Request(url,
    headers={
      "User-Agent": "Mozilla/5.0",
      "Referer": "https://mc.yakitahome.com/story"
    }
  )
  with urllib.request.urlopen(req) as resp:
    content = resp.read().decode("utf-8")
    return json.loads(content)
  
def get_manifest(file_path: str = "manifest.json", refresh: bool = False) -> dict:
  """如果指定refresh为 True，或者本地文件不存在，才从远端拉取"""
  
  # refresh == False 并且 本地文件存在
  if not refresh and os.path.exists(file_path):
    print(f"[*] 检测到本地存在 {file_path}，使用本地缓存。")
    with open(file_path, "r", encoding="utf-8") as f:
      return json.load(f)
    
  # 按需更新
  print(f"[*] 正在按需更新 Manifest 缓存...")
  data = fetch_manifest()
  with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
  print(f"[*] 本地 {file_path} 已刷新至最新状态。")
  return data
