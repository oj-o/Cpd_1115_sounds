#!/usr/bin/env python3
"""
저승공무원으로 취업했습니다!!! — 조명 큐 파일 생성기 (MA dot2)

조명 큐는 엑셀로 여는 CSV 파일 4개에 들어 있습니다. 이 파일들을 고친 뒤 이 프로그램을 돌리면
dot2 명령 목록과 인쇄용 큐시트가 새로 만들어지고, dot2 onPC에 자동으로 입력할 수 있습니다.

  cues.csv     큐 목록: 큐 번호, 이름, 페이드, '명령' 칸 (예: spot on, bg 30 blue, off, A)
  looks.csv    자주 쓰는 룩 이름 ↔ 명령 (예: A = front 70, top 60, wash 50, bg 30, office)
  patch.csv    장비 ID와 DMX 주소
  groups.csv   그룹 번호, 이름, 장비 선택
  presets.csv  프리셋 이름 ↔ dot2 프리셋 번호

  python dot2_cues.py build          검사 → dot2_commands.txt, cue_sheet.html 생성 (어디서나 실행 가능)
  python dot2_cues.py check          파일 검사만
  python dot2_cues.py type 1         1단계(패치 주소 + 그룹) 자동 입력  ← Windows + dot2 onPC
  python dot2_cues.py type 2         2단계(큐) 자동 입력
  python dot2_cues.py type 2 --from 40   40번째 줄부터 이어서

자동 입력 중 멈추려면 마우스를 화면 왼쪽 위 모서리로 옮기세요.
"""
import sys, time, argparse, os, csv, html, re

HERE = os.path.dirname(os.path.abspath(__file__))
FIXED_COLS = ["큐", "이름", "대본표시", "GO 타이밍", "Fade", "Trig", "음향", "메모"]
TYPEABLE = re.compile(r"^[A-Za-z0-9 .\-+]*$")   # dot2에 자동으로 입력할 수 있는 글자

class CueFileError(Exception):
    pass

