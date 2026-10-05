import re
from pathlib import Path
from typing import Any

TAG_RE = re.compile(r"<[^>]+>")
GENDER_RE = re.compile(r"\{Male=([^;{}]+);Female=([^;{}]+)\}")


def clean_text(text: str | None) -> str:
    if not text:
        return ""
    text = GENDER_RE.sub(r"\1/\2", text)
    text = text.replace("{TA}", "TA")
    text = TAG_RE.sub("", text)
    return text.strip()


def json_to_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = []

    # 1. 标题与元信息头
    title = clean_text(data.get("name", "未命名故事"))
    desc = clean_text(data.get("description", ""))
    group = clean_text(data.get("typeDescription", "任务"))
    version = clean_text(
        data.get("versionTag") or data.get("taskMeta", {}).get("versionTag", "")
    )

    lines.append(f"# {title}\n")
    meta = [f"**任务分类**: {group}"]
    if version:
        meta.append(f"**版本**: {version}")
    lines.append(f"- {' | '.join(meta)}")
    if desc:
        lines.append(f"- **剧情简介**: {desc}\n")
    lines.append("---\n")

    # 2. 章节提取与首末顺序矫正
    raw_chapters = data.get("displayChapters") or data.get("taskChapters", [])
    chapters = []
    quest_data_chaps = []
    for c in raw_chapters:
        if c.get("kind") == "quest-data":
            quest_data_chaps.append(c)
        else:
            chapters.append(c)
    chapters = quest_data_chaps + chapters

    # 3. 逐个渲染所有流程节点
    for chap in chapters:
        chap_title = clean_text(chap.get("title", ""))
        dialogues = chap.get("dialogues", [])

        # 只要有标题就必须输出（即使 dialogues 为空，也保留任务目标节点）
        if chap_title:
            lines.append(f"## {chap_title}\n")

        for d in dialogues:
            speaker = clean_text(d.get("speaker", ""))
            text = clean_text(d.get("text", ""))
            options = [
                clean_text(opt.get("text", ""))
                for opt in d.get("options", [])
                if clean_text(opt.get("text", ""))
            ]

            # 纯选项挂载点
            if not text and options:
                for opt in options:
                    lines.append(f"  - 🔘 **[选项]** {opt}")
                lines.append("")
                continue

            if not text and not options:
                continue

            # 旁白 / 动作 / 系统通知
            if not speaker:
                lines.append(f"> 💬 *{text}*\n")
            else:
                lines.append(f"**{speaker}**：{text}\n")

            if options:
                for opt in options:
                    lines.append(f"  - 🔘 **[选项]** {opt}")
                lines.append("")

        lines.append("")  # 节点之间保持标准留白

    return "\n".join(lines)


def get_available_path(output_dir: Path, base_name: str) -> Path:
    """按 base.md, base2.md, base3.md 顺位获取尚未被占用的文件路径"""
    candidate = output_dir / f"{base_name}.md"
    if not candidate.exists():
        return candidate

    idx = 2
    while True:
        candidate = output_dir / f"{base_name}{idx}.md"
        if not candidate.exists():
            return candidate
        idx += 1


def save_markdown_file(data: dict[str, Any], output_dir: Path) -> Path:
    title = clean_text(data.get("name", "story"))
    safe_title = re.sub(r'[\\/*?:"<>|]', "_", title).strip() or "story"

    target_path = get_available_path(output_dir, safe_title)
    md_content = json_to_markdown(data)
    target_path.write_text(md_content, encoding="utf-8")

    return target_path
