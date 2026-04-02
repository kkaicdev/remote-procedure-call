def handle(dispatcher, req):
    if "method" not in req:
        raise Exception("invalid request")

    return dispatcher.call(req["method"], req.get("params", []))

def response(req_id, result=None, error=None):
    base = {"jsonrpc": "2.0", "id": req_id}

    if error is None:
        return base | {"result": result}
    
    return base | {
        "error": {
            "code": -32000,
            "message": error
        }
    }

def process(dispatcher, data):
    def single(req):
        try:
            result = handle(dispatcher, req)
            return None if req.get("id") is None else response(req.get("id"), result=result)
        except Exception as e:
            return None if req.get("id") is None else response(req.get("id"), error=str(e))
        
    if isinstance(data, list):
        res = []
        for r in data:
            out = single(r)
            if out is not None:
                res.append(out)

        return res or None
        
    return single(data)
