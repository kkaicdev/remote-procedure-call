def handle(dispatcher, req):
    if not isinstance(req, dict) or req.get("jsonrpc") != "2.0":
        raise ValueError("invalid request")
        
    method = req.get("method")
    if not isinstance(method, str):
        raise ValueError("invalid method")

    params = req.get("params")
    if params is None:
        params = []
    elif not isinstance(params, (list, dict)):
        raise ValueError("invalid params")

    return dispatcher.call(method, params)

def response(req_id, *, result=None, error=None):
    base = {"jsonrpc": "2.0", "id": req_id}

    if error is not None:
        return base | {
            "error": {
                "code": -32000,
                "message": error
            }
        }

    return base | {"result": result}

def _execute(dispatcher, req):
    req_id = req.get("id")

    try:
        result = handle(dispatcher, req)
        return None if req_id is None else response(req_id, result=result)
    except Exception:
        return None if req_id is None else response(req_id, error="internal error")

def process(dispatcher, data):
    if isinstance(data, list):
        results = [r for r in (_execute(dispatcher, req) for req in data) if r is not None]
        return results or None

    return _execute(dispatcher, data)