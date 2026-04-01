class Dispatcher:
    def __init__(self):
        self.methods = {}

    def register(self, name, fn):
        self.methods[name] = fn

    def call(self, method, params):
        fn = self.methods.get(method)
        if not fn:
            raise Exception(f"method not found: {method}")

        if isinstance(params, dict):
            return fn(**params)
        if isinstance(params, list):
            return fn(*params)
        return fn()