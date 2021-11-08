## Furfellas Server

### 주요 기능
* Mysql(ORM)
  * 유저(현재는 관리자만), 액션, 장소, 사진, 사진 타입, 할일 등 저장 
* Docker-compose
  * flask app(gunicorn), nginx, mysql 설정
* Pytest 
  * 각 엔드포인트 테스트(리소스 생성,추가,수정,삭제)
  * 헬퍼 함수 테스트