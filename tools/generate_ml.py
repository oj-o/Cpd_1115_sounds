#!/usr/bin/env python3
"""
ML 버전 큐 음원 생성기 (선택 사항)

Meta의 MusicGen(음악)과 AudioGen(효과음)으로 각 큐를 프롬프트에 맞춰 새로 생성합니다.
생성된 파일은 audio_ml/ 폴더에 저장되고, --apply 옵션을 주면 cues.js가 새 파일을 쓰도록 바뀝니다
(원래 목록은 cues_original.js로 백업).

⚠ 라이선스: MusicGen·AudioGen 모델 가중치는 CC-BY-NC 4.0(비상업)입니다.
   학교·동아리 등 비영리 공연이 아니라면 기본 음원(audio/)을 쓰세요.

설치 (인터넷 연결된 PC, GPU 권장 — CPU도 가능하지만 큐당 수 분 소요):
    pip install torch torchaudio transformers scipy numpy
    pip install audiocraft          # 효과음(AudioGen)까지 만들 때만

실행 (패키지 폴더에서):
    python tools/generate_ml.py                 # 전체 생성
    python tools/generate_ml.py --only 1 17 27  # 일부 큐만
    python tools/generate_ml.py --music-only    # audiocraft 없이 음악만
    python tools/generate_ml.py --apply         # 생성 후 cues.js에 반영
같은 프롬프트라도 실행할 때마다 결과가 달라집니다. 마음에 드는 결과가 나올 때까지 --only로 다시 돌리세요.
"""
import argparse, json, os, re, shutil
import numpy as np
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "audio_ml")

# (큐 id, 출력 파일명, 엔진, 길이(초), 프롬프트, 목표 RMS dBFS)
JOBS = [
    ("0",   "00_house",         "music", 20, "gentle playful office comedy background music, celesta and soft piano, light pizzicato, 96 bpm, C major, calm lobby music, no drums", -22),
    ("1",   "01_opening",       "music", 16, "bright cheerful comedy musical opening, ukulele strumming, glockenspiel melody, whistling, light shaker and claps, 132 bpm, C major, quirky and upbeat", -20),
    ("2A",  "02a_scare",        "sfx",    3, "sudden horror movie string screech with a deep boom", -18),
    ("2B",  "02b_boing",        "sfx",    1.5, "cartoon spring boing sound effect", -18),
    ("3",   "03_ring",          "sfx",    5, "modern mobile phone ringtone, marimba melody, ringing", -19),
    ("4",   "04_hangup",        "sfx",    3, "telephone busy tone beeping after the call ends", -21),
    ("5",   "05_midnight",      "sfx",   10, "grandfather clock striking midnight with eerie wind howling", -22),
    ("6",   "06_jingle",        "music",  5, "short spooky but playful transition sting, harpsichord and pizzicato strings descending chromatically, ends with a timpani hit", -18),
    ("7",   "07_auditor",       "music",  8, "heavy authoritative orchestral entrance, low brass chord swelling, timpani roll, ending with a big gong", -19),
    ("9",   "09_pass",          "music",  6, "short triumphant brass fanfare celebrating good news, trumpets and timpani, comedic", -19),
    ("10",  "10_stamp",         "sfx",    1, "rubber stamp slammed hard on paper on a wooden desk", -17),
    ("11",  "11_drone",         "music", 10, "slowly building suspense drone, low cellos and double basses, heartbeat, rising tension, horror film", -20),
    ("12",  "12_horror",        "music",  5, "loud horror jump scare stinger, dissonant orchestra hit, screeching violins, deep impact", -19),
    ("13",  "13_comic_fanfare", "music",  5, "sarcastic comedic celebration fanfare, brass and party popper, cartoon", -20),
    ("15",  "15_trombone",      "sfx",    4, "sad trombone wah wah wah fail sound", -18),
    ("16",  "16_thunder",       "sfx",    6, "orchestral horror sting followed by a loud thunder clap and rumbling", -21),
    ("17",  "17_piano",         "music", 27, "emotional gentle solo piano with soft strings, A minor, 72 bpm, tender and reflective, theatre underscore", -21),
    ("19",  "19_reaper",        "music", 10, "sly swing jazz with walking upright bass, clarinet, brushes on ride cymbal, sneaky comedic, ends with coins jingling", -19),
    ("20A", "20a_ding",         "sfx",    2, "elevator arrival ding chime", -20),
    ("20B", "20b_dundun",       "music",  4, "dramatic comedic dun dun dunnn orchestral sting, brass and strings, timpani roll", -18),
    ("21",  "21_strings",       "music", 29, "warm lyrical string ensemble with solo cello and harp, F major, 66 bpm, hopeful and tender, gentle", -21),
    ("22",  "22_hope",          "music", 26, "uplifting inspiring orchestral music building to a climax, strings, brass, piano arpeggios, timpani, C major, 84 bpm", -18),
    ("23",  "23_chime",         "sfx",    4, "four note public address announcement chime ding dong, school intercom", -19),
    ("24",  "24_fanfare",       "music",  6, "celebratory brass fanfare with timpani followed by applause", -18),
    ("26",  "26_edit",          "sfx",    6, "fast typing on a keyboard, pressing enter, then a stamp thud and a magical sparkle", -22),
    ("27",  "27_curtain",       "music", 28, "joyful energetic curtain call finale for a comedy musical, full band with trumpets, ukulele, drums, glockenspiel, 144 bpm, C major, big ending", -20),
]

