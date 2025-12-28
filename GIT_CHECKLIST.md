# Git 커밋 체크리스트

## 백엔드 레포지토리에 포함되어야 할 파일들

### ✅ 필수 파일 (반드시 커밋)

#### Python 코드
- [x] `app.py` - Flask 애플리케이션
- [x] `crawler.py` - 나무위키 크롤러

#### 의존성
- [x] `requirements.txt` - Python 패키지 목록

#### 프론트엔드
- [x] `templates/index.html` - 메인 페이지
- [x] `templates/results.html` - 결과 페이지
- [x] `static/css/style.css` - 스타일시트
- [x] `static/js/config.js` - API URL 설정
- [x] `static/js/main.js` - 메인 페이지 로직
- [x] `static/js/results.js` - 결과 페이지 로직

#### 설정 파일
- [x] `.gitignore` - Git 제외 목록
- [x] `cache/.gitkeep` - 캐시 디렉토리 유지용

#### 문서
- [x] `README.md` - 프로젝트 설명

#### 배포 파일 (선택사항이지만 권장)
- [x] `Procfile` - Heroku 배포용
- [x] `runtime.txt` - Python 버전 지정
- [x] `DEPLOYMENT.md` - 배포 가이드

---

### ❌ 제외되어야 할 파일 (절대 커밋 금지)

#### 캐시 및 임시 파일
- [ ] `cache/*.json` - 크롤링 캐시 파일
- [ ] `__pycache__/` - Python 캐시
- [ ] `*.pyc`, `*.pyo` - 컴파일된 Python 파일

#### 환경 및 설정
- [ ] `.env` - 환경 변수 (비밀키 포함)
- [ ] `venv/`, `.venv/` - 가상환경

#### IDE 설정
- [ ] `.vscode/` - VS Code 설정
- [ ] `.idea/` - PyCharm 설정

#### OS 파일
- [ ] `.DS_Store` - macOS 파일
- [ ] `Thumbs.db` - Windows 파일

---

## Git 명령어

### 1. 초기화 및 상태 확인
```bash
# Git 초기화 (처음 한 번만)
git init

# 현재 상태 확인
git status

# .gitignore가 제대로 작동하는지 확인
# (cache/*.json, __pycache__ 등이 안 보여야 함)
```

### 2. 파일 추가
```bash
# 모든 파일 추가
git add .

# 또는 개별적으로 추가
git add app.py crawler.py requirements.txt
git add templates/ static/ cache/.gitkeep
git add README.md .gitignore
git add Procfile runtime.txt DEPLOYMENT.md
```

### 3. 커밋
```bash
git commit -m "Initial commit: Nuna 백엔드 서비스"

# 또는 더 자세한 커밋 메시지
git commit -m "feat: 학교 출신 유명인 검색 서비스 초기 버전

- Flask 백엔드 API
- 나무위키 크롤러
- 인물 필터링 로직
- 프로필 이미지 추출
- 반응형 프론트엔드
- CORS 설정
"
```

### 4. GitHub 연결 및 푸시
```bash
# GitHub에서 레포지토리 생성 후
git remote add origin https://github.com/username/nuna-backend.git

# 브랜치 확인
git branch

# main으로 이름 변경 (필요시)
git branch -M main

# 푸시
git push -u origin main
```

---

## 커밋 전 최종 체크

### 파일 확인
```bash
# 커밋될 파일 목록 확인
git status

# 제외되어야 할 파일이 있는지 확인
git status | grep -E "(cache.*json|__pycache__|\.pyc|venv|\.DS_Store)"
# → 아무것도 나오면 안 됨!
```

### .gitignore 테스트
```bash
# cache 디렉토리는 있지만 .json 파일은 제외되는지 확인
ls -la cache/
# → .gitkeep만 있어야 함

git status cache/
# → cache/.gitkeep만 추적되어야 함
```

### 디렉토리 구조 확인
```bash
tree -a -I '__pycache__|*.pyc|venv|.git'
```

---

## 배포 플랫폼별 체크리스트

### Railway
- [x] `requirements.txt` 있음
- [x] `app.py` 있음
- [x] Flask 앱 객체 이름이 `app`임

### Render
- [x] `requirements.txt` 있음
- [x] Start Command: `gunicorn app:app`
- [x] `gunicorn`이 requirements.txt에 포함됨

### Heroku
- [x] `Procfile` 있음
- [x] `runtime.txt` 있음
- [x] `requirements.txt` 있음
- [x] `gunicorn`이 requirements.txt에 포함됨

### Vercel (Serverless)
- [x] `vercel.json` 필요 (별도 생성 필요)
- [x] Python 3.9+ 사용

---

## 일반적인 실수 방지

### ❌ 하지 말아야 할 것
1. `.env` 파일 커밋 (API 키, 비밀키 노출)
2. `venv/` 디렉토리 커밋 (용량 큼)
3. `cache/*.json` 커밋 (개인 검색 기록)
4. `__pycache__/` 커밋 (불필요)
5. IDE 설정 커밋 (개인 환경)

### ✅ 해야 할 것
1. README.md 작성
2. requirements.txt 최신 상태 유지
3. .gitignore 설정
4. 배포 전 로컬 테스트
5. 커밋 메시지 명확하게 작성

---

## 문제 해결

### cache/ 디렉토리가 커밋되지 않을 때
```bash
# .gitkeep 파일이 있는지 확인
ls -la cache/

# .gitkeep 추가
touch cache/.gitkeep
git add cache/.gitkeep
```

### .gitignore가 작동하지 않을 때
```bash
# Git 캐시 초기화
git rm -r --cached .
git add .
git commit -m "fix: .gitignore 적용"
```

### 큰 파일이 실수로 커밋되었을 때
```bash
# 마지막 커밋 취소 (푸시 전)
git reset --soft HEAD~1

# 파일 제거 후 다시 커밋
git rm --cached 큰파일명
git commit -m "fix: 불필요한 파일 제거"
```
