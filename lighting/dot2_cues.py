#!/usr/bin/env python3
"""
저승공무원으로 취업했습니다!!! — MA dot2 조명 큐 자동 입력기

dot2는 외부 파일로 쇼를 불러오는 기능이 없어서, 이 스크립트가 dot2 onPC의 명령줄에
명령을 대신 타이핑해 쇼를 만듭니다. 완성된 쇼 파일을 USB로 콘솔(dot2 core)에 옮기면 됩니다.

  python dot2_cues.py list            명령 목록을 화면과 dot2_commands.txt로 출력 (어디서나 실행 가능)
  python dot2_cues.py type 1          1단계(패치 주소 + 그룹) 자동 입력  ← Windows + dot2 onPC
  python dot2_cues.py type 2          2단계(큐) 자동 입력
  python dot2_cues.py type 2 --from 40  중간에 멈췄을 때 40번째 줄부터 다시

자동 입력 중 멈추려면 마우스를 화면 왼쪽 위 모서리로 옮기세요.
"""
import sys, time, argparse, os

# ───────────── 1. 장비 (패치는 2026.06.22 극장 도면 기준) ─────────────
# (Fixture ID, DMX "유니버스.주소" 또는 None=패치 안 함)
FIXTURES = (
    [(101 + i, f"2.{a}") for i, a in enumerate([96, 116, 135, 154, 173])] +      # Diamond19 워시 SUS1
    [(106 + i, f"2.{a}") for i, a in enumerate([1, 20, 39, 58, 77])] +           # Diamond19 워시 SUS2
    [(201 + i, f"2.{a}") for i, a in enumerate([273, 291, 309, 327])] +          # Rogue R2X Spot SUS1
    [(205 + i, f"2.{a}") for i, a in enumerate([201, 219, 237, 255])] +          # Rogue R2X Spot SUS2
    [(301 + i, f"2.{a}") for i, a in enumerate([350, 353, 356, 359, 362])] +     # LED 파 3ch SUS6
    [(306 + i, f"2.{a}") for i, a in enumerate([365, 366, 367, 368, 369])] +     # 1ch 장비 SUS6/SUS4
    [(d, f"1.{d}") for d in list(range(1, 7)) + list(range(13, 25)) + [26, 28, 29] + list(range(32, 38))] +  # 디머 회로
    [(401 + i, None) for i in range(4)] +                                         # 블라인더 (주소 확인 후 수동 패치)
    [(501, "3.505")] +                                                            # 포그 JEM ZR35
    [(601 + i, f"3.{347 + 2 * i}") for i in range(9)] +                           # 하우스 LED 파 2ch
    [(611 + i, f"3.{507 + i}") for i in range(6)]                                 # 하우스 디머
)

# ───────────── 2. 그룹 ─────────────
GROUPS = [  # (번호, 이름, dot2 선택 문법)
    (1, "Spot",      "Fixture 201 Thru 208"),
    (2, "Wash",      "Fixture 101 Thru 110"),
    (3, "Front",     "Fixture 1 Thru 6 + 13 Thru 18"),
    (4, "Top",       "Fixture 19 Thru 24"),
    (5, "Back",      "Fixture 26 + 28 + 29 + 32 Thru 36"),
    (6, "BG",        "Fixture 301 Thru 310 + 37"),
    (7, "Blinder",   "Fixture 401 Thru 404"),
    (8, "House",     "Fixture 601 Thru 616"),
    (9, "Fog",       "Fixture 501"),
    (10, "Spot Solo", "Fixture 202"),
    (11, "Spot Pair", "Fixture 205 + 208"),
]
EXPECTED = {1: 8, 2: 10, 3: 12, 4: 6, 5: 8, 6: 11, 7: 4, 8: 15, 9: 1, 10: 1, 11: 2}

