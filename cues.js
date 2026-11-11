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
  "title": "음악1 · 밝은 음악",
  "timing": "지문 '밝은 조명. 음악1'",
  "fadeOthers": 2.5,
  "note": "음악 종류: 경쾌한 오피스 코미디(우쿨렐레·글로켄슈필·휘슬, 132BPM). \"여러분!!!\" 직전에 볼륨을 낮춤",
  "type": "audio",
  "src": "audio/01_opening.mp3",
  "dur": 17.93
 },
 {
  "id": "2",
  "scene": "1장",
  "title": "휴대전화 벨소리 (수신)",
  "timing": "지문 '휴대전화 벨소리.' (\"…'저승관리청' 이었어요!\" 뒤)",
  "loop": true,
  "vol": 0.8,
  "type": "audio",
  "src": "audio/03_ring.wav",
  "dur": 5.0
 },
 {
  "id": "2B",
  "scene": "1장",
  "title": "벨소리 정지",
  "timing": "주인공 \"여보세요?\" 직전 (받는 순간)",
  "type": "stop",
  "fade": 0.1,
  "note": "이어지는 인사담당자 (전화) 대사는 무대 뒤 마이크 + 전화 음색 EQ"
 },
 {
  "id": "3",
  "scene": "1장",
  "title": "통화 종료음",
  "timing": "지문 '(전화 종료)' (\"열심히 준비 하겠습니다!\" 뒤)",
  "type": "audio",
  "src": "audio/04_hangup.mp3",
  "dur": 2.55
 },
 {
  "id": "4",
  "scene": "2장",
  "title": "통화 발신음",
  "timing": "지문 '팀장이 휴대전화를 꺼내 감사팀장에게 전화를 한다.'",
  "loop": true,
  "vol": 0.8,
  "type": "audio",
  "src": "audio/05_ringback.wav",
  "dur": 6.0
 },
 {
  "id": "4B",
  "scene": "2장",
  "title": "발신음 정지",
  "timing": "팀장 \"감사팀장님 오랜만이에요.\" 직전 (연결되는 순간)",
  "type": "stop",
  "fade": 0.1
 },
 {
  "id": "5",
  "scene": "3장",
  "title": "녹음 메시지 신호음",
  "timing": "지문 '녹음된 메세지가 재생된다' (3장 시작, 암전 중)",
  "note": "이어서 인사담당자 메시지: 배우 녹음 파일로 교체하거나 무대 뒤 마이크 + 전화 음색 EQ",
  "type": "audio",
  "src": "audio/06_ars.mp3",
  "dur": 1.63
 },
 {
  "id": "6",
  "scene": "3장",
  "title": "명부 재확인 스팅",
  "timing": "\"…저였어요!!!(명부를 다시 확인한다.)\"",
  "type": "audio",
  "src": "audio/07_recheck.mp3",
  "dur": 4.62
 },
 {
  "id": "7",
  "scene": "3→4장",
  "title": "4장 전환 음악",
  "timing": "\"(머리를 감싼다.)\" → 4장 시작",
  "type": "audio",
  "src": "audio/08_jingle.mp3",
  "dur": 4.98
 },
 {
  "id": "8",
  "scene": "4장",
  "title": "휴대전화 벨소리 (크게)",
  "timing": "지문 '그때 휴대전화 벨소리.' (\"지금 칭찬하실 때가 아니잖아요!\" 뒤)",
  "loop": true,
  "vol": 1.0,
  "type": "audio",
  "src": "audio/03_ring.wav",
  "dur": 5.0
 },
 {
  "id": "8B",
  "scene": "4장",
  "title": "벨소리 정지",
  "timing": "\"(전화 받음.) 여보세요?\"",
  "type": "stop",
  "fade": 0.1,
  "note": "인사담당자 (전화) 대사는 무대 뒤 마이크 + 전화 음색 EQ"
 },
 {
  "id": "9",
  "scene": "8장",
  "title": "방송음 (사내 방송 차임)",
  "timing": "인사담당자 \"(방송) 긴급 공지입니다…\" 직전",
  "note": "차임 끝나고 방송 대사: 무대 뒤 마이크 + 확성기 음색 EQ",
  "type": "audio",
  "src": "audio/09_chime.mp3",
  "dur": 3.44
 },
 {
  "id": "10",
  "scene": "9장",
  "title": "밝은 음악 · 커튼콜",
  "timing": "지문 '밝은 음악. 모두 관객을 향해 인사한다.'",
  "fadeOthers": 1,
  "note": "\"하나, 둘! 감사합니다!!!\" · 암전 뒤 인사가 끝날 때까지 이어짐 (마지막 화음은 시작 약 27초 뒤)",
  "type": "audio",
  "src": "audio/10_curtain.mp3",
  "dur": 30.84
 },
 {
  "id": "11",
  "scene": "공연 후",
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
