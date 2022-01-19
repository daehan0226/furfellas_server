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
  ![DB TABLES](https://user-images.githubusercontent.com/47915302/150068250-8911080d-79d7-4988-abd9-c88d3d180385.png)
* Docker-compose
  * flask app - gunicorn - nginx
* Pytest 
  * 각 엔드포인트 테스트(리소스 생성,추가,수정,삭제)
  * 헬퍼 함수 테스트
  * 픽스쳐 - API context(test), TEST DB
# API DOC
<!-- ## Authorization
| Key | Value | 
| :--- | :--- | 
| `Authorization` | Session key | -->

## Status Codes

API returns the following status codes:

| Status Code | Description |
| :--- | :--- |
| 200 | `OK` |
| 201 | `CREATED` |
| 202 | `ACCEPTED` |
| 204 | `No CONTENT` |
| 400 | `BAD REQUEST` |
| 401 | `NO AUTH` |
| 403 | `FORBBIDEN` |
| 404 | `NOT FOUND` |
| 500 | `INTERNAL SERVER ERROR` |

## Endpoints
### /actions
<details>
<summary>Fetch actions</summary>

| | |
| :--- | :--- | 
| URL	| /actions/ |
| Method	| GET |
| Success Response	| Code: 200 {"result":[{"id": 1, "name": "play"}, ...}], "message": "Success"}
| Error Response	| Code: 500 {"Message": "Oops, something went wrong"}
| Sample Request	| axios.get('/actions/') |
</details>
<details>
<summary>Create an action</summary>

| | |
| :--- | :--- | 
| URL	| /actions/ |
| Query Params | ?name=action-name |
| Method	| POST |
| Success Response	| Code: 201 {"result":action_id, "message": "Created"}
| Error Response	| Code: 400 {"Message": "Dupilicate action name"} <br> Code: 401 {"message": "Please login first"} <br> Code: 403  {"message": "No permission"} <br> Code: 500  {"Message": "Oops, something went wrong"}
| Sample Request	| axios.post('/actions/?name=action name') |
</details>
<details>
<summary>Fetch an action</summary>

| | |
| :--- | :--- | 
| URL	| /actions/<strong>int:action_id</strong> |
| URL Parameters |	Required: <strong>action_id=[integer]</strong>|
| Method	| GET |
| Success Response	| Code: 200 {"message": "Success", "result": {id: action_id, name: action_name}} 
| Error Response	| Code: 404 {"message": "Couldn't find what you want"} <br> Code: 500 {"message": "Oops, something went wrong"}
| Sample Request	| axios.get(/actions/1) |
</details>
<details>
<summary>Delete an action</summary>

| | |
| :--- | :--- | 
| URL	| /actions/<strong>int:action_id</strong> |
| URL Parameters |	Required: <strong>action_id=[integer]</strong>|
| Method	| DELETE |
| Success Response	| Code: 204 {"message": "Request has succeeded"}
| Error Response	| Code: 401 {"message": "Please login first"} <br> Code: 403  {"message": "No permission"} <br> Code: 404 {"message": "Couldn't find what you want"} <br> Code: 500  {"message": "Oops, something went wrong"}
| Sample Request	| axios.delete(/actions/1) |
</details>
<details>
<summary>Update an action</summary>

| | |
| :--- | :--- | 
| URL	| /actions/<strong>int:action_id</strong> |
| URL Parameters |	Required: <strong>action_id=[integer]</strong> |
| Query Params | ?name=action-name |
| Method	| PUT |
| Success Response	| Code: 204 {"message": "Request has succeeded"}
| Error Response	| Code: 401  {"message": "Please login first"} <br> Code: 403 {"message": "No permission"} <br> Code: 404  {"message": "Couldn't find what you want"} <br> Code: 500 {"message": "Oops, something went wrong"}
| Sample Request	| axios.put('/actions/?name=new-action-name')  |
</details>