# ───────────── 3. 프리셋 (2단계 전에 직접 만들 것) ─────────────
# 색·위치는 엔코더로만 정할 수 있어서 자동 입력이 불가능합니다. 아래 번호에 미리 저장해 두세요.
PRESETS = {
    "4.1": ("Office",   "색: 차가운 화이트 + 연보라 (Wash·BG·Spot)"),
    "4.2": ("Meeting",  "색: 회의실 웜 화이트 (Wash·BG)"),
    "4.3": ("Amber",    "색: 앰버 (Wash·Spot)"),
    "4.4": ("Blue",     "색: 배경 블루 (BG)"),
    "4.5": ("Curtain",  "색: 커튼콜 멀티 (Wash·BG·Spot)"),
    "2.1": ("DownC",    "위치: 다운센터 독백 (Spot)"),
    "2.2": ("Desk",     "위치: 주인공 책상 (Spot Solo)"),
    "2.3": ("Audit",    "위치: 감사팀장 자리 (Spot Pair)"),
    "2.4": ("Sweep",    "위치: 커튼콜 객석 쪽 (Spot)"),
}

# ───────────── 4. 큐 (대본 빨간 원 기준, 조명 큐 문서와 같은 번호) ─────────────
ALL = [1, 2, 3, 4, 5, 6, 7, 8]   # 매 큐마다 이 그룹들의 값을 모두 명시해 트래킹 꼬임 방지 (포그 9는 페이더로 수동 운용)
SUB = [10, 11]                    # Spot 그룹(1)의 일부. 켤 때만 Group 1 다음에 덮어씀
def look(**lv):  # 지정 안 한 그룹은 0
    d = {g: lv.get(f"g{g}", 0) for g in ALL}
    d.update({g: lv[f"g{g}"] for g in SUB if lv.get(f"g{g}")})
    return d

A = dict(levels=look(g3=70, g4=60, g2=50, g6=30), color={2: "4.1", 6: "4.1"})
BO = dict(levels=look(), color={})
CUES = [  # (큐, 이름, 페이드 초, 상태)
    ("0.5", "Preshow",    0,   dict(levels=look(g8=100, g6=15), color={6: "4.4"})),
    ("1",   "House Out",  5,   BO),
    ("2",   "1 Office",   2,   A),
    ("3",   "2 Meeting",  3,   dict(levels=look(g3=80, g4=60, g2=50, g6=30), color={2: "4.2", 6: "4.2"})),
    ("4",   "3-4 BO",     1,   BO),
    ("5",   "4 Office",   1.5, A),
    ("6",   "7 Audit",    4,   dict(levels=look(g3=55, g4=30, g5=40, g2=30, g6=20, g11=60),
                                    color={2: "4.3", 6: "4.4", 11: "4.3"}, pos={11: "2.3"})),
    ("7",   "7 Spot",     5,   dict(levels=look(g10=70, g3=10, g2=10, g6=10), color={10: "4.3"}, pos={10: "2.2"})),
    ("8",   "7 BO",       3,   BO),
    ("9",   "8 Office",   2,   A),
    ("10",  "9 Full",     10,  dict(levels=look(g3=85, g4=70, g2=60, g5=50, g6=40), color={2: "4.1", 6: "4.1"})),
    ("11",  "CC Bright",  2,   dict(levels=look(g1=100, g2=100, g3=100, g4=100, g5=100, g6=100),
                                    color={1: "4.5", 2: "4.5", 6: "4.5"}, pos={1: "2.4"})),
    ("12",  "CC Blinder", 0,   dict(levels=look(g1=100, g2=100, g3=100, g4=100, g5=100, g6=100, g7=100), color={}, pos={})),
    ("12.5", "CC BO",     0,   BO),
    ("13",  "Bow",        1,   dict(levels=look(g1=100, g2=100, g3=100, g4=100, g5=100, g6=100), color={1: "4.5", 2: "4.5", 6: "4.5"}, pos={1: "2.4"})),
    ("14",  "House In",   5,   dict(levels=look(g8=100), color={})),
]