# ───────────── CSV 읽기 ─────────────
def read_csv(name):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        raise CueFileError(f"{name} 파일이 없습니다.")
    for enc in ("utf-8-sig", "cp949"):            # 엑셀이 한국어 윈도우에서 저장하면 cp949가 될 수 있음
        try:
            with open(path, newline="", encoding=enc) as f:
                rows = [r for r in csv.DictReader(f)]
            return [{(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in rows
                    if any((v or "").strip() for v in r.values())]
        except UnicodeDecodeError:
            continue
    raise CueFileError(f"{name}의 글자 인코딩을 읽을 수 없습니다. 'CSV UTF-8'로 다시 저장하세요.")

def num(text):
    """'4.10'·'4.1'·'10.0' 같은 엑셀 표기를 dot2 표기로 정리"""
    f = float(text)
    return f"{f:g}"

def load():
    errs = []
    patch = []
    for i, r in enumerate(read_csv("patch.csv"), 2):
        try:
            fid = int(float(r["ID"]))
        except (ValueError, KeyError):
            errs.append(f"patch.csv {i}행: ID '{r.get('ID')}'가 숫자가 아닙니다."); continue
        dmx = r.get("DMX", "")
        if dmx and not re.fullmatch(r"[1-4]\.\d{1,3}", dmx):
            errs.append(f"patch.csv {i}행: DMX '{dmx}'는 '유니버스.주소' 형식(예: 2.96)이어야 합니다.")
        elif dmx and not 1 <= int(dmx.split(".")[1]) <= 512:
            errs.append(f"patch.csv {i}행: DMX 주소는 1~512입니다 ({dmx}).")
        patch.append((fid, dmx, r.get("장비", ""), r.get("위치", "")))
    ids = [p[0] for p in patch]
    for d in sorted({x for x in ids if ids.count(x) > 1}):
        errs.append(f"patch.csv: ID {d}가 두 번 나옵니다.")
    used = [p[1] for p in patch if p[1]]
    for d in sorted({x for x in used if used.count(x) > 1}):
        errs.append(f"patch.csv: DMX {d}가 두 장비에 겹칩니다.")

    groups = []
    for i, r in enumerate(read_csv("groups.csv"), 2):
        try:
            g = int(float(r["그룹"]))
        except (ValueError, KeyError):
            errs.append(f"groups.csv {i}행: 그룹 번호가 숫자가 아닙니다."); continue
        name, sel = r.get("이름", ""), r.get("선택", "")
        if not TYPEABLE.match(name): errs.append(f"groups.csv {i}행: 그룹 이름 '{name}'은 영문·숫자로만 써야 dot2에 입력됩니다.")
        if not TYPEABLE.match(sel) or not sel.startswith("Fixture"): errs.append(f"groups.csv {i}행: 선택 '{sel}'은 'Fixture 1 Thru 6 + 13' 형식이어야 합니다.")
        exp = r.get("대수", "")
        yes = lambda k: r.get(k, "").upper() in ("O", "Y", "YES", "1", "TRUE")
        groups.append(dict(no=g, name=name, sel=sel, expected=int(float(exp)) if exp else None,
                           reset=yes("매 큐 0으로 초기화"), color=yes("색·위치"),
                           alias=[a.strip().lower() for a in r.get("별칭", "").split("/") if a.strip()]))
    gby = {g["name"]: g for g in groups}

    presets = {}
    for i, r in enumerate(read_csv("presets.csv"), 2):
        try:
            presets[r["이름"]] = (num(r["dot2 프리셋"]), r.get("종류", ""), r.get("설명", ""),
                                 [a.strip().lower() for a in r.get("별칭", "").split("/") if a.strip()])
        except (ValueError, KeyError):
            errs.append(f"presets.csv {i}행: dot2 프리셋 번호 '{r.get('dot2 프리셋')}'가 '4.1' 같은 형식이 아닙니다.")

    looks = {}
    if os.path.exists(os.path.join(HERE, "looks.csv")):
        for r in read_csv("looks.csv"):
            if r.get("룩"): looks[r["룩"].lower()] = r.get("명령", "")
    P = Parser(groups, presets, looks)

    raw = read_csv("cues.csv")
    cols = list(raw[0].keys()) if raw else []
    level_cols, attr_cols = [], []
    for c in cols:
        if c in FIXED_COLS or c == "명령": continue
        m = re.fullmatch(r"(.+) (색|위치)", c)
        if m:
            if m.group(1) not in gby: errs.append(f"cues.csv: '{c}' 열의 그룹 '{m.group(1)}'이 groups.csv에 없습니다.")
            else: attr_cols.append((c, m.group(1), m.group(2)))
        elif c in gby: level_cols.append(c)
        else: errs.append(f"cues.csv: '{c}' 열을 알 수 없습니다. 명령, 그룹 이름, '그룹 색', '그룹 위치' 중 하나여야 합니다.")
    cues, seen = [], set()
    for i, r in enumerate(raw, 2):
        try:
            no = num(r["큐"]); nf = float(no)
        except (ValueError, KeyError):
            errs.append(f"cues.csv {i}행: 큐 번호 '{r.get('큐')}'가 숫자가 아닙니다."); continue
        if no in seen: errs.append(f"cues.csv {i}행: 큐 {no}가 두 번 나옵니다.")
        if cues and nf <= float(cues[-1]["no"]): errs.append(f"cues.csv {i}행: 큐 {no}가 앞 큐({cues[-1]['no']})보다 작습니다. 큐는 오름차순이어야 합니다.")
        seen.add(no)
        name = r.get("이름", "")
        if not TYPEABLE.match(name): errs.append(f"cues.csv {i}행: 큐 이름 '{name}'은 영문·숫자로만 써야 dot2에 입력됩니다. 한글 설명은 'GO 타이밍'이나 '메모'에 쓰세요.")
        try:
            fade = num(r.get("Fade") or "0")
            if float(fade) < 0: raise ValueError
        except ValueError:
            errs.append(f"cues.csv {i}행: Fade '{r.get('Fade')}'는 0 이상 숫자(초)여야 합니다."); fade = "0"
        lv, at = {}, {}          # 그룹이름 → 값 / (그룹이름, 종류) → 프리셋이름
        for g in groups:
            if g["reset"]: lv[g["name"]] = 0
        cmd = r.get("명령", "")
        if cmd:
            for msg in P.apply(cmd, lv, at): errs.append(f"cues.csv {i}행 명령 '{cmd}': {msg}")
        else:                    # 예전 방식: 그룹별 숫자 칸
            for g in groups:
                if g["name"] not in level_cols: continue
                v = r.get(g["name"], "")
                if v == "": continue
                try:
                    x = float(v)
                    if not 0 <= x <= 100: raise ValueError
                    lv[g["name"]] = int(x) if x == int(x) else x
                except ValueError:
                    errs.append(f"cues.csv {i}행: {g['name']} 레벨 '{v}'는 0~100이어야 합니다.")
            for c, gname, kind in attr_cols:
                p = r.get(c, "")
                if not p: continue
                if p not in presets: errs.append(f"cues.csv {i}행: '{c}'의 프리셋 '{p}'이 presets.csv에 없습니다.")
                else: at[(gname, kind)] = p
        # 초기화 그룹을 먼저, 그 일부를 덮어쓰는 그룹(Spot Solo 등)을 나중에 입력
        levels = sorted(((gby[n], v) for n, v in lv.items()), key=lambda t: (not t[0]["reset"], groups.index(t[0])))
        attrs = sorted(((gby[n], presets[p][0], k, p) for (n, k), p in at.items()),
                       key=lambda t: (t[2] == "위치", groups.index(t[0])))
        trig = (r.get("Trig") or "Go").strip()
        if trig.lower() not in ("go", "follow"): errs.append(f"cues.csv {i}행: Trig는 Go 또는 Follow입니다 ('{trig}').")
        cues.append(dict(no=no, name=name, fade=fade, trig="Follow" if trig.lower() == "follow" else "Go",
                         levels=levels, attrs=attrs, lv=lv, cmd=cmd, script=r.get("대본표시", ""), timing=r.get("GO 타이밍", ""),
                         sound=r.get("음향", ""), memo=r.get("메모", ""), raw=r))
    # 큐시트에 보일 그룹: 초기화 그룹 + 한 번이라도 쓰인 그룹
    used_g = {n for c in cues for n in c["lv"]}
    level_cols = [g["name"] for g in groups if g["reset"] or g["name"] in used_g]
    for g in groups:
        if g["expected"]:
            n = count_selection(g["sel"], set(ids))
            if n is not None and n != g["expected"]:
                errs.append(f"groups.csv: {g['name']} 선택 '{g['sel']}'은 patch.csv 기준 {n}대인데 대수 칸은 {g['expected']}입니다.")
    if errs:
        raise CueFileError("\n".join(errs))
    return dict(patch=patch, groups=groups, presets=presets, looks=looks, cues=cues, level_cols=level_cols)

class Parser:
    """'명령' 칸 해석기.  쉼표로 나눈 항목을 왼쪽부터 차례로 적용합니다.
      off / bo / 암전          모든 '매 큐 0' 그룹을 0으로 (명령을 안 쓴 그룹도 원래 0)
      spot on / spot off       100 / 0          spot 70      레벨 70
      all on / all 60          Blinder·House·Fog를 뺀 '매 큐 0' 그룹 전체
      bg 30 blue               레벨 + 색 프리셋   spot solo 70 amber desk  레벨 + 색 + 위치
      blue                     그룹 없이 색만 쓰면, 그 시점에 켜져 있는 색·위치 그룹 전부에 적용
      A                        looks.csv의 룩을 그대로 펼침 (뒤에 항목을 더 써서 덮어쓸 수 있음)
    그룹·프리셋 이름은 대소문자 구분 없음, groups.csv·presets.csv의 '별칭'(예: 스팟, 블루)도 됩니다."""
    ALL_EXCLUDE = {"blinder", "house", "fog"}
    ON, OFF = {"on", "켬", "full"}, {"off", "끔"}

    def __init__(self, groups, presets, looks):
        self.groups, self.presets, self.looks = groups, presets, looks
        self.gnames = []                      # (토큰 목록, 그룹) — 긴 이름 먼저
        for g in groups:
            for n in [g["name"].lower()] + g["alias"]:
                self.gnames.append((n.split(), g))
        self.gnames.sort(key=lambda t: -len(t[0]))
        self.pnames = {}
        for p, v in presets.items():
            for n in [p.lower()] + v[3]: self.pnames[n] = p

    def apply(self, text, lv, at, depth=0):
        errs = []
        if depth > 5: return ["룩이 서로를 계속 부릅니다."]
        for item in [x.strip() for x in re.split(r"[,;/]", text) if x.strip()]:
            low = item.lower()
            toks = low.split()
            if low in self.looks:
                errs += self.apply(self.looks[low], lv, at, depth + 1); continue
            if low in ("off", "bo", "blackout", "암전", "all off"):
                for g in self.groups:
                    if g["reset"]: lv[g["name"]] = 0
                continue
            targets, rest = None, toks
            if toks[0] in ("all", "전체"):
                targets = [g for g in self.groups if g["reset"] and g["name"].lower() not in self.ALL_EXCLUDE]; rest = toks[1:]
            else:
                for ntoks, g in self.gnames:
                    if toks[:len(ntoks)] == ntoks:
                        targets, rest = [g], toks[len(ntoks):]; break
            if targets is None:            # 그룹 없이 프리셋만: 색은 켜진 색·위치 그룹 전부에
                for t in toks:
                    p = self.pnames.get(t)
                    if not p: errs.append(f"'{t}'는 그룹·프리셋·룩 이름이 아닙니다."); continue
                    kind = self.presets[p][1]
                    if kind == "위치": errs.append(f"위치 프리셋 '{p}'는 그룹과 함께 쓰세요 (예: spot {p.lower()})."); continue
                    on = [g for g in self.groups if g["color"] and lv.get(g["name"], 0) > 0]
                    if not on: errs.append(f"'{p}'를 받을 켜진 색 그룹이 없습니다. 그룹 레벨을 먼저 쓰세요.")
                    for g in on: at[(g["name"], kind)] = p
                continue
            if not rest: errs.append(f"'{item}': 그룹 뒤에 on/off, 숫자, 프리셋 중 하나를 쓰세요."); continue
            for t in rest:
                if t in self.ON: val = 100
                elif t in self.OFF: val = 0
                elif re.fullmatch(r"\d+(\.\d+)?%?", t):
                    val = float(t.rstrip("%"))
                    if val > 100: errs.append(f"'{item}': 레벨 {t}는 0~100이어야 합니다."); continue
                    val = int(val) if val == int(val) else val
                else:
                    p = self.pnames.get(t)
                    if not p: errs.append(f"'{item}': '{t}'를 알 수 없습니다."); continue
                    kind = self.presets[p][1]
                    for g in targets:
                        if not g["color"]: errs.append(f"'{item}': {g['name']}는 색·위치가 없는 디머 그룹입니다."); continue
                        at[(g["name"], kind)] = p
                    continue
                for g in targets: lv[g["name"]] = val
        return errs

def count_selection(sel, ids):
    body = sel.replace("Fixture", "", 1)
    total = set()
    for part in body.split("+"):
        m = re.fullmatch(r"\s*(\d+)\s*(?:Thru\s*(\d+))?\s*", part, re.I)
        if not m: return None
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        total |= {x for x in range(a, b + 1) if x in ids}
    return len(total)

# ───────────── 명령 생성 ─────────────
def stage1(D):
    out = [("note", "1단계: 패치 주소 지정")]
    for fid, dmx, _, _ in D["patch"]:
        if dmx: out.append(("cmd", f"Assign Fixture {fid} At DMX {dmx}"))
    out.append(("note", "1단계: 그룹 저장 (값을 하나 넣어 선택을 닫아야 다음 선택이 새로 시작됩니다)"))
    for g in D["groups"]:
        out += [("cmd", g["sel"]), ("cmd", f"Store Group {g['no']}"), ("cmd", f"Label Group {g['no']}"), ("name", g["name"]), ("cmd", "At 0")]
    return out

def stage2(D):
    out = []
    for c in D["cues"]:
        out.append(("note", f"큐 {c['no']} {c['name']}"))
        for g, v in c["levels"]:
            out.append(("cmd", f"Group {g['no']} At {v}"))
        for g, p, _, _ in c["attrs"]:
            out.append(("cmd", f"Group {g['no']} At Preset {p}"))
        out.append(("cmd", f"Store Cue {c['no']} Fade {c['fade']}"))
        if c["name"]: out += [("cmd", f"Label Cue {c['no']}"), ("name", c["name"])]
    return out

def numbered(items):
    n = 0; rows = []
    for kind, text in items:
        if kind == "note": rows.append((None, kind, text))
        else: n += 1; rows.append((n, kind, text))
    return rows

def write_commands(D, path):
    lines = ["# dot2 명령 목록 — dot2_cues.py가 cues.csv 등으로 만든 파일입니다. 직접 고치지 말고 CSV를 고친 뒤 다시 만드세요.",
             "# [이름창] 줄은 앞 줄(Label)을 입력하면 뜨는 이름 입력 창에 넣는 글자입니다.", ""]
    for title, items in (("1단계 — 패치 주소 + 그룹", stage1(D)), ("2단계 — 큐", stage2(D))):
        lines.append(f"########## {title} ##########")
        for n, kind, text in numbered(items):
            if kind == "note": lines.append(f"\n# {text}")
            elif kind == "name": lines.append(f"{n:4d}  [이름창] {text}")
            else: lines.append(f"{n:4d}  {text}")
        lines.append("")
    lines.append("########## 프리셋 (2단계 전에 직접 저장) ##########")
    for nm, (k, kind, desc, _) in D["presets"].items(): lines.append(f"Preset {k}  {nm:8s} {kind}: {desc}")
    follow = [c["no"] for c in D["cues"] if c["trig"] == "Follow"]
    if follow: lines.append(f"\n# 2단계 후 손으로: 큐 {', '.join(follow)}의 Trig를 Follow로 바꾸세요.")
    with open(path, "w", encoding="utf-8") as f: f.write("\n".join(lines) + "\n")

def write_sheet(D, path):
    """인쇄용 조명 큐시트 (브라우저로 열어 인쇄)"""
    e = html.escape
    lv = D["level_cols"]
    head = "".join(f"<th class='lv'>{e(c)}</th>" for c in lv)
    rows = []
    for c in D["cues"]:
        cells = "".join(f"<td class='lv{' z' if not c['lv'].get(n) else ''}'>{e(str(c['lv'][n])) if n in c['lv'] else '·'}</td>" for n in lv)
        attrs = ", ".join("%s %s" % (g["name"], e(p)) for g, _, _, p in c["attrs"])
        if c["cmd"]: attrs = f"<b>{e(c['cmd'])}</b><br>" + attrs
        rows.append(f"<tr class='{'follow' if c['trig'] == 'Follow' else ''}'><td class='no'>{e(c['no'])}</td><td>{e(c['script'])}</td>"
                    f"<td class='go'>{e(c['timing'])}</td><td>{e(c['name'])}</td><td class='t'>{e(c['fade'])}s</td><td>{e(c['trig'])}</td>"
                    f"<td class='t'>{e(c['sound'])}</td>{cells}<td class='attr'>{attrs}</td><td>{e(c['memo'])}</td></tr>")
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>조명 큐시트</title><style>
@page {{ size: A4 landscape; margin: 10mm; }}
body {{ font-family: "Malgun Gothic","Apple SD Gothic Neo","Noto Sans KR",Arial,sans-serif; font-size: 10.5px; color: #111; margin: 16px; }}
h1 {{ font-size: 16px; margin: 0 0 4px; }} p {{ margin: 0 0 8px; color: #555; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #999; padding: 3px 4px; vertical-align: top; }}
th {{ background: #e9e7f2; font-weight: 700; }}
td.no {{ font-weight: 800; font-size: 13px; text-align: center; white-space: nowrap; }}
td.go {{ font-weight: 600; min-width: 150px; }}
td.lv, th.lv {{ text-align: center; width: 34px; font-variant-numeric: tabular-nums; }}
td.z {{ color: #bbb; }} td.t {{ text-align: center; white-space: nowrap; }}
td.attr {{ font-size: 9.5px; color: #333; }}
tr.follow td {{ background: #fff6e0; }}
tr {{ page-break-inside: avoid; }}
</style></head><body>
<h1>저승공무원으로 취업했습니다!!! · 조명 큐시트 (MA dot2)</h1>
<p>cues.csv에서 자동 생성 · 레벨 단위 % · 노란 줄은 Trig Follow(앞 큐 뒤 자동 진행) · ♪는 동시에 나가는 음향 큐 번호</p>
<table><thead><tr><th>큐</th><th>대본</th><th>GO 타이밍</th><th>이름</th><th>Fade</th><th>Trig</th><th>♪</th>{head}<th>명령 → 색·위치</th><th>메모</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></body></html>"""
    with open(path, "w", encoding="utf-8") as f: f.write(doc)

# ───────────── Windows 자동 타이핑 ─────────────
def typer():
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    ULONG_PTR = ctypes.c_size_t
    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]
    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                    ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]
    class _U(ctypes.Union): _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT)]
    class INPUT(ctypes.Structure): _fields_ = [("type", wintypes.DWORD), ("u", _U)]
    KEYUP, SHIFT = 0x0002, 0x10
    VK = {" ": 0x20, ".": 0xBE, "+": 0xBB, "-": 0xBD, "\n": 0x0D}

    def key(vk, up=False):
        sc = user32.MapVirtualKeyW(vk, 0)
        i = INPUT(type=1, u=_U(ki=KEYBDINPUT(vk, sc, KEYUP if up else 0, 0, 0)))
        user32.SendInput(1, ctypes.byref(i), ctypes.sizeof(INPUT))

    def char(c, delay):
        shift = c.isupper() or c == "+"
        vk = VK.get(c) or ord(c.upper())
        if shift: key(SHIFT)
        key(vk); key(vk, True)
        if shift: key(SHIFT, True)
        time.sleep(delay)

    def english_layout():   # 한글 입력 상태면 명령이 깨지므로 영문(US) 자판으로 전환 요청
        hwnd = user32.GetForegroundWindow()
        hkl = user32.LoadKeyboardLayoutW("00000409", 1)
        user32.PostMessageW(hwnd, 0x0050, 0, hkl)

    def corner():
        pt = wintypes.POINT(); user32.GetCursorPos(ctypes.byref(pt)); return pt.x <= 2 and pt.y <= 2

    return char, english_layout, corner

def run_type(D, stage, start, delay):
    if os.name != "nt":
        sys.exit("자동 입력은 Windows에서 dot2 onPC를 켠 상태로 실행하세요. (파일만 만들려면: python dot2_cues.py build)")
    char, english_layout, corner = typer()
    rows = [r for r in numbered(stage1(D) if stage == 1 else stage2(D)) if r[0] is not None]
    total = rows[-1][0]
    print(f"{stage}단계: 총 {total}줄. {start}번째 줄부터 입력합니다.")
    print("지금 dot2 onPC의 명령줄(Command Line)을 한 번 클릭해 두세요. 5초 뒤 시작합니다.")
    print("멈추려면 마우스를 화면 왼쪽 위 모서리로 옮기세요.")
    for s in range(5, 0, -1): print(f"  {s}…", end="", flush=True); time.sleep(1)
    print(); english_layout(); time.sleep(0.3)
    for n, kind, text in rows:
        if n < start: continue
        if corner():
            print(f"\n멈춤. 이어서 하려면:  python dot2_cues.py type {stage} --from {n}"); return
        print(f"{n:4d}/{total}  {'[이름창] ' if kind == 'name' else ''}{text}")
        for c in text: char(c, delay)
        char("\n", delay)
        wait = 0.35
        if text.startswith("Store"): wait = 0.9
        if text.startswith("Label"): wait = 1.0           # 이름 입력 창이 뜨는 시간
        if kind == "name": wait = 0.7
        time.sleep(wait)
    print(f"\n{stage}단계 완료.")
    if stage == 1:
        print("Group 풀에서 대수를 확인하세요:", ", ".join(f"{g['name']} {g['expected']}" for g in D["groups"] if g["expected"]))
    else:
        follow = [c["no"] for c in D["cues"] if c["trig"] == "Follow"]
        print(f"Cues 창에서 큐 {D['cues'][0]['no']}~{D['cues'][-1]['no']}를 확인하세요."
              + (f" 큐 {', '.join(follow)}의 Trig를 Follow로 바꾼 뒤" if follow else "") + " 쇼를 저장하세요.")

def main():
    ap = argparse.ArgumentParser(description="dot2 조명 큐 파일 생성기")
    ap.add_argument("mode", choices=["build", "check", "type", "list"])
    ap.add_argument("stage", nargs="?", type=int, choices=[1, 2])
    ap.add_argument("--from", dest="start", type=int, default=1)
    ap.add_argument("--delay", type=float, default=0.03, help="글자 사이 간격(초). 글자가 빠지면 0.06으로")
    a = ap.parse_args()
    try:
        D = load()
    except CueFileError as ex:
        print("큐 파일에 고칠 곳이 있습니다:\n" + str(ex)); sys.exit(1)
    n1 = len([r for r in numbered(stage1(D)) if r[0]]); n2 = len([r for r in numbered(stage2(D)) if r[0]])
    if a.mode == "check":
        print(f"이상 없음 · 장비 {len(D['patch'])}대, 그룹 {len(D['groups'])}개, 프리셋 {len(D['presets'])}개, 큐 {len(D['cues'])}개 (명령 {n1}+{n2}줄)")
    elif a.mode in ("build", "list"):
        write_commands(D, os.path.join(HERE, "dot2_commands.txt"))
        write_sheet(D, os.path.join(HERE, "cue_sheet.html"))
        print(f"만들었습니다 · dot2_commands.txt (1단계 {n1}줄, 2단계 {n2}줄), cue_sheet.html (큐 {len(D['cues'])}개)")
    else:
        if not a.stage: ap.error("type 다음에 1 또는 2를 쓰세요")
        run_type(D, a.stage, a.start, a.delay)

if __name__ == "__main__":
    main()
