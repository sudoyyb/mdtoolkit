import re
from pathlib import Path

_FENCE = re.compile(r"^\s*(```|~~~)")
_HEADING = re.compile(r"^(#{1,6})\s*(.*?)\s*$")
_ULIST = re.compile(r"^(\s*)[*+]\s+(.*)$")


def normalize(text: str) -> str:
    out, in_fence = [], False
    for line in text.splitlines():
        if _FENCE.match(line):
            in_fence = not in_fence
            out.append(line.rstrip())
            continue
        if in_fence:
            out.append(line)
            continue
        m = _HEADING.match(line)
        if m and line.lstrip().startswith("#"):
            line = f"{m.group(1)} {m.group(2)}"
        m = _ULIST.match(line)
        if m:
            line = f"{m.group(1)}- {m.group(2)}"
        out.append(line.rstrip())
    collapsed, blank = [], False
    for line in out:
        if line == "":
            if blank:
                continue
            blank = True
        else:
            blank = False
        collapsed.append(line)
    return "\n".join(collapsed) + "\n"


def run(args) -> int:
    path = Path(args.file)
    if not path.is_file():
        print(f"错误:文件不存在 {path}")
        return 1
    result = normalize(path.read_text(encoding="utf-8"))
    if args.write:
        path.write_text(result, encoding="utf-8")
        print(f"已格式化并写回 {path}")
    else:
        print(result, end="")
    return 0
