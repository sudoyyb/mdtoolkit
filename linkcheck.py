import re
import urllib.request
from pathlib import Path

_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_FENCE = re.compile(r"^\s*(```|~~~)")


def extract_links(lines):
    links, in_fence = [], False
    for lineno, line in enumerate(lines, start=1):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in _LINK.finditer(line):
            target = m.group(1).strip().split()[0]
            links.append((lineno, target))
    return links


def check_relative(target, base_dir):
    path_part = target.split("#")[0]
    if not path_part:
        return True
    return (base_dir / path_part).exists()


def check_http(url, timeout=5):
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status < 400
    except Exception:
        return False


def run(args) -> int:
    path = Path(args.file)
    if not path.is_file():
        print(f"错误:文件不存在 {path}")
        return 1
    lines = path.read_text(encoding="utf-8").splitlines()
    bad = []
    for lineno, target in extract_links(lines):
        if target.startswith(("http://", "https://")):
            ok, reason = check_http(target), "无法访问"
        elif target.startswith(("mailto:", "#")):
            continue
        else:
            ok, reason = check_relative(target, path.parent), "文件不存在"
        if not ok:
            bad.append((lineno, target, reason))
    for lineno, target, reason in bad:
        print(f"{path.name}:{lineno}  坏链: {target} ({reason})")
    if bad:
        print(f"发现 {len(bad)} 处坏链")
        return 1
    print("未发现坏链")
    return 0