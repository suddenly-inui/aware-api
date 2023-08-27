ERRORS = {
    "1": "フォーマットが変",
}

def send_error(code: int, target):
    return {
        "error": {
            "code": code,
            "message": ERRORS[f"{code}"],
            "target": target
        }        
	}