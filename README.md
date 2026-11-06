# 저승공무원으로 취업했습니다!!! — 음향 큐 패키지

공연 당일 노트북 한 대로 운영할 수 있는 오프라인 음향 큐 세트입니다. 인터넷이 없어도 작동합니다.

```
cue_package/
├─ index.html          ← 큐 플레이어 (더블클릭으로 실행)
├─ cues.js             ← 큐 목록 (순서·볼륨·페이드·음원 경로)
├─ audio/              ← 공연용 음원 26개 (직접 작곡·렌더링, 저작권 걱정 없음)
├─ tools/
│   ├─ render_cues.py  ← audio/ 음원을 다시 만드는 Python 스크립트
│   └─ generate_ml.py  ← (선택) ML 모델로 음원을 새로 생성
└─ README.md
```

## 1. 실행

1. 폴더 전체를 공연용 노트북에 복사합니다. `audio/` 폴더가 `index.html` 옆에 있어야 합니다.
2. `index.html`을 **Chrome 또는 Edge**로 엽니다. 상단에 "음원 26개 준비 완료"가 뜨면 준비된 것입니다.
3. 처음 한 번은 화면을 클릭하거나 GO를 눌러야 소리가 나옵니다(브라우저 정책).

| 조작 | 기능 |
| --- | --- |
| `Space` 또는 GO 버튼 | 대기 큐(초록 줄) 실행 후 다음 큐로 이동 |
| `↑` `↓` / 큐 클릭 | 대기 큐 바꾸기 |
| 큐 두 번 클릭 | 그 큐를 바로 실행 |
| `F` | 재생 중인 모든 소리 3초 페이드아웃 |
| `Esc` | 전체 즉시 정지 (비상용) |
| 오른쪽 카드의 슬라이더 / 페이드 / 정지 | 재생 중인 큐 하나만 조절 |

GO를 연달아 두 번 눌러도 한 번만 실행됩니다(0.25초 이중 입력 방지).

## 2. 큐 구성 (총 34개)

- **음원 큐**: 소리를 재생합니다. `반복` 표시가 있는 큐(하우스 음악, 벨소리, 감성 테마, 서정 현악)는 끊김 없이 반복되므로 직접 페이드하거나 다음 큐로 끄세요.
- **정지 큐**(3B, 11B, 14B): 재생 중인 소리를 끕니다. 벨소리를 "전화 받는 순간" 끊을 때 씁니다.
- **이전 F.O**: GO를 누르면 앞에서 재생 중이던 소리를 그 시간 동안 자연스럽게 줄이고 새 큐를 시작합니다. 예를 들어 1번 오프닝은 하우스 음악을 2.5초 동안 줄이며 시작합니다.
- **F.I**: 새 큐가 0에서 시작해 서서히 커집니다.

대본 기준 핵심 흐름은 다음과 같습니다.

- 1장: 오프닝, 공포 스팅과 띠용, 벨소리, 자정 괘종
- 3장: 도장 → 긴장 드론(11) → **11B로 정적** → 호러 쇼크(12)
- 5~7장: 감성 피아노(17), 서정 현악(21), 희망 테마(22)
- 9장: 수명 수정(26), 커튼콜(27), 하우스 음악(28)

## 3. 리허설 체크리스트

- [ ] 극장 스피커로 큐마다 볼륨을 맞추고, `cues.js`의 `vol`(0~1)에 적어 둡니다.
- [ ] 27번 커튼콜은 "하나, 둘! 감사합니다!!!"에 마지막 화음(시작 후 약 27초)이 오도록 출발 시점을 맞춥니다.
- [ ] 11번 드론은 "나 네?"에서 11B로 끊고, 1초 정적 후 12번을 실행합니다.
- [ ] 노트북 절전·화면 보호기·알림을 끄고 전원을 연결합니다.
- [ ] 다른 브라우저 탭과 메신저를 닫습니다. 알림음이 객석 스피커로 나갈 수 있습니다.
- [ ] 패키지를 USB에 한 부 더 복사해 둡니다.

## 4. 음원 바꾸기 (무료 음원 사용)

기본 음원은 이 패키지에서 직접 작곡하고 실제 악기 샘플(FluidR3 GM, MIT 라이선스)로 렌더링했습니다. 효과음은 Python으로 합성했습니다. 그대로 공연해도 저작권 문제가 없습니다.

더 사실적인 녹음을 쓰고 싶다면 다음 순서로 바꾸세요.

1. 아래 사이트에서 음원을 내려받습니다.
2. `audio/` 폴더에 **같은 파일 이름**으로 덮어씁니다. 확장자가 다르면 `cues.js`의 `src`도 고칩니다.
3. 플레이어를 새로고침합니다. 길이는 자동으로 다시 표시됩니다.

