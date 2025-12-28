from flask import Flask, request, jsonify
from flask_cors import CORS
from crawler import NamuWikiCrawler
import os

app = Flask(__name__)

# CORS 설정 - 모든 origin 허용 (프론트엔드 분리 배포)
CORS(app, resources={
    r"/*": {
        "origins": "*",  # 모든 도메인 허용
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

crawler = NamuWikiCrawler()

@app.route('/')
def index():
    """API 상태 확인"""
    return jsonify({
        'status': 'ok',
        'message': 'Nuna Backend API',
        'version': '1.0.0',
        'endpoints': {
            'POST /search': '학교 출신 유명인 검색'
        }
    })

@app.route('/search', methods=['POST'])
def search():
    """학교 검색 API"""
    data = request.get_json()
    school_name = data.get('school_name', '').strip()
    
    if not school_name:
        return jsonify({'error': '학교 이름을 입력해주세요.'}), 400
    
    try:
        print(f"[검색 요청] 학교명: {school_name}")
        result = crawler.crawl_school_celebrities(school_name)
        
        if 'error' in result:
            print(f"[오류] {result.get('error')}")
            return jsonify(result), 200  # 404 대신 200으로 반환하되 error 필드 포함
        
        print(f"[검색 성공] 연예인 {result.get('count', 0)}명 발견")
        return jsonify(result), 200
    except Exception as e:
        import traceback
        print(f"[예외 발생] {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'검색 중 오류가 발생했습니다: {str(e)}'}), 500

if __name__ == '__main__':
    # cache 디렉토리 확인
    if not os.path.exists('cache'):
        os.makedirs('cache')
    
    app.run(debug=True, host='0.0.0.0', port=5001)

