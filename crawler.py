import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import re
import json
import os

class NamuWikiCrawler:
    def __init__(self, cache_dir="cache"):
        self.base_url = "https://namu.wiki"
        self.cache_dir = cache_dir
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://namu.wiki/'
        }
        # 간단한 User-Agent 목록 (회피용)
        self.user_agents = [
            self.headers['User-Agent'],
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15'
        ]
        # 선택적 프록시 (환경 변수로 설정 가능)
        self.proxy_url = os.environ.get('PROXY_URL')
        
        # 캐시 디렉토리 생성
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def get_cache_path(self, school_name):
        """캐시 파일 경로 반환"""
        safe_name = re.sub(r'[^\w\s-]', '', school_name).strip()
        return os.path.join(self.cache_dir, f"{safe_name}.json")
    
    def load_cache(self, school_name):
        """캐시에서 데이터 로드"""
        cache_path = self.get_cache_path(school_name)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def save_cache(self, school_name, data):
        """데이터를 캐시에 저장"""
        cache_path = self.get_cache_path(school_name)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"캐시 저장 실패: {e}")
    
    def get_school_page(self, school_name):
        """학교 문서 페이지 가져오기"""
        # 여러 변형 시도
        variations = [
            school_name,  # 원본
            school_name.replace(' ', ''),  # 띄어쓰기 제거
            school_name.replace(' ', '·'),  # 나무위키 중간점
        ]
        
        # "고등학교" ↔ "고" 변환 추가
        if '고등학교' in school_name:
            # "서울예술고등학교" → "서울예술고"
            short_name = school_name.replace('고등학교', '고')
            variations.append(short_name)
            variations.append(short_name.replace(' ', ''))
        elif school_name.endswith('고'):
            # "서울예술고" → "서울예술고등학교"
            full_name = school_name[:-1] + '고등학교'
            variations.append(full_name)
            variations.append(full_name.replace(' ', ''))
        
        # 세션 생성
        session = requests.Session()
        session.headers.update(self.headers)
        if self.proxy_url:
            session.proxies.update({'http': self.proxy_url, 'https': self.proxy_url})

        # 각 variant에 대해 여러번 시도 (User-Agent 회전, 지수 백오프)
        for i, variant in enumerate(variations):
            encoded_name = urllib.parse.quote(variant)
            url = f"{self.base_url}/w/{encoded_name}"

            # variant 간 기본 대기
            if i > 0:
                time.sleep(1.5)

            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                # 시도할 때마다 User-Agent를 바꿔 본다
                ua = self.user_agents[(attempt - 1) % len(self.user_agents)]
                session.headers.update({'User-Agent': ua, 'Referer': self.headers.get('Referer')})

                try:
                    print(f"[시도] URL: {url} (variant={variant}, attempt={attempt}, UA={ua})")
                    response = session.get(url, timeout=12, allow_redirects=True)

                    if response.status_code == 200:
                        print(f"[성공] 학교 페이지 로드: {variant}")
                        return response.text
                    elif response.status_code == 404:
                        print(f"[404] 페이지 없음: {variant}")
                        break  # 이 variant는 없음, 다음 variant로
                    elif response.status_code == 403:
                        print(f"[403] 응답 코드: {variant} (attempt {attempt})")
                        # 지수 백오프
                        backoff = 1.5 * (2 ** (attempt - 1))
                        time.sleep(backoff)
                        continue
                    else:
                        print(f"[{response.status_code}] 응답 코드: {variant}")
                        break
                except requests.exceptions.RequestException as e:
                    print(f"[오류] 학교 페이지 요청 실패 ({variant}, attempt {attempt}): {e}")
                    time.sleep(1.5 * attempt)
                    continue
        
        return None
    
    def extract_alumni_section(self, html):
        """출신 인물 섹션 추출 - 리스트 항목에서만 추출"""
        soup = BeautifulSoup(html, 'lxml')
        alumni_list = []
        
        # "출신 인물" 또는 "출신" 섹션 찾기
        headings = soup.find_all(['h2', 'h3', 'h4', 'h5'])
        
        def extract_links_from_list_items(element):
            """리스트 항목(li)에서만 링크 추출 - 개선된 버전"""
            links_found = []
            if not element:
                return links_found
            
            # ul, ol 내의 모든 li 요소 찾기 (재귀적으로)
            list_items = element.find_all('li')
            print(f"[디버깅] 발견된 li 요소 개수: {len(list_items)}")
            
            for idx, li in enumerate(list_items):
                # li 내용 확인
                li_text = li.get_text().strip()[:100]
                print(f"[디버깅] li[{idx}] 내용: {li_text}")
                
                # li 내의 모든 링크 추출
                links = li.find_all('a', href=True)
                print(f"[디버깅] li[{idx}]의 링크 개수: {len(links)}")
                
                # 각 li에서 첫 번째 유효한 인물 링크만 추출
                found_person_in_li = False
                for link in links:
                    name = link.get_text().strip()
                    href = link.get('href', '')
                    print(f"[디버깅] 링크 발견: {name} -> {href}")
                    
                    # "가나다순", "나무위키" 등 일반 링크 제외
                    if name in ['가나다순', '나무위키', 'ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']:
                        print(f"[디버깅] 일반 링크로 필터링: {name}")
                        continue
                    
                    # 나무위키 내부 링크만, 분류 링크 제외
                    if name and href.startswith('/w/') and not href.startswith('/w/분류:'):
                        print(f"[디버깅] 유효한 나무위키 링크: {name}")
                        # 강력한 필터링 적용
                        if self.is_likely_person_name(name):
                            print(f"[디버깅] 인물 이름으로 판단: {name}")
                            links_found.append({
                                'name': name,
                                'url': href
                            })
                            found_person_in_li = True
                            break  # 첫 번째 인물 링크만 추출하고 중단
                        else:
                            print(f"[디버깅] 인물 아님으로 필터링: {name}")
            
            print(f"[디버깅] 최종 추출된 링크 수: {len(links_found)}")
            return links_found
        
        for heading in headings:
            text = heading.get_text().strip()
            # "출신 인물", "출신", "동문", "졸업생" 등 키워드 확인
            if any(keyword in text for keyword in ['출신 인물', '출신', '동문', '졸업생', '저명한 동문', '주요 동문']):
                print(f"[섹션 발견] {text}")
                
                # 방법 1: 헤딩 다음의 ul, ol 리스트 찾기 (우선)
                next_list = heading.find_next(['ul', 'ol'])
                print(f"[디버깅] 방법1 - 리스트 찾기: {next_list is not None}")
                if next_list:
                    print(f"[디버깅] 리스트 요소: {next_list.name}, 클래스: {next_list.get('class', [])}")
                    # 다음 헤딩까지의 리스트만 확인
                    next_heading = next_list.find_next(['h2', 'h3', 'h4', 'h5'])
                    
                    # 리스트 범위 확인
                    current_list = next_list
                    list_count = 0
                    while current_list and list_count < 10:  # 최대 10개 리스트만 확인
                        list_count += 1
                        if next_heading:
                            # 다음 헤딩 이전인지 확인
                            test_elem = current_list.find_next(['h2', 'h3', 'h4', 'h5'])
                            if test_elem and test_elem == next_heading:
                                # 리스트가 헤딩 이전에 있음
                                pass
                            elif test_elem and test_elem != next_heading:
                                # 다른 헤딩을 만났으므로 중단
                                break
                        
                        # 리스트 항목에서만 링크 추출
                        links = extract_links_from_list_items(current_list)
                        for link in links:
                            if not any(a['name'] == link['name'] for a in alumni_list):
                                alumni_list.append(link)
                        
                        # 다음 형제 리스트 확인
                        current_list = current_list.find_next_sibling(['ul', 'ol'])
                        if not current_list:
                            break
                        
                        # 다음 헤딩을 지나쳤는지 확인
                        if next_heading:
                            check_heading = current_list.find_previous(['h2', 'h3', 'h4', 'h5'])
                            if check_heading and check_heading == next_heading:
                                # 헤딩을 지나쳤으므로 중단
                                break
                    
                    if alumni_list:
                        print(f"[출신 인물 추출 성공 (리스트)] {len(alumni_list)}명")
                        return alumni_list
                
                # 방법 2: 헤딩 다음의 div 내부에서 ul, ol 찾기
                next_div = heading.find_next(['div', 'section'])
                print(f"[디버깅] 방법2 - div 찾기: {next_div is not None}")
                if next_div:
                    # 다음 헤딩 찾기
                    next_heading = next_div.find_next(['h2', 'h3', 'h4', 'h5'])
                    print(f"[디버깅] 다음 헤딩: {next_heading.get_text().strip() if next_heading else 'None'}")
                    
                    # div 내부의 리스트 찾기 (재귀적으로)
                    lists_in_div = next_div.find_all(['ul', 'ol'], recursive=True)
                    print(f"[디버깅] div 내 리스트 개수: {len(lists_in_div)}")
                    for list_elem in lists_in_div:
                        # 다음 헤딩 이전에 있는 리스트만 확인
                        if next_heading:
                            # 리스트가 헤딩 이후에 있는지 확인
                            after_heading = list_elem.find_previous(['h2', 'h3', 'h4', 'h5'])
                            if after_heading and after_heading == next_heading:
                                # 헤딩 이후의 리스트이므로 건너뜀
                                continue
                        
                        links = extract_links_from_list_items(list_elem)
                        for link in links:
                            if not any(a['name'] == link['name'] for a in alumni_list):
                                alumni_list.append(link)
                    
                    if alumni_list:
                        print(f"[출신 인물 추출 성공 (div 내 리스트)] {len(alumni_list)}명")
                        return alumni_list
                
                # 방법 3: 헤딩 다음의 형제 요소에서 리스트 찾기
                current = heading
                max_iterations = 20
                iteration = 0
                print(f"[디버깅] 방법3 - 형제 요소 탐색 시작")
                
                while current and iteration < max_iterations:
                    iteration += 1
                    current = current.find_next_sibling()
                    
                    if not current:
                        print(f"[디버깅] 형제 요소 없음")
                        break
                    
                    print(f"[디버깅] 형제 요소: {current.name if hasattr(current, 'name') else 'None'}")
                    
                    # 다음 헤딩을 만나면 중단
                    if current.name in ['h2', 'h3', 'h4', 'h5']:
                        print(f"[디버깅] 다음 헤딩 발견: {current.get_text().strip()}")
                        break
                    
                    # 리스트 요소인 경우
                    if current.name in ['ul', 'ol']:
                        print(f"[디버깅] 리스트 발견: {current.name}")
                        links = extract_links_from_list_items(current)
                        print(f"[디버깅] 리스트에서 추출한 링크 수: {len(links)}")
                        for link in links:
                            if not any(a['name'] == link['name'] for a in alumni_list):
                                alumni_list.append(link)
                    # div 내부의 리스트 찾기
                    elif current.name in ['div', 'section']:
                        lists = current.find_all(['ul', 'ol'], recursive=False)
                        print(f"[디버깅] div 내 리스트 개수: {len(lists)}")
                        for list_elem in lists:
                            links = extract_links_from_list_items(list_elem)
                            print(f"[디버깅] 리스트에서 추출한 링크 수: {len(links)}")
                            for link in links:
                                if not any(a['name'] == link['name'] for a in alumni_list):
                                    alumni_list.append(link)
                
                if alumni_list:
                    print(f"[출신 인물 추출 성공 (형제 요소)] {len(alumni_list)}명")
                    return alumni_list
                
                # 방법 4: 헤딩 다음의 모든 요소에서 직접 링크 찾기 (최후의 수단)
                print(f"[디버깅] 방법4 - 직접 링크 검색")
                next_heading = heading.find_next(['h2', 'h3', 'h4', 'h5'])
                current_elem = heading
                max_depth = 50
                depth = 0
                
                while current_elem and depth < max_depth:
                    depth += 1
                    current_elem = current_elem.find_next()
                    
                    if not current_elem:
                        break
                    
                    # 다음 헤딩을 만나면 중단
                    if current_elem.name in ['h2', 'h3', 'h4', 'h5']:
                        if next_heading and current_elem == next_heading:
                            break
                    
                    # 링크가 있는 요소 찾기
                    if hasattr(current_elem, 'find_all'):
                        links = current_elem.find_all('a', href=True)
                        for link in links:
                            name = link.get_text().strip()
                            href = link.get('href', '')
                            if name and href.startswith('/w/') and not href.startswith('/w/분류:'):
                                if self.is_likely_person_name(name):
                                    if not any(a['name'] == name for a in alumni_list):
                                        alumni_list.append({
                                            'name': name,
                                            'url': href
                                        })
                                        print(f"[디버깅] 링크 발견: {name}")
                
                if alumni_list:
                    print(f"[출신 인물 추출 성공 (직접 검색)] {len(alumni_list)}명")
                    return alumni_list
        
        # 대안: 문서 전체에서 "출신" 키워드 주변 링크 찾기
        if not alumni_list:
            print("[대안 방법] 문서 전체에서 출신 인물 검색")
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                # 링크 주변 텍스트 확인 (부모와 형제 요소 포함)
                parent = link.parent
                if parent:
                    # 부모 요소의 텍스트 확인
                    parent_text = parent.get_text().lower()
                    # 형제 요소도 확인
                    prev_sibling = parent.find_previous_sibling()
                    next_sibling = parent.find_next_sibling()
                    context_text = parent_text
                    if prev_sibling:
                        context_text += ' ' + prev_sibling.get_text().lower()
                    if next_sibling:
                        context_text += ' ' + next_sibling.get_text().lower()
                    
                    if any(keyword in context_text for keyword in ['출신', '동문', '졸업생', '출신 인물']):
                        name = link.get_text().strip()
                        href = link.get('href', '')
                        if name and href.startswith('/w/') and not href.startswith('/w/분류:'):
                            # 일반 단어 필터링
                            if self.is_likely_person_name(name):
                                if not any(a['name'] == name for a in alumni_list):
                                    alumni_list.append({
                                        'name': name,
                                        'url': href
                                    })
        
        if alumni_list:
            print(f"[출신 인물 추출 성공 (대안)] {len(alumni_list)}명")
        else:
            print("[출신 인물 추출 실패] 출신 인물을 찾을 수 없음")
            # 디버깅: 모든 헤딩 출력
            print("[디버깅] 문서의 모든 헤딩:")
            for h in soup.find_all(['h2', 'h3', 'h4', 'h5']):
                print(f"  - {h.get_text().strip()}")
        
        return alumni_list
    
    def is_likely_person_name(self, name):
        """이름이 사람 이름일 가능성이 있는지 간단히 확인 (빠른 필터링)"""
        if not name or len(name.strip()) <= 1:
            return False
        
        name_clean = name.strip()
        
        # 괄호가 있는 경우 괄호 앞의 이름만 추출
        # 예: "강우성(피아니스트)" -> "강우성"
        if '(' in name_clean:
            name_without_parenthesis = name_clean.split('(')[0].strip()
            # 괄호 앞이 비어있거나 숫자만 있으면 교통 관련 (예: "160(나주)")
            if not name_without_parenthesis or re.match(r'^\d+$', name_without_parenthesis):
                return False
            # 괄호 앞의 이름으로 계속 검증
            name_clean = name_without_parenthesis
        
        # 숫자가 포함된 이름 제외 (버스 노선 번호 등)
        if re.search(r'\d+', name_clean):
            # 단, 연도나 생년월일이 아닌 경우만 제외
            # 예: "1990년생" 같은 건 허용하지만 "송정19", "좌석02" 같은 건 제외
            if not re.search(r'(년|월|일|생)', name_clean):
                return False
        
        # 역, 공항, 정류장 등 교통 관련 키워드
        transport_keywords = ['역', '공항', '정류장', '터미널', '버스', '지하철', '기차']
        if any(keyword in name_clean for keyword in transport_keywords):
            return False
        
        # 일반적인 단어나 개념 제외 (완전 일치만 체크하는 키워드와 포함 체크하는 키워드 구분)
        # 완전 일치 체크 (짧은 단어들)
        exact_match_keywords = [
            '음악', '미술', '발레', '정치', '경제', '사회',
            '문화', '역사', '지리', '과학', '기술', '공학',
            '소설', '영화', '드라마', '게임', '만화',
            '음식', '요리', '스포츠', '운동', '종목',
            '도시', '나라', '국가', '지역', '산', '강',
            '동물', '식물', '물건', '기계', '장비'
        ]
        
        # 포함 체크 (긴 키워드들)
        contains_keywords = [
            '대중교통', '교통', '버스', '지하철', '택시', '기차', '비행기',
            '학교', '고등학교', '중학교', '초등학교', '대학교', '대학',
            '회사', '기업', '단체', '조직', '기관', '협회',
            '좌석', '송정', '일곡', '상무', '진월', '진곡', '임곡'  # 버스 노선 관련
        ]
        
        name_lower = name_clean.lower()
        
        # 완전 일치 체크
        if name_lower in exact_match_keywords:
            return False
        
        # 포함 체크
        for keyword in contains_keywords:
            if keyword in name_lower:
                return False
        
        # 너무 짧은 이름 제외 (1글자만)
        if len(name_clean) <= 1:
            return False
        
        # 특수문자나 기호가 많이 포함된 경우 제외
        if len(re.sub(r'[가-힣a-zA-Z0-9\s]', '', name_clean)) > 2:
            return False
        
        return True
    
    def is_person(self, name, person_html):
        """실제 인물인지 확인"""
        # 특정 키워드 완전 제외
        exclude_names = ['나무위키', '가나다순']
        if name.strip() in exclude_names:
            print(f"[인물 아님] 제외 키워드: {name}")
            return False
        
        # 일반적인 단어나 개념 제외 (완전 일치만 체크하는 키워드와 포함 체크하는 키워드 구분)
        # 완전 일치 체크 (짧은 단어들)
        exact_match_keywords = [
            '음악', '미술', '발레', '정치', '경제', '사회',
            '문화', '역사', '지리', '과학', '기술',
            '소설', '영화', '드라마', '게임',
            '음식', '요리', '스포츠', '운동'
        ]
        
        # 포함 체크 (긴 키워드들)
        contains_keywords = [
            '대중교통', '교통', '버스', '지하철', '택시', '기차',
            '학교', '고등학교', '중학교', '초등학교', '대학교',
            '회사', '기업', '단체', '조직', '기관'
        ]
        
        name_lower = name.lower()
        
        # 완전 일치 체크
        if name_lower in exact_match_keywords:
            print(f"[인물 아님] 일반 단어/개념: {name}")
            return False
        
        # 포함 체크
        for keyword in contains_keywords:
            if keyword in name_lower:
                print(f"[인물 아님] 일반 단어/개념: {name}")
                return False
        
        # 너무 짧은 이름 제외 (1글자만)
        if len(name.strip()) <= 1:
            print(f"[인물 아님] 이름이 너무 짧음: {name}")
            return False
        
        soup = BeautifulSoup(person_html, 'lxml')
        text = soup.get_text().lower()
        
        # 인물 문서의 특징 확인
        # 1. 생년월일, 출생일 등이 있는지 확인
        person_indicators = ['출생', '생년', '생일', '출생일', '태어난', '출생지', 
                           '사망', '사망일', '나이', '본명', '본관', '가족']
        
        has_person_indicator = any(indicator in text for indicator in person_indicators)
        
        # 2. 분류에서 "인물" 관련 분류 확인
        category_links = soup.find_all('a', href=re.compile(r'/w/분류:'))
        has_person_category = False
        for link in category_links:
            link_text = link.get_text().lower()
            if '인물' in link_text or '사람' in link_text:
                has_person_category = True
                break
        
        # 인물 문서가 아니면 False
        if not has_person_indicator and not has_person_category:
            print(f"[인물 아님] 인물 문서의 특징이 없음: {name}")
            return False
        
        return True
    
    def is_celebrity(self, person_html):
        """연예인 여부 판별 (예술인 포함)"""
        soup = BeautifulSoup(person_html, 'lxml')
        text = soup.get_text().lower()
        
        # 연예인 & 예술인 키워드 확인
        celebrity_keywords = [
            # 방송/연예
            '배우', '가수', '아이돌', '래퍼', '방송인', '개그맨', 
            '코미디언', 'mc', '엠씨', '아나운서', '모델', '연예인',
            '싱어', 'singer', 'actor', 'actress', 'idol', 'rapper',
            '뮤지컬', 'musical', '탤런트', '예능',
            # 음악 예술
            '피아니스트', 'pianist', '바이올리니스트', 'violinist',
            '첼리스트', 'cellist', '성악가', '지휘자', 'conductor',
            '작곡가', 'composer', '연주자', '클래식',
            # 무용 예술
            '무용가', '발레리나', 'ballerina', '댄서', 'dancer',
            '안무가', 'choreographer',
            # 미술 예술
            '화가', 'painter', '조각가', 'sculptor', '예술가', 'artist',
            # 기타 예술
            '성우', '뮤지션', 'musician'
        ]
        
        for keyword in celebrity_keywords:
            if keyword in text:
                return True
        
        # 분류 섹션 확인
        categories = soup.find_all('div', class_=re.compile('category|분류'))
        for category in categories:
            category_text = category.get_text().lower()
            for keyword in celebrity_keywords:
                if keyword in category_text:
                    return True
        
        # 문서 하단 분류 링크 확인
        category_links = soup.find_all('a', href=re.compile(r'/w/분류:'))
        for link in category_links:
            link_text = link.get_text().lower()
            for keyword in celebrity_keywords:
                if keyword in link_text:
                    return True
        
        return False
    
    def get_person_info_from_html(self, html, person_url):
        """HTML에서 인물 정보 추출 (재요청 없이)"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            url = f"{self.base_url}{person_url}"
            
            # 프로필 이미지 찾기 - alt에 인물 이름이 있는 이미지 우선
            image_url = None
            
            # person_url에서 인물 이름 추출 (예: /w/형독 -> 형독)
            person_name_from_url = person_url.split('/')[-1]
            try:
                person_name_from_url = urllib.parse.unquote(person_name_from_url)
                # 괄호 제거 (예: 형독(래퍼) -> 형독)
                if '(' in person_name_from_url:
                    person_name_from_url = person_name_from_url.split('(')[0].strip()
            except:
                pass
            
            # 프로필 이미지 찾기 - "출생" 텍스트 바로 앞 이미지
            image_url = None
            
            # "출생" 텍스트를 포함하는 요소 찾기
            birth_tags = soup.find_all(string=re.compile(r'출생'))
            
            for birth_text in birth_tags:
                # "출생" 텍스트의 부모 태그 찾기
                birth_parent = birth_text.parent if hasattr(birth_text, 'parent') else None
                if not birth_parent:
                    continue
                
                # 부모 태그 이전의 모든 형제 요소에서 이미지 찾기 (역순으로)
                for prev_elem in birth_parent.find_all_previous():
                    if prev_elem.name == 'img':
                        src = prev_elem.get('src', '')
                        data_src = prev_elem.get('data-src', '')
                        actual_src = data_src if data_src else src
                        alt = prev_elem.get('alt', '').lower()
                        height = prev_elem.get('height', '')
                        
                        # 필터링
                        if not actual_src or actual_src.startswith('data:'):
                            continue
                        if '.svg' in actual_src.lower():
                            continue
                        if height == "100%":
                            continue
                        if any(keyword in alt for keyword in ['로고', 'logo', '배너', 'banner', '아이콘', 'icon']):
                            continue
                        
                        # 첫 번째 유효한 이미지 발견
                        if actual_src.startswith('//'):
                            image_url = f"https:{actual_src}"
                            break
                        elif actual_src.startswith('http'):
                            image_url = actual_src
                            break
                
                # 이미지를 찾았으면 중단
                if image_url:
                    break
            
            # 우선순위 2: alt가 일치하는 이미지가 없으면, 테이블의 첫 번째 이미지
            if not image_url:
                tables = soup.find_all('table')
                for table in tables[:3]:  # 처음 3개 테이블만 확인
                    imgs = table.find_all('img', src=True)
                    for img in imgs:
                        src = img.get('src', '')
                        data_src = img.get('data-src', '')
                        actual_src = data_src if data_src else src
                        alt = img.get('alt', '').lower()
                        height = img.get('height', '')
                        
                        # 필터링
                        if not actual_src or actual_src.startswith('data:'):
                            continue
                        if '.svg' in actual_src.lower():
                            continue
                        if height == "100%":
                            continue
                        if any(keyword in alt for keyword in ['로고', 'logo', '배너', 'banner', '아이콘', 'icon']):
                            continue
                        
                        # 첫 번째 유효한 이미지 선택
                        if actual_src.startswith('//'):
                            image_url = f"https:{actual_src}"
                            break
                        elif actual_src.startswith('http'):
                            image_url = actual_src
                            break
                    
                    if image_url:
                        break
            
            # 직업 정보 추출
            job = None
            job_keywords = {
                '배우': ['배우', 'actor', 'actress'],
                '가수': ['가수', 'singer'],
                '아이돌': ['아이돌', 'idol'],
                '래퍼': ['래퍼', 'rapper'],
                '방송인': ['방송인', 'broadcaster'],
                '개그맨': ['개그맨', 'comedian'],
                'MC': ['MC', '엠씨'],
                '아나운서': ['아나운서', 'announcer'],
                '모델': ['모델', 'model']
            }
            
            text = soup.get_text().lower()
            for job_name, keywords in job_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        job = job_name
                        break
                if job:
                    break
            
            # 소속 그룹 찾기
            group = None
            group_keywords = ['소속사', '소속', '그룹', '팀']
            for keyword in group_keywords:
                headings = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b'])
                for heading in headings:
                    if keyword in heading.get_text():
                        next_elem = heading.find_next_sibling()
                        if next_elem:
                            group_text = next_elem.get_text().strip()
                            if group_text:
                                group = group_text.split('\n')[0].strip()
                                break
                if group:
                    break
            
            return {
                'image_url': image_url,
                'job': job or '연예인',
                'group': group,
                'namu_url': url
            }
        except Exception as e:
            print(f"인물 정보 가져오기 실패 ({person_url}): {e}")
            return None
    
    def get_person_info(self, person_url):
        """인물 정보 가져오기 (별도 요청 필요 시)"""
        url = f"{self.base_url}{person_url}"
        
        try:
            time.sleep(1)  # 요청 간 딜레이
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            html = response.text
            return self.get_person_info_from_html(html, person_url)
        except Exception as e:
            print(f"인물 정보 가져오기 실패 ({person_url}): {e}")
            return None
    
    def crawl_school_celebrities(self, school_name):
        """학교 출신 연예인 크롤링"""
        print(f"[크롤링 시작] 학교명: {school_name}")
        
        # 캐시 확인
        cached_data = self.load_cache(school_name)
        if cached_data:
            print(f"[캐시 사용] 학교명: {school_name}")
            return cached_data
        
        # 학교 페이지 가져오기
        html = self.get_school_page(school_name)
        if not html:
            print(f"[오류] 학교 문서를 찾을 수 없음: {school_name}")
            return {'error': f'학교 문서를 찾을 수 없습니다. (검색어: {school_name})'}
        
        # 출신 인물 섹션 추출
        print(f"[출신 인물 섹션 추출 중]")
        alumni_list = self.extract_alumni_section(html)
        print(f"[출신 인물 발견] {len(alumni_list)}명")
        
        if not alumni_list:
            return {'error': '출신 인물 정보를 찾을 수 없습니다. 문서에 출신 인물 섹션이 없을 수 있습니다.'}
        
        # 각 인물 확인
        celebrities = []
        max_check = 100  # 최대 확인 인원 (충분히 크게)
        check_count = min(len(alumni_list), max_check)
        print(f"[출신 인물 정보 수집 시작] 총 {check_count}명 확인 예정")
        for i, person in enumerate(alumni_list[:max_check]):  # 최대 100명까지 확인
            person_url = person['url']
            person_html = None
            
            try:
                time.sleep(1)  # 요청 간 딜레이 (1.5초 -> 1초로 단축)
                response = requests.get(
                    f"{self.base_url}{person_url}",
                    headers=self.headers,
                    timeout=10
                )
                response.raise_for_status()
                person_html = response.text
            except Exception as e:
                print(f"[인물 페이지 요청 실패] {person['name']}: {e}")
                continue
            
            # 먼저 실제 인물인지 확인
            if not self.is_person(person['name'], person_html):
                print(f"[건너뜀] 인물이 아님: {person['name']}")
                continue
            
            # 출신 인물 섹션에 있는 모든 인물 포함
            print(f"[출신 인물 추가] {person['name']}")
            # 이미 person_html이 있으므로 재요청 없이 정보 추출
            person_info = self.get_person_info_from_html(person_html, person_url)
            if person_info:
                celebrities.append({
                    'name': person['name'],
                    'job': person_info.get('job', '인물'),
                    'group': person_info.get('group'),
                    'image_url': person_info.get('image_url'),
                    'namu_url': person_info.get('namu_url', f"{self.base_url}{person_url}")
                })
        
        result = {
            'school_name': school_name,
            'celebrities': celebrities,
            'count': len(celebrities)
        }
        
        # 캐시 저장 (출신 인물이 있든 없든 저장하여 재검색 시 빠르게 응답)
        self.save_cache(school_name, result)
        print(f"[캐시 저장 완료] 학교명: {school_name}, 출신 인물 수: {len(celebrities)}")
        
        return result