# ───────────── 명령 생성 ─────────────
# 각 항목: ("cmd", 텍스트) | ("name", 이름창에 입력할 텍스트)
def stage1():
    out = [("note", "1단계: 패치 주소 지정")]
    for fid, dmx in FIXTURES:
        if dmx: out.append(("cmd", f"Assign Fixture {fid} At DMX {dmx}"))
    out.append(("note", "1단계: 그룹 저장 (값을 하나 넣어 선택을 닫아야 다음 선택이 새로 시작됩니다)"))
    for g, name, sel in GROUPS:
        out += [("cmd", sel), ("cmd", f"Store Group {g}"), ("cmd", f"Label Group {g}"), ("name", name), ("cmd", "At 0")]
    return out

def stage2():
    out = []
    for no, name, fade, s in CUES:
        out.append(("note", f"큐 {no} {name}"))
        for g, v in s["levels"].items():
            out.append(("cmd", f"Group {g} At {v}"))
        for g, p in s.get("color", {}).items():
            out.append(("cmd", f"Group {g} At Preset {p}"))
        for g, p in s.get("pos", {}).items():
            out.append(("cmd", f"Group {g} At Preset {p}"))
        out.append(("cmd", f"Store Cue {no} Fade {fade:g}" if isinstance(fade, (int, float)) else f"Store Cue {no}"))
        out += [("cmd", f"Label Cue {no}"), ("name", name)]
    return out

def numbered(items):
    n = 0; rows = []
    for kind, text in items:
        if kind == "note": rows.append((None, kind, text))
        else: n += 1; rows.append((n, kind, text))
    return rows

def write_list(path):
    lines = ["# dot2 명령 목록 — dot2_cues.py가 만든 파일입니다. 손으로 입력할 때도 이 순서대로 쓰면 됩니다.",
             "# [이름창] 줄은 앞 줄(Label)을 입력하면 뜨는 이름 입력 창에 넣는 글자입니다.", ""]
    for title, items in (("1단계 — 패치 주소 + 그룹", stage1()), ("2단계 — 큐", stage2())):
        lines.append(f"########## {title} ##########")
        for n, kind, text in numbered(items):
            if kind == "note": lines.append(f"\n# {text}")
            elif kind == "name": lines.append(f"{n:4d}  [이름창] {text}")
            else: lines.append(f"{n:4d}  {text}")
        lines.append("")
    lines.append("########## 프리셋 (2단계 전에 직접 저장) ##########")
    for k, (nm, desc) in PRESETS.items(): lines.append(f"Preset {k}  {nm:8s} {desc}")
    with open(path, "w", encoding="utf-8") as f: f.write("\n".join(lines) + "\n")
    return "\n".join(lines)

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

def run_type(stage, start, delay):
    if os.name != "nt":
        sys.exit("자동 입력은 Windows에서 dot2 onPC를 켠 상태로 실행하세요. (명령 목록만 보려면: python dot2_cues.py list)")
    char, english_layout, corner = typer()
    rows = [r for r in numbered(stage1() if stage == 1 else stage2()) if r[0] is not None]
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
    if stage == 1: print("Group 풀에서 그룹 수를 확인하세요:", ", ".join(f"{g}번 {EXPECTED[g]}대" for g in EXPECTED))
    else: print("Cues 창에서 큐 0.5~14와 12.5를 확인하고, 12.5의 Trig를 Follow로 바꾼 뒤 쇼를 저장하세요.")

def main():
    ap = argparse.ArgumentParser(description="dot2 조명 큐 자동 입력기")
    ap.add_argument("mode", choices=["list", "type"])
    ap.add_argument("stage", nargs="?", type=int, choices=[1, 2])
    ap.add_argument("--from", dest="start", type=int, default=1)
    ap.add_argument("--delay", type=float, default=0.03, help="글자 사이 간격(초). 글자가 빠지면 0.06으로")
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    if a.mode == "list":
        print(write_list(os.path.join(here, "dot2_commands.txt")))
    else:
        if not a.stage: ap.error("type 다음에 1 또는 2를 쓰세요")
        run_type(a.stage, a.start, a.delay)

if __name__ == "__main__":
    main()
