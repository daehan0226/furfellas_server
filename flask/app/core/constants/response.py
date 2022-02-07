status = {
    "OK": 200,  # GET - DATA OR EMPTY LIST
    "CREATED": 201,  # POST,
    "ACCEPTED": 202,  # POST - ASYNC
    "NO CONTENT": 204,  # DELETE, PUT
    "BAD REQUEST": 400,  # GENERAIL FAIL - CLIENT ERROR
    "NO AUTH": 401,  # LOGIN NEEDED
    "FORBIDDEN": 403,  # ADMIN ONLY
    "NOT FOUND": 404,  # NOT FOUND BY IDENTIFIER
    "CONFLICT": 409,  # CREATE/UPDATE Fail
    "SEVER ERROR": 500,  # SEVER ERROR
}

status_code_msg = {y: x for x, y in status.items()}


message = {
    "kr": {
        "OK": "성공",  # GET - DATA OR EMPTY LIST
        "CREATED": "생성",  # POST,
        "ACCEPTED": "요청 성공",
        "NO CONTENT": "요청 성공",  # DELETE, PUT
        "BAD REQUEST": "잘못된 요청입니다.",  # GENERAIL FAIL - CLIENT ERROR
        "NO AUTH": "로그인이 필요합니다.",  # LOGIN NEEDED
        "FORBIDDEN": "접근 권한이 없습니다.",  # ADMIN ONLY
        "NOT FOUND": "원하시는 데이터를 찾지 못했습니다.",  # NOT FOUND BY IDENTIFIER
        "CONFLICT": "충돌이 발생했습니다.",
        "SEVER ERROR": "죄송합니다. 다음에 다시 시도해주세요.",  # SEVER ERROR
    },
    "en": {
        "OK": "Success",  # GET - DATA OR EMPTY LIST
        "CREATED": "Created",  # POST
        "ACCEPTED": "Request accepted",
        "NO CONTENT": "Request has succeeded",  # DELETE, PUT
        "BAD REQUEST": "BAD REQUEST",  # GENERAIL FAIL - CLIENT ERROR
        "NO AUTH": "Please login first",  # LOGIN NEEDED
        "FORBIDDEN": "No permission",  # ADMIN ONLY
        "NOT FOUND": "Couldn't find what you want",  # NOT FOUND BY IDENTIFIER
        "CONFLICT": "Conflict occurred",
        "SEVER ERROR": "Oops, something went wrong",  # SEVER ERROR
    },
}
