// 큐 목록 — 음원을 바꾸려면 src 경로만 바꾸면 됩니다.
// type: audio | stop · loop: 반복 · vol: 0~1 · fadeIn/fadeOthers/fade: 초
window.CUES = [
 {
  "id": "0",
  "scene": "프리쇼",
  "title": "관객 입장 음악 (약 5분)",
  "timing": "관객 입장 시간 · 조명 프리셋",
  "loop": true,
  "vol": 0.6,
  "note": "저승관리청 모음곡: 스산한 로비 → 행정 업무 → 삼도천 지하철 → 살아 있는 동안 → 저승사자 출장 → 환생 대기번호",
  "type": "audio",
  "src": "audio/00_house_suite.mp3",
  "dur": 313.71
 },
 {
  "id": "1",
  "scene": "1장",
  "title": "음악1 · 스산한 저승 오피스 왈츠",
  "timing": "입장 음악 F.O · 조명 fade out → 직원들 등장, 서류 정리 (주인공 제외)",
  "loop": true,
  "fadeOthers": 4,
  "note": "또렷한 첼레스타·오르골 선율의 단조 왈츠, 아래에 낮은 현·테레민·시계 소리. 반복되므로 다음 큐로 넘김",
  "type": "audio",
  "src": "audio/01_underworld_office.wav",
  "dur": 32.73
 },
 {
  "id": "1B",
  "scene": "1장",
  "title": "주인공 센터 · 밝은 음악",
  "timing": "주인공이 센터로 나올 때 (\"여러분!!!\" 직전)",
  "fadeOthers": 1.5,
  "note": "스산한 음악에서 밝은 음악으로 반전. 대사가 시작되면 볼륨을 낮춤",
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
  "fadeOthers": 1,
  "note": "음악 off 후 벨소리 (대본 메모)",
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
  "note": "이어지는 인사담당자 (전화) 대사는 녹음 파일 또는 무대 뒤 마이크 + 전화 음색 EQ"
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
  "title": "퇴장 음악",
  "timing": "커튼콜 인사 후 하우스 조명",
  "loop": true,
  "vol": 0.6,
  "fadeOthers": 4,
  "fadeIn": 3,
  "type": "audio",
  "src": "audio/00_house_suite.mp3",
  "dur": 313.71
 }
];