def level(x, db):
    x = x.astype(np.float64)
    if x.ndim == 1: x = np.stack([x, x], 1)
    rms = np.sqrt(np.mean(x ** 2)) + 1e-9
    g = min(10 ** (db / 20) / rms, 10 ** (-1 / 20) / (np.abs(x).max() + 1e-9))
    x *= g; n = min(len(x), 1200); x[-n:] *= np.linspace(1, 0, n)[:, None]
    return np.clip(x, -1, 1)

def save(name, sr, x, db):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name + ".wav")
    wavfile.write(p, sr, (level(x, db) * 32767).astype(np.int16))
    print("  →", os.path.relpath(p, ROOT))

def run_music(jobs, model_id):
    import torch
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    proc = AutoProcessor.from_pretrained(model_id)
    model = MusicgenForConditionalGeneration.from_pretrained(model_id).to(dev)
    sr = model.config.audio_encoder.sampling_rate
    for cid, name, _, dur, prompt, db in jobs:
        print(f"[음악] 큐 {cid}: {prompt[:60]}…")
        inp = proc(text=[prompt], padding=True, return_tensors="pt").to(dev)
        with torch.no_grad():
            audio = model.generate(**inp, do_sample=True, guidance_scale=3.0, max_new_tokens=int(dur * 50) + 10)
        save(name, sr, audio[0, 0].cpu().numpy(), db)

def run_sfx(jobs, model_id):
    from audiocraft.models import AudioGen
    model = AudioGen.get_pretrained(model_id)
    for cid, name, _, dur, prompt, db in jobs:
        print(f"[효과음] 큐 {cid}: {prompt}")
        model.set_generation_params(duration=dur)
        wav = model.generate([prompt])
        save(name, model.sample_rate, wav[0, 0].cpu().numpy(), db)

def apply_to_cues():
    p = os.path.join(ROOT, "cues.js"); bak = os.path.join(ROOT, "cues_original.js")
    if not os.path.exists(bak): shutil.copy(p, bak)
    txt = open(bak, encoding="utf-8").read()
    cues = json.loads(re.search(r"window\.CUES = (\[.*\]);", txt, re.S).group(1))
    n = 0
    for c in cues:
        if c.get("type") != "audio": continue
        stem = os.path.splitext(os.path.basename(c["src"]))[0]
        if os.path.exists(os.path.join(OUT, stem + ".wav")):
            c["src"] = f"audio_ml/{stem}.wav"; c["dur"] = None; n += 1
    with open(p, "w", encoding="utf-8") as f:
        f.write("// ML 생성 음원 적용본 — 원래 목록은 cues_original.js\nwindow.CUES = " + json.dumps(cues, ensure_ascii=False, indent=1) + ";\n")
    print(f"cues.js 갱신: {n}개 큐가 audio_ml/ 음원을 사용합니다 (되돌리기: cues_original.js를 cues.js로 복사)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", help="생성할 큐 id (예: 1 17 2A)")
    ap.add_argument("--music-only", action="store_true")
    ap.add_argument("--sfx-only", action="store_true")
    ap.add_argument("--music-model", default="facebook/musicgen-small", help="더 좋은 품질: facebook/musicgen-medium")
    ap.add_argument("--sfx-model", default="facebook/audiogen-medium")
    ap.add_argument("--apply", action="store_true", help="생성 후 cues.js에 반영")
    a = ap.parse_args()
    jobs = [j for j in JOBS if not a.only or j[0] in a.only]
    if not a.sfx_only:
        m = [j for j in jobs if j[2] == "music"]
        if m: run_music(m, a.music_model)
    if not a.music_only:
        s = [j for j in jobs if j[2] == "sfx"]
        if s: run_sfx(s, a.sfx_model)
    if a.apply: apply_to_cues()

if __name__ == "__main__":
    main()
