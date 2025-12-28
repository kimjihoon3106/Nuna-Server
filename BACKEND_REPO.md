# 백엔드 레포지토리 구성

## 올려야 할 필수 파일들

### 1. Python 코드
```
app.py              # Flask 앱 메인 파일
crawler.py          # 나무위키 크롤러
```

### 2. 의존성 관리
```
requirements.txt    # Python 패키지 목록
```

### 3. 프론트엔드 파일들 (Flask가 서빙)
```
templates/
  ├── index.html
  └── results.html

static/
  ├── css/
  │   └── style.css
  ├── js/
  │   ├── config.js
  │   ├── main.js
  │   └── results.js
```

### 4. 문서
```
README.md           # 프로젝트 설명
DEPLOYMENT.md       # 배포 가이드 (선택사항)
```

### 5. 설정 파일
```
.gitignore         # Git 제외 파일 목록
```

### 6. 디렉토리 (빈 폴더는 안 올라가므로 .gitkeep 사용)
```
cache/.gitkeep     # 캐시 디렉토리 (런타임에 JSON 파일 생성됨)
```

## 올리면 안 되는 파일들 (.gitignore에 포함됨)

```
❌ __pycache__/           # Python 캐시
❌ cache/*.json           # 크롤링 캐시 파일
❌ .venv/, venv/          # 가상환경
❌ .env                   # 환경 변수 (비밀키 등)
❌ .DS_Store              # macOS 파일
❌ .vscode/, .idea/       # IDE 설정
```

## 전체 레포지토리 구조

```
nuna-backend/
├── app.py                  ✅ 필수
├── crawler.py              ✅ 필수
├── requirements.txt        ✅ 필수
├── README.md               ✅ 필수
├── DEPLOYMENT.md           ⭕ 선택
├── .gitignore             ✅ 필수
├── cache/
│   └── .gitkeep           ✅ 필수 (빈 디렉토리 유지용)
├── templates/             ✅ 필수
│   ├── index.html
│   └── results.html
└── static/                ✅ 필수
    ├── css/
    │   └── style.css
    └── js/
        ├── config.js
        ├── main.js
        └── results.js
```

## Git 명령어

### 초기 설정
```bash
git init
git add .
git commit -m "Initial commit: Nuna 백엔드"
```

### GitHub에 푸시
```bash
git remote add origin https://github.com/username/nuna-backend.git
git branch -M main
git push -u origin main
```

## 배포 플랫폼별 추가 파일

### Railway
- 자동 감지되므로 추가 파일 불필요
- `requirements.txt`만 있으면 자동으로 Flask 앱 인식

### Render
**`render.yaml` (선택)**
```yaml
services:
  - type: web
    name: nuna-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
```

**`requirements.txt`에 추가**
```
gunicorn==21.2.0
```

### Heroku
**`Procfile`**
```
web: gunicorn app:app
```

**`runtime.txt`**
```
python-3.11.0
```

## 중요 체크리스트

배포 전 확인:
- [ ] `cache/` 디렉토리가 `.gitignore`에 있는가?
- [ ] `.env` 파일이 있다면 `.gitignore`에 포함되었는가?
- [ ] `requirements.txt`에 모든 패키지가 포함되었는가?
- [ ] `__pycache__/` 등 불필요한 파일이 제외되었는가?
- [ ] README.md에 프로젝트 설명이 있는가?

배포 후:
- [ ] `cache/` 디렉토리가 자동 생성되는가?
- [ ] 쓰기 권한 문제가 없는가?
- [ ] 모든 엔드포인트가 동작하는가?
