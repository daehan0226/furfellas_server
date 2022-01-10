## Furfellas Server
[![Python 3.8](https://img.shields.io/badge/python-v3.8-blue)](https://www.python.org/downloads/release/python-380/)
### 주요 기능
1. 펫 프로필
   1. 펫 이름, 몸무게, 성격, 성별, 소개 등의 프로필 정보
2. 할일 리스트
   1. 약 먹거나 목욕 일정, 병원 방문 등의 일회성, 다회성 일들을 기록
3. 앨범
   1. 사진 속 활동, 사진의 위치, 펫을 선택하여 저장하고, 해당 정보를 필터링 하여 사진 검색
4. 관리자는 위의 정보들을 추가, 수정할 수 있음
### 기술 및 구현 간략한 소개
* Mysql(Sqlalchemy ORM) - Docker
  * 유저, 유저 역할, 액션, 장소, 사진, 사진 타입, 할일, 세션 데이터 저장 
  ![DB TABLES](https://user-images.githubusercontent.com/47915302/140753090-4de6dab3-8556-46b1-b75f-588b7b6c122c.png)
* Docker-compose
  * flask app - gunicorn - nginx
* Pytest 
  * 각 엔드포인트 테스트(리소스 생성,추가,수정,삭제)
  * 헬퍼 함수 테스트
  * 픽스쳐 - API context(test), TEST DB
* RESTFUL API 
![Restful_api](https://user-images.githubusercontent.com/47915302/148562064-14def396-530d-493e-a560-882f6e8f8c22.png)
* 응답 상태 코드
  * 성공
     * 200 Success
     * 201 Created
     * 202 Accepted(사진 비동기 구글 드라이브 업로드) 
     * 204 No content(수정, 삭제 성공)
  * 실패
    * 400 Fail
    * 401 No auth(로그인 필요)
    * 403 Forbbiden(관리자만 접속 가능)
    * 404 Not found (식별자를 통한 조회 시 없는 경우)
    * 500 서버 에러