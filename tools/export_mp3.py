"""큐 순서대로 번호를 붙인 mp3 묶음(zip) 만들기: python tools/export_mp3.py
결과: download/저승공무원_음향큐_mp3.zip (mp3 + 00_큐순서.txt)
     download/mp3/  큐별 mp3 (개별 다운로드)  ·  download/files.js  플레이어의 큐별 'mp3 ↓' 링크 목록"""
import shutil
import json, os, re, subprocess, zipfile, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = open(os.path.join(ROOT, "cues.js"), encoding="utf-8").read()
cues = json.loads(t[t.index("["):t.rindex("]") + 1])
safe = lambda s: re.sub(r'[\\:*?"<>|]', "", s.replace("/", "-")).replace(" ", "_")[:40]
os.makedirs(os.path.join(ROOT, "download"), exist_ok=True)
MP3DIR = os.path.join(ROOT, "download", "mp3")
shutil.rmtree(MP3DIR, ignore_errors=True); os.makedirs(MP3DIR)
dl = {}
out = os.path.join(ROOT, "download", "저승공무원_음향큐_mp3.zip")
lines = ["저승공무원으로 취업했습니다!!! — 음향 큐 순서", "번호 = 재생 순서 · 정지 큐는 파일 없음", ""]
with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as z:
    n = 0
    for c in cues:
        n += 1
        head = f"{n:02d}. [{c['id']}] {c.get('scene','')} · {c['title']}"
        timing = f"     GO: {c.get('timing','')}"
        if c["type"] == "stop":
            lines += [head + "  (정지 큐 — 소리 없음)", timing]; continue
        src = os.path.join(ROOT, c["src"].split("?")[0])
        if not os.path.exists(src):
            lines += [head + f"  (파일 없음 — {'유튜브 https://www.youtube.com/watch?v=' + c['youtube'] if c.get('youtube') else '직접 준비'})", timing]; continue
        name = f"{n:02d}_{c['id']}_{safe(c['title'])}.mp3"
        dst = os.path.join(tmp, name)
        if src.endswith(".mp3"):
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-c", "copy", "-map_metadata", "-1", dst], check=True)
        else:
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-b:a", "192k", dst], check=True)
        z.write(dst, name)
        shutil.copy(dst, os.path.join(MP3DIR, name)); dl[c["id"]] = "download/mp3/" + name
        extra = " · 반복" if c.get("loop") else ""
        lines += [head + f"  → {name}  ({c.get('dur','?')}초{extra})", timing]
        if "녹음 대사:" in c.get("note", ""): lines.append("     " + c["note"].split(" · ")[0])
        for l in c.get("lines", []): lines.append("       " + l)
    z.writestr("00_큐순서.txt", "\n".join(lines) + "\n")
open(os.path.join(MP3DIR, "00_큐순서.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
open(os.path.join(ROOT, "download", "files.js"), "w", encoding="utf-8").write("window.DL = " + json.dumps(dl, ensure_ascii=False, indent=1) + ";\n")
print(out, os.path.getsize(out) // 1024, "KB")
print("\n".join(lines))
