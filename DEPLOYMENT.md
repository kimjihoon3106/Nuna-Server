# 배포 가이드

## 환경 설정

### 로컬 개발 환경
- 자동으로 `http://localhost:5001`을 백엔드 URL로 사용
- 별도 설정 불필요

### 프로덕션 환경 (배포 시)

#### 1. 백엔드 배포
백엔드를 배포한 후, 실제 백엔드 URL을 받습니다.
예: `https://nuna-backend.railway.app`

#### 2. 프론트엔드 설정 변경
`static/js/config.js` 파일에서 프로덕션 URL을 변경:

```javascript
production: {
    baseURL: 'https://nuna-backend.railway.app'  // ← 여기를 실제 백엔드 URL로 변경
}
```

#### 3. 백엔드 CORS 설정 변경
`app.py` 파일에서 프론트엔드 도메인을 추가:

```python
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:*",
            "http://127.0.0.1:*",
            "https://nuna.vercel.app"  # ← 여기를 실제 프론트엔드 URL로 변경
        ],
        ...
    }
})
```

## 배포 시나리오

### 시나리오 1: 같은 서버에서 프론트+백엔드 함께 배포
- Railway, Render, Heroku 등에서 Flask 앱 전체 배포
- URL 설정 불필요 (상대 경로 사용)
- 가장 간단한 방법

### 시나리오 2: 프론트와 백엔드 분리 배포
- 프론트엔드: Vercel, Netlify, GitHub Pages 등
- 백엔드: Railway, Render, Heroku 등
- 위의 "프론트엔드 설정 변경" 및 "백엔드 CORS 설정 변경" 필요

## 추천 배포 방법

### Railway에 전체 배포 (추천)
1. Railway 가입
2. 새 프로젝트 생성
3. GitHub 저장소 연결
4. 자동 배포 완료
5. 생성된 URL로 접속

### Vercel + Railway 분리 배포
1. **백엔드 (Railway)**:
   - Railway에서 Python 앱 배포
   - 백엔드 URL 복사: `https://nuna-backend.railway.app`

2. **프론트엔드 (Vercel)**:
   - `static/js/config.js`에서 production baseURL 변경
   - `app.py`에서 CORS origins에 Vercel 도메인 추가
   - Vercel에 배포

## 환경 변수 사용 (고급)

더 유연한 방법으로, 환경 변수를 사용할 수 있습니다:

### config.js를 동적으로 생성
```javascript
const API_BASE_URL = window.ENV_API_URL || 'http://localhost:5001';
```

### HTML에서 주입
```html
<script>
    window.ENV_API_URL = '{{ api_base_url }}';
</script>
```

### Flask에서 환경 변수 읽기
```python
import os
api_base_url = os.environ.get('API_BASE_URL', 'http://localhost:5001')
```

## 체크리스트

배포 전 확인사항:
- [ ] `requirements.txt`에 모든 패키지 포함됨
- [ ] `config.js`의 production URL 설정 완료
- [ ] `app.py`의 CORS origins 설정 완료
- [ ] 로컬에서 테스트 완료
- [ ] 캐시 디렉토리 생성 확인 (`cache/` 폴더)

배포 후 확인사항:
- [ ] API 엔드포인트 동작 확인 (백엔드 URL/search)
- [ ] CORS 에러 없는지 확인 (브라우저 콘솔)
- [ ] 실제 검색 기능 동작 확인
- [ ] 이미지 로딩 확인
