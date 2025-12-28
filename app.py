from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from crawler import NamuWikiCrawler
import os

app = Flask(__name__)

# CORS 설정 - Vercel 프론트엔드 허용
CORS(app, 
     origins=["*"],
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Content-Type"],
     supports_credentials=False,
     max_age=3600)

crawler = NamuWikiCrawler()

@app.route('/')
@cross_origin()
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

@app.route('/search', methods=['POST', 'OPTIONS'])
@cross_origin()
def search():
    """학교 검색 API"""
    if request.method == 'OPTIONS':
        return '', 204
    
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
    
    # Railway는 PORT 환경 변수 제공
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(debug=debug, host='0.0.0.0', port=port)