| 사이트 | 이용 조건 (2026년 11월 확인) |
| --- | --- |
| [Pixabay 효과음·음악](https://pixabay.com/sound-effects/) | 상업·비상업 모두 무료, 출처 표시 불필요. 단, 음원 자체를 따로 재배포하는 것은 금지 ([FAQ](https://pixabay.com/service/faq/)) |
| [Freesound](https://freesound.org) | 음원마다 라이선스가 다름. 검색 필터에서 **CC0**를 고르면 조건 없이 사용 가능. CC-BY는 출처 표시, NC는 비상업만 허용 |
| [공유마당 (한국저작권위원회)](https://gongu.copyright.or.kr/gongu/main/contents.do?menuNo=200196) | 자유이용·CCL·공공누리 등 음원마다 조건이 다르므로 상세 페이지의 라이선스를 확인. 문의: 저작권상담센터 1800-5455 |

**큐별 검색어** (Pixabay와 Freesound에서는 영어 검색이 결과가 많습니다)

| 큐 | 검색어 |
| --- | --- |
| 0, 28 하우스 | `quirky lobby music`, `playful background celesta` |
| 1 오프닝, 27 커튼콜 | `ukulele happy comedy`, `whistle upbeat quirky` |
| 2A, 12, 16 공포 스팅 | `horror stinger`, `jump scare hit`, `thunder clap` |
| 2B, 18 띠용 | `cartoon boing`, `spring boing` |
| 3, 14 벨소리 | `phone ringing`, `marimba ringtone` |
| 4 통화 종료 | `phone busy tone`, `hang up beep` |
| 5 자정 | `grandfather clock midnight`, `wind howling` |
| 6, 8 전환 | `spooky transition sting`, `halloween comedy sting` |
| 7 감사팀장 | `gong`, `epic brass entrance` |
| 9, 13, 24 팡파르 | `brass fanfare short`, `tada fanfare`, `applause small crowd` |
| 10 도장 | `stamp paper`, `rubber stamp` |
| 11 드론 | `suspense drone`, `heartbeat tension` |
| 15 실패 | `sad trombone` |
| 17 감성 | `emotional piano`, `sad piano theme` |
| 19 저승사자 | `sneaky jazz`, `coins drop` |
| 20A, 20B | `elevator ding`, `dun dun dun dramatic` |
| 21 서정 | `warm strings cello`, `river stream` |
| 22, 25 희망 | `inspiring orchestral`, `uplifting cinematic` |
| 23 방송 | `announcement chime`, `school bell chime` |
| 26 수정 | `keyboard typing`, `magic sparkle` |

내려받은 파일은 앞뒤 무음을 잘라 내고 음량을 맞춘 뒤 넣으세요. 무료 편집기 Audacity의 "자르기"와 "정규화"를 쓰면 됩니다.

## 5. 음원 다시 만들기 (Python)

음색·템포·길이를 고치려면 `tools/render_cues.py`의 해당 함수를 수정하고 다시 렌더링합니다. 예를 들어 오프닝은 `opening()`, 감성 테마는 `piano_theme()`입니다.

```bash
# Ubuntu/Debian
sudo apt install fluidsynth fluid-soundfont-gm ffmpeg
pip install numpy scipy mido
python3 tools/render_cues.py
```

Windows나 macOS에서는 FluidSynth와 ffmpeg를 설치하고, `FluidR3_GM.sf2`를 `tools/` 폴더에 넣으면 됩니다. 큐 목록(`cues.js`)도 함께 다시 만들어지므로, 손으로 고친 볼륨 값은 렌더 후 다시 확인하세요.

## 6. ML 모델로 생성하기 (선택)

`tools/generate_ml.py`는 Meta의 MusicGen(음악)과 AudioGen(효과음)으로 큐마다 맞춘 프롬프트의 음원을 생성합니다. 결과는 `audio_ml/`에 저장되고, `--apply`를 주면 플레이어가 그 음원을 씁니다.

```bash
pip install torch torchaudio transformers scipy numpy audiocraft
python tools/generate_ml.py --only 1 17 27 --apply   # 원하는 큐만 생성 후 적용
```

- 인터넷이 되는 PC에서 실행해야 합니다. 첫 실행 때 모델을 내려받습니다.
- GPU가 있으면 큐당 수십 초, CPU만 있으면 수 분이 걸립니다.
- 실행할 때마다 결과가 다르므로, 마음에 들 때까지 `--only`로 다시 돌려 고르세요.
- 원래 음원으로 되돌리려면 `cues_original.js`를 `cues.js`로 복사하면 됩니다.
- **라이선스 주의:** MusicGen·AudioGen 가중치는 [CC-BY-NC 4.0(비상업)](https://facebookresearch.github.io/audiocraft/model_cards/MUSICGEN_MODEL_CARD.html)입니다. 유료 공연이라면 기본 음원이나 Pixabay 음원을 쓰세요.
