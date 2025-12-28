# Nuna Backend API

학교 출신 유명인 검색 API 백엔드 서버입니다.

나무위키의 학교 동문 목록을 크롤링하여 실제 인물만 추출하고, 프로필 이미지와 직업 정보를 제공합니다.

## 주요 기능

- 🔍 학교 이름으로 출신 유명인 검색 API
- 👤 크롤링 및 인물 필터링
- 🖼️ 프로필 이미지 자동 추출
-  검색 결과 캐싱
- � CORS 지원 (프론트엔드 분리 배포)

## 기술 스택

- **Backend**: Flask 3.0.0
- **Crawling**: requests, BeautifulSoup4, lxml
- **CORS**: Flask-CORS
- **Deploy**: Gunicorn (Production)

## API 엔드포인트

### GET /
서버 상태 확인

**응답**
```json
{
  "status": "ok",
  "message": "Nuna Backend API",
  "version": "1.0.0"
}
```

### POST /search
학교 출신 유명인 검색

**요청**
```json
{
  "school_name": "서울예술고등학교"
}
```

**응답**
```json
{
  "school_name": "서울예술고등학교",
  "count": 65,
  "celebrities": [
    {
      "name": "김고은",
      "job": "배우",
      "image_url": "https://i.namu.wiki/...",
      "namu_url": "https://namu.wiki/w/김고은"
    }
  ]
}
```

## 설치 및 실행

## 설치 및 실행

### 로컬 개발

```bash
# 1. 저장소 클론
git clone https://github.com/kimjihoon3106/Nuna-Server.git
cd Nuna-Server

# 2. 가상환경 생성
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 서버 실행
python app.py
```

서버가 `http://localhost:5001`에서 실행됩니다.

### 배포

```bash
# Gunicorn으로 실행
gunicorn app:app --bind 0.0.0.0:$PORT
```

## 프로젝트 구조

```
Nuna-Server/
├── app.py              # Flask API 서버
├── crawler.py          # ㄹ크롤러
├── requirements.txt    # Python 의존성
├── Procfile           # Heroku/Railway 배포 설정
├── runtime.txt        # Python 버전
├── .gitignore
├── README.md
└── cache/             # 크롤링 결과 캐시
    └── .gitkeep
```

## 크롤링 로직

1. **학교명 정규화**: 다양한 표기 지원 (예: 서울예고 ↔ 서울예술고등학교)
2. **동문 추출**: 동문 출신인물 추출
3. **인물 필터링**: 
   - 필터링
   - 실제 인물만 추출
4. **프로필 이미지**: 로고/배너 필터링 후 프로필 이미지 추출
5. **직업 정보**: 직업 키워드 자동 추출

## 캐싱

- 검색 결과를 `cache/` 디렉토리에 JSON으로 저장
- 동일 학교 재검색 시 즉시 반환
- 배포 시 write 권한 필요

## 환경 변수

필요한 경우 `.env` 파일 사용:

```env
FLASK_ENV=production
PORT=5001
```

## 라이센스

MIT License

## 관련 레포지토리

- Frontend: [Nuna-Client](https://github.com/kimjihoon3106/Nuna-Client) (별도 예정)

