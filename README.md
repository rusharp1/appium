# 당근마켓 자동화 봇

당근마켓 앱에서 자동으로 게시물에 좋아요를 누르고, 프로필의 관심목록을 읽어오는 Appium 기반 자동화 도구입니다.

## 📁 프로젝트 구조

```
carrot/
├── carrot_like.py          # 좋아요 자동화 봇
├── carrot_read_like.py     # 프로필 관심목록 리더
├── carrot.py              # 두 기능을 연동한 검증 도구
└── README.md              # 프로젝트 설명서
```

## 🚀 주요 기능

### 1. 좋아요 자동화 봇 (`CarrotLikeBot`)
- 당근마켓 피드에서 자동으로 게시물에 좋아요 추가
- "거래완료", "예약중" 텍스트 자동 제거
- 토스트 메시지를 통한 성공/실패 감지
- UiAutomator2 crash 자동 복구
- 스크롤을 통한 연속 처리

**주요 메서드:**
- `run(max_posts, enable_scroll)`: 메인 실행 함수
- `process_post()`: 개별 게시물 처리
- `click_like_button()`: 좋아요 버튼 클릭
- `get_post_title()`: 게시물 제목 추출

### 2. 프로필 관심목록 리더 (`CarrotProfileReader`)
- 프로필 화면으로 자동 이동
- 관심목록의 모든 제목 수집
- "관심 있을 만한" 섹션 감지 시 자동 중단
- WebDriverWait를 통한 안정적인 요소 대기

**주요 메서드:**
- `run()`: 메인 실행 함수
- `get_liked_posts_from_profile()`: 관심목록 수집
- `extract_titles_from_textviews()`: XPath 기반 제목 추출

### 3. 검증 도구 (`carrot.py`)
- 좋아요 봇과 프로필 리더 연동
- 좋아요 누른 항목들이 프로필에 정상 반영되었는지 검증
- 누락된 항목 자동 감지 및 보고

## 🛠 설치 및 설정

### 필수 요구사항
```bash
pip install appium-python-client
pip install selenium
```

### 디바이스 설정
- Android 디바이스 (R3CN20HAC4A)
- USB 디버깅 활성화
- 당근마켓 앱 설치
- Appium Server 실행 (포트 4723)

## 📖 사용법

### 1. 좋아요 자동화만 실행
```python
from carrot_like import CarrotLikeBot

bot = CarrotLikeBot()
results = bot.run(max_posts=10, enable_scroll=True)
print(f"좋아요 성공: {results['liked_count']}개")
```

### 2. 관심목록 읽기만 실행
```python
from carrot_read_like import CarrotProfileReader

reader = CarrotProfileReader()
titles = reader.run()
print(f"관심목록: {len(titles)}개")
```

### 3. 통합 검증 실행
```python
from carrot import verify_likes

result = verify_likes()
if result:
    print("검증 성공!")
else:
    print("검증 실패!")
```

## ⚙️ 설정 옵션

### CarrotLikeBot 설정
- `max_posts`: 처리할 최대 게시물 수 (기본값: 10)
- `enable_scroll`: 스크롤 활성화 여부 (기본값: True)
- `device_name`: 디바이스 이름 (기본값: "R3CN20HAC4A")

### 타이밍 설정
- `DEFAULT_TIMEOUT = 5`: 요소 대기 시간
- `TOAST_TIMEOUT = 2`: 토스트 메시지 대기 시간
- `SCROLL_DELAY = 1`: 스크롤 후 대기 시간
- `PAGE_LOAD_DELAY = 2`: 페이지 로드 대기 시간

## 🔧 주요 기술 특징

### XPath 기반 요소 선택
- 안정적인 Android View 계층구조 탐색
- 동적 경로 결정 로직 (View[3] vs View[4])
- TextView 개수 기반 자동 판단

### 오류 처리 및 복구
- UiAutomator2 instrumentation crash 자동 감지
- 세션 자동 재시작 기능
- 요소 찾기 실패 시 재시도 로직

### 스마트 텍스트 처리
- 상태 텍스트 자동 제거 ("거래완료", "예약중")
- 중복 제목 방지 로직
- 종료 조건 자동 감지

## 🚨 주의사항

1. **디바이스 연결**: USB 디버깅이 활성화된 Android 디바이스 필요
2. **앱 상태**: 당근마켓 앱이 설치되어 있고 로그인된 상태여야 함
3. **네트워크**: 안정적인 인터넷 연결 필요
4. **화면 해상도**: 코드는 특정 해상도 기준으로 작성됨 (1080x2340)
5. **이용 약관**: 당근마켓 이용약관을 준수하여 사용

## 🐛 문제 해결

### 요소를 찾을 수 없음
- 앱 버전 업데이트로 인한 UI 변경 가능성
- XPath 경로 재확인 필요

### UiAutomator2 오류
- 디바이스 재연결
- Appium 서버 재시작
- 앱 강제 종료 후 재실행

### 좋아요 실패
- 네트워크 상태 확인
- 토스트 메시지 타이밍 조정
- 계정 상태 확인

## 📝 로그 예시

```
좋아요 봇 시작
게시물 제목: iPhone 13 팝니다
새로운 관심 추가 성공! (총 1개)
게시물 제목: 노트북 판매합니다
관심 상태 유지됨 (카운트 안함)

프로필 리더 시작...
프로필 화면으로 이동 완료
관심목록 섹션 클릭 완료
발견된 element 개수: 15
제목 발견: iPhone 13 팝니다
제목 발견: 노트북 판매합니다

검증 시작...
PASS: 좋아요 누른 모든 항목이 프로필 관심목록에 포함되어 있습니다!
```

## 📄 라이선스

이 프로젝트는 개인 학습 및 연구 목적으로 제작되었습니다.

## 🤝 기여

버그 리포트나 기능 개선 제안은 이슈로 등록해 주세요.