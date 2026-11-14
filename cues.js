// 큐 목록 — 음원을 바꾸려면 src 경로만 바꾸면 됩니다.
// type: audio | stop · loop: 반복 · vol: 0~1 · fadeIn/fadeOthers/fade: 초
window.CUES = [
 {
  "id": "OP",
  "scene": "프리쇼",
  "title": "관객 입장 · 오프닝 음악 (반복)",
  "timing": "하우스 오픈, 관객 입장 시작",
  "loop": true,
  "vol": 0.6,
  "userFile": true,
  "youtube": "_CzSCWpF7TM",
  "note": "음원 파일이 없으면 유튜브 플레이어로 반복 재생(인터넷 필요) · 연결이 안 되면 GO 때 유튜브 새 탭이 열림 · 파일을 고르면 그 파일로 재생 · 다음 큐 0이 2초에 걸쳐 끔",
  "type": "audio",
  "src": "audio/00_opening.mp3",
  "dur": null
 },
 {
  "id": "0",
  "scene": "프리쇼",
  "title": "관객 입장 · 시작 음악 (으스스, 약 5분)",
  "timing": "관객 입장 시간 · 공연 시작 전 F.O",
  "vol": 0.6,
  "fadeOthers": 2,
  "over": true,
  "note": "음이 나간 로비 왈츠 → 저승 오피스 왈츠 → 삼도천 지하철 → 더 낮은 로비 왈츠, 한 번 재생 후 끝남(반복 없음). 공연 시작 전 F(전체 페이드)로 끄거나 1번 벨소리가 1초에 걸쳐 끔",
  "type": "audio",
  "src": "audio/00_house_suite.mp3?v=8feb51c0",
  "dur": 304.13
 },
 {
  "id": "1",
  "scene": "1장",
  "title": "전화벨 (수신)",
  "timing": "지문 '휴대전화 벨소리.' (\"…'저승관리청' 이었어요!\" 뒤)",
  "vol": 0.8,
  "fadeOthers": 1,
  "note": "벨소리 2번(5초) 후 저절로 끝남 · 음악이 남아 있으면 1초에 걸쳐 꺼짐",
  "type": "audio",
  "src": "audio/03_ring.wav?v=f5587fd7",
  "dur": 5.0
 },
 {
  "id": "1B",
  "scene": "1장",
  "title": "전화벨 정지 (받음)",
  "timing": "주인공 \"여보세요?\" 직전",
  "type": "stop",
  "fade": 0.1,
  "targets": [
   "1"
  ]
 },
 {
  "id": "1C",
  "scene": "1장",
  "title": "녹음 음성 1-1 (큐프1 1/3)",
  "timing": "1B(전화 받음) 바로 뒤",
  "voice": true,
  "note": "큐프1 새 녹음 원본 0.5–7초 구간 · 배우 녹음 · 한 번 재생 후 자동 종료 · 페이드되지 않음(F·다른 큐에도 끝까지 재생)",
  "type": "audio",
  "src": "audio/voice1_1.mp3?v=abbf5d0e",
  "dur": 6.53
 },
 {
  "id": "1D",
  "scene": "1장",
  "title": "녹음 음성 1-2 (큐프1 2/3)",
  "timing": "녹음 1-1 뒤 다음 대사 차례",
  "voice": true,
  "note": "큐프1 새 녹음 원본 7–14.5초 구간 · 배우 녹음 · 한 번 재생 후 자동 종료 · 페이드되지 않음(F·다른 큐에도 끝까지 재생)",
  "type": "audio",
  "src": "audio/voice1_2.mp3?v=cad5075b",
  "dur": 7.55
 },
 {
  "id": "1E",
  "scene": "1장",
  "title": "녹음 음성 1-3 (큐프1 3/3)",
  "timing": "녹음 1-2 뒤 다음 대사 차례",
  "voice": true,
  "note": "큐프1 새 녹음 원본 14.5–22.5초 구간 · 배우 녹음 · 한 번 재생 후 자동 종료 · 페이드되지 않음(F·다른 큐에도 끝까지 재생)",
  "type": "audio",
  "src": "audio/voice1_3.mp3?v=394b8d45",
  "dur": 8.05
 },
 {
  "id": "2",
  "scene": "1장",
  "title": "전화 끊김",
  "timing": "지문 '(전화 종료)' (\"열심히 준비 하겠습니다!\" 뒤)",
  "type": "audio",
  "src": "audio/04_hangup.mp3?v=166cb3c4",
  "dur": 1.94
 },
 {
  "id": "3",
  "scene": "2장",
  "title": "감사팀장 전화 신호 (발신음)",
  "timing": "지문 '팀장이 휴대전화를 꺼내 감사팀장에게 전화를 한다.'",
  "vol": 0.8,
  "type": "audio",
  "src": "audio/05_ringback.wav?v=a87e77eb",
  "dur": 6.0
 },
 {
  "id": "3B",
  "scene": "2장",
  "title": "신호 정지 (연결)",
  "timing": "팀장 \"감사팀장님 오랜만이에요.\" 직전",
  "type": "stop",
  "fade": 0.1,
  "targets": [
   "3"
  ]
 },
 {
  "id": "3C",
  "scene": "2장",
  "title": "녹음 음성 2 (큐프2)",
  "timing": "3B(감사팀장 연결) 바로 뒤",
  "voice": true,
  "note": "배우 녹음 · 한 번 재생 후 자동 종료 · 페이드되지 않음(F·다른 큐에도 끝까지 재생)",
  "type": "audio",
  "src": "audio/voice2.mp3?v=2231d11e",
  "dur": 9.74
 },
 {
  "id": "4",
  "scene": "4장",
  "title": "벨소리 (인사과 전화)",
  "timing": "지문 '그때 휴대전화 벨소리.' (\"지금 칭찬하실 때가 아니잖아요!\" 뒤)",
  "vol": 1.0,
  "type": "audio",
  "src": "audio/03_ring.wav?v=f5587fd7",
  "dur": 5.0
 },
 {
  "id": "4A",
  "scene": "4장",
  "title": "벨소리 + 녹음 음성 3 (큐프3)",
  "timing": "4(벨소리)와 4B(받음) 사이",
  "voice": true,
  "over": true,
  "cuts": [
   "4"
  ],
  "note": "벨소리 2번(5초) → 배우 녹음. 시작할 때 4번 벨소리는 바로 끊기고 녹음 속 벨소리로 이어짐 · 녹음은 페이드되지 않음",
  "type": "audio",
  "src": "audio/voice3.mp3?v=cada76bb",
  "dur": 30.54
 },
 {
  "id": "4B",
  "scene": "4장",
  "title": "벨소리 정지 (받음)",
  "timing": "\"(전화 받음.) 여보세요?\"",
  "type": "stop",
  "fade": 0.1,
  "targets": [
   "4"
  ],
  "note": "인사담당자 (전화) 대사는 무대 뒤 마이크 + 전화 음색 EQ"
 },
 {
  "id": "5",
  "scene": "8장",
  "title": "긴급공지 방송 (차임)",
  "timing": "인사담당자 \"(방송) 긴급 공지입니다…\" 직전",
  "note": "차임 끝나고 5B 녹음 방송",
  "type": "audio",
  "src": "audio/09_chime.mp3?v=98922fbd",
  "dur": 3.48
 },
 {
  "id": "5B",
  "scene": "8장",
  "title": "녹음 음성 4 · 긴급공지 방송 (큐프4)",
  "timing": "5(차임) 끝나면 바로",
  "voice": true,
  "note": "배우 녹음 · 한 번 재생 후 자동 종료 · 페이드되지 않음(F·다른 큐에도 끝까지 재생)",
  "type": "audio",
  "src": "audio/voice4.mp3?v=4487002f",
  "dur": 7.63
 },
 {
  "id": "6",
  "scene": "엔딩",
  "title": "엔딩 · 밝은 음악 (커튼콜, 약 3분)",
  "timing": "지문 '밝은 음악. 모두 관객을 향해 인사한다.'",
  "fadeOthers": 1,
  "note": "\"하나, 둘! 감사합니다!!!\" · 약 3분, C→D→E로 조가 올라가며 끝에 큰 마무리. 일찍 끝나면 F로 페이드",
  "type": "audio",
  "src": "audio/10_curtain.mp3?v=12af55fc",
  "dur": 185.16
 }
];
