// 큐 목록 — 음원을 바꾸려면 src 경로만 바꾸면 됩니다.
// type: audio | stop · loop: 반복 · vol: 0~1 · fadeIn/fadeOthers/fade: 초
window.CUES = [
 {
  "id": "0",
  "scene": "프리쇼",
  "title": "하우스 음악",
  "timing": "관객 입장 중 (공연 전)",
  "loop": true,
  "vol": 0.55,
  "type": "audio",
  "src": "audio/00_house.wav",
  "dur": 20.0
 },
 {
  "id": "1",
  "scene": "1장",
  "title": "오프닝 테마",
  "timing": "밝은 조명 · 지문 '음악1'",
  "fadeOthers": 2.5,
  "note": "\"여러분!!!\" 직전에 볼륨을 낮춤",
  "type": "audio",
  "src": "audio/01_opening.mp3",
  "dur": 17.93
 },
 {
  "id": "2A",
  "scene": "1장",
  "title": "공포 스팅",
  "timing": "\"결재하는 사람입니다.\" 정적 뒤",
  "fadeOthers": 0.5,
  "type": "audio",
  "src": "audio/02a_scare.mp3",
  "dur": 4.77
 },
 {
  "id": "2B",
  "scene": "1장",
  "title": "코믹 띠용",
  "timing": "\"이렇게 말하니 좀 무서운데요?\"",
  "type": "audio",
  "src": "audio/02b_boing.mp3",
  "dur": 1.34
 },
 {
  "id": "3",
  "scene": "1장",
  "title": "휴대전화 벨소리",
  "timing": "\"…'저승관리청' 이었어요!\"",
  "loop": true,
  "vol": 0.8,
  "type": "audio",
  "src": "audio/03_ring.wav",
  "dur": 5.0
 },
 {
  "id": "3B",
  "scene": "1장",
  "title": "벨소리 정지",
  "timing": "전화를 받는 순간",
  "type": "stop",
  "fade": 0.1
 },
 {
  "id": "4",
  "scene": "1장",
  "title": "통화 종료음",
  "timing": "\"열심히 준비 하겠습니다!\"",
  "type": "audio",
  "src": "audio/04_hangup.mp3",
  "dur": 2.55
 },
 {
  "id": "5",
  "scene": "1장",
  "title": "자정 괘종 + 바람",
  "timing": "\"시간은 밤12시 장소는 멘사장례식장?\"",
  "note": "바람은 면접장 전환까지 이어짐",
  "type": "audio",
  "src": "audio/05_midnight.mp3",
  "dur": 13.0
 },
 {
  "id": "6",
  "scene": "1장",
  "title": "장면 전환 징글",
  "timing": "\"이번에는 제발 합격했으면 좋겠다!\" 암전",
  "fadeOthers": 1.5,
  "type": "audio",
  "src": "audio/06_jingle.mp3",
  "dur": 4.98
 },
 {
  "id": "7",
  "scene": "2장",
  "title": "감사팀장 등장",
  "timing": "\"다들 일어나요. 감사팀장님 오시네요.\"",
  "fadeOthers": 1,
  "type": "audio",
  "src": "audio/07_auditor.mp3",
  "dur": 9.24
 },
 {
  "id": "8",
  "scene": "2장",
  "title": "장면 전환 징글",
  "timing": "인사담당자 퇴장",
  "fadeOthers": 1.5,
  "type": "audio",
  "src": "audio/06_jingle.mp3",
  "dur": 4.98
 },
 {
  "id": "9",
  "scene": "3장",
  "title": "합격 안내 + 팡파르",
  "timing": "암전 중 녹음 메시지 끝",
  "type": "audio",
  "src": "audio/09_pass.mp3",
  "dur": 7.81
 },
 {
  "id": "10",
  "scene": "3장",
  "title": "도장 쾅",
  "timing": "\"완벽히 일치했습니다. 승인!!!\"",
  "type": "audio",
  "src": "audio/10_stamp.mp3",
  "dur": 0.62
 },
 {
  "id": "11",
  "scene": "3장",
  "title": "긴장 드론 + 심장박동",
  "timing": "\"자, 그 다음 대상자는…… 이름 유내일.\"",
  "note": "대사가 짧으면 11B로 바로 끊음",
  "type": "audio",
  "src": "audio/11_drone.mp3",
  "dur": 10.0
 },
 {
  "id": "11B",
  "scene": "3장",
  "title": "드론 컷 (정적)",
  "timing": "\"(자기자신을 가리킨다.) 나 네?\"",
  "type": "stop",
  "fade": 0
 },
 {
  "id": "12",
  "scene": "3장",
  "title": "호러 쇼크",
  "timing": "\"으아아아아악!!! 저에요!!!\"",
  "fadeOthers": 0,
  "type": "audio",
  "src": "audio/12_horror.mp3",
  "dur": 6.31
 },
 {
  "id": "13",
  "scene": "4장",
  "title": "코믹 팡파르",
  "timing": "\"우와! 축하해.\"",
  "type": "audio",
  "src": "audio/13_comic_fanfare.mp3",
  "dur": 5.6
 },
 {
  "id": "14",
  "scene": "4장",
  "title": "휴대전화 벨소리 (크게)",
  "timing": "\"지금 칭찬하실 때가 아니잖아요!\" 직후",
  "loop": true,
  "vol": 1.0,
  "fadeOthers": 0.3,
  "type": "audio",
  "src": "audio/03_ring.wav",
  "dur": 5.0
 },
 {
  "id": "14B",
  "scene": "4장",
  "title": "벨소리 정지",
  "timing": "전화를 받는 순간",
  "type": "stop",
  "fade": 0.1
 },
 {
  "id": "15",
  "scene": "4장",
  "title": "실패 트롬본",
  "timing": "\"저승에도 이해 충돌 방지 규정이 있더라고요.\"",
  "type": "audio",
  "src": "audio/15_trombone.mp3",
  "dur": 3.88
 },
 {
  "id": "16",
  "scene": "5장",
  "title": "공포 스팅 + 천둥",
  "timing": "\"특이사항 본 계약은 사망 이후에도 유효함.\"",
  "fadeOthers": 0.3,
  "type": "audio",
  "src": "audio/16_thunder.mp3",
  "dur": 5.41
 },
 {
  "id": "17",
  "scene": "5~6장",
  "title": "감성 피아노 테마",
  "timing": "\"왜 바로 승인하지 않았어?\"",
  "loop": true,
  "fadeIn": 5,
  "vol": 0.7,
  "note": "팀장 대사에 맞춰 볼륨을 서서히 올림",
  "type": "audio",
  "src": "audio/17_piano.wav",
  "dur": 26.67
 },
 {
  "id": "18",
  "scene": "6장",
  "title": "감성 F.O → 띠용",
  "timing": "\"물론 연장근무는 좀 줄였으면 좋겠습니다.\"",
  "fadeOthers": 2.5,
  "type": "audio",
  "src": "audio/02b_boing.mp3",
  "dur": 1.34
 },
 {
  "id": "19",
  "scene": "6장",
  "title": "저승사자 테마 + 동전",
  "timing": "저승사자 배낭 메고 등장",
  "fadeOthers": 0.5,
  "type": "audio",
  "src": "audio/19_reaper.mp3",
  "dur": 10.71
 },
 {
  "id": "20A",
  "scene": "7장",
  "title": "엘리베이터 띵",
  "timing": "\"엘리베이터에서 방귀 뀌고…\"",
  "type": "audio",
  "src": "audio/20a_ding.mp3",
  "dur": 1.58
 },
 {
  "id": "20B",
  "scene": "7장",
  "title": "범인 발각 스팅",
  "timing": "\"설마 어제 엘리베이터에서 그 방귀…….\"",
  "type": "audio",
  "src": "audio/20b_dundun.mp3",
  "dur": 4.62
 },
 {
  "id": "21",
  "scene": "7장",
  "title": "서정 현악 + 물소리",
  "timing": "\"누군가에게 다시 살아갈 기회를 주는 일이요.\"",
  "loop": true,
  "fadeIn": 4,
  "vol": 0.65,
  "type": "audio",
  "src": "audio/21_strings.wav",
  "dur": 29.09
 },
 {
  "id": "22",
  "scene": "7장",
  "title": "희망 테마 (클라이맥스)",
  "timing": "\"살아 있는 동안에만 할 수 있는 일이 있어요.\"",
  "fadeOthers": 3,
  "fadeIn": 2,
  "type": "audio",
  "src": "audio/22_hope.mp3",
  "dur": 26.84
 },
 {
  "id": "23",
  "scene": "8장",
  "title": "사내 방송 차임",
  "timing": "지문 '(방송) 긴급 공지'",
  "fadeOthers": 1,
  "type": "audio",
  "src": "audio/23_chime.mp3",
  "dur": 3.44
 },
 {
  "id": "24",
  "scene": "8장",
  "title": "축하 팡파르",
  "timing": "\"응 수습기간이 종료됐어.\"",
  "type": "audio",
  "src": "audio/24_fanfare.mp3",
  "dur": 5.96
 },
 {
  "id": "25",
  "scene": "8장",
  "title": "희망 테마",
  "timing": "\"……역시 이 기관은 이상합니다.\"",
  "fadeIn": 4,
  "vol": 0.75,
  "type": "audio",
  "src": "audio/22_hope.mp3",
  "dur": 26.84
 },
 {
  "id": "26",
  "scene": "9장",
  "title": "타이핑 → 엔터 → 도장",
  "timing": "\"제 수명을…… 4,444년으로 수정하겠습니다!\"",
  "fadeOthers": 2,
  "type": "audio",
  "src": "audio/26_edit.mp3",
  "dur": 6.79
 },
 {
  "id": "27",
  "scene": "9장",
  "title": "커튼콜",
  "timing": "\"여러분! 저승관리청은 항상 정상 영업합니다!\"",
  "fadeIn": 3,
  "note": "\"하나, 둘! 감사합니다!!!\"에 마지막 화음이 오도록 미리 출발",
  "type": "audio",
  "src": "audio/27_curtain.mp3",
  "dur": 30.84
 },
 {
  "id": "28",
  "scene": "커튼콜 후",
  "title": "하우스 음악",
  "timing": "커튼콜 인사 후 하우스 조명",
  "loop": true,
  "vol": 0.55,
  "fadeOthers": 4,
  "fadeIn": 3,
  "type": "audio",
  "src": "audio/00_house.wav",
  "dur": 20.0
 }
];
