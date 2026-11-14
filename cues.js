// 큐 목록 — 음원을 바꾸려면 src 경로만 바꾸면 됩니다.
// type: audio | stop · loop: 반복 · vol: 0~1 · fadeIn/fadeOthers/fade: 초
window.CUES = [
 {
  "id": "0",
  "scene": "프리쇼",
  "title": "관객 입장 · 시작 음악 (으스스, 약 3분)",
  "timing": "관객 입장 시간 · 공연 시작 전 F.O",
  "loop": true,
  "vol": 0.6,
  "note": "음이 나간 로비 왈츠 → 저승 오피스 왈츠 → 삼도천 지하철, 끝나면 처음부터 반복. 공연 시작 전 F(전체 페이드)로 끄거나 1번 벨소리가 1초에 걸쳐 끔",
  "type": "audio",
  "src": "audio/00_house_suite.mp3",
  "dur": 184.48
 },
 {
  "id": "1",
  "scene": "1장",
  "title": "전화벨 (수신)",
  "timing": "지문 '휴대전화 벨소리.' (\"…'저승관리청' 이었어요!\" 뒤)",
  "loop": true,
  "vol": 0.8,
  "fadeOthers": 1,
  "note": "음악이 남아 있으면 1초에 걸쳐 꺼짐",
  "type": "audio",
  "src": "audio/03_ring.wav",
  "dur": 5.0
 },
 {
  "id": "1B",
  "scene": "1장",
  "title": "전화벨 정지 (받음)",
  "timing": "주인공 \"여보세요?\" 직전",
  "type": "stop",
  "fade": 0.1
 },
 {
  "id": "2",
  "scene": "1장",
  "title": "전화 끊김",
  "timing": "지문 '(전화 종료)' (\"열심히 준비 하겠습니다!\" 뒤)",
  "type": "audio",
  "src": "audio/04_hangup.mp3",
  "dur": 2.55
 },
 {
  "id": "3",
  "scene": "2장",
  "title": "감사팀장 전화 신호 (발신음)",
  "timing": "지문 '팀장이 휴대전화를 꺼내 감사팀장에게 전화를 한다.'",
  "loop": true,
  "vol": 0.8,
  "type": "audio",
  "src": "audio/05_ringback.wav",
  "dur": 6.0
 },
 {
  "id": "3B",
  "scene": "2장",
  "title": "신호 정지 (연결)",
  "timing": "팀장 \"감사팀장님 오랜만이에요.\" 직전",
  "type": "stop",
  "fade": 0.1
 },
 {
  "id": "4",
  "scene": "4장",
  "title": "벨소리 (인사과 전화)",
  "timing": "지문 '그때 휴대전화 벨소리.' (\"지금 칭찬하실 때가 아니잖아요!\" 뒤)",
  "loop": true,
  "vol": 1.0,
  "type": "audio",
  "src": "audio/03_ring.wav",
  "dur": 5.0
 },
 {
  "id": "4B",
  "scene": "4장",
  "title": "벨소리 정지 (받음)",
  "timing": "\"(전화 받음.) 여보세요?\"",
  "type": "stop",
  "fade": 0.1,
  "note": "인사담당자 (전화) 대사는 무대 뒤 마이크 + 전화 음색 EQ"
 },
 {
  "id": "5",
  "scene": "8장",
  "title": "긴급공지 방송 (차임)",
  "timing": "인사담당자 \"(방송) 긴급 공지입니다…\" 직전",
  "note": "차임 끝나고 방송 대사: 무대 뒤 마이크 + 확성기 음색 EQ",
  "type": "audio",
  "src": "audio/09_chime.mp3",
  "dur": 3.44
 },
 {
  "id": "6",
  "scene": "엔딩",
  "title": "엔딩 · 밝은 음악 (커튼콜, 약 3분)",
  "timing": "지문 '밝은 음악. 모두 관객을 향해 인사한다.'",
  "fadeOthers": 1,
  "note": "\"하나, 둘! 감사합니다!!!\" · 약 3분, C→D→E로 조가 올라가며 끝에 큰 마무리. 일찍 끝나면 F로 페이드",
  "type": "audio",
  "src": "audio/10_curtain.mp3",
  "dur": 185.13
 }
];
