import json

def process_data(data):
    if type(data) in [dict, list]:
        return json.dumps(data)
    elif type(data) in [float, int]:
        return str(data)
    else:
        return data

def response_ok(data):
    return process_data(data), 200, {'Content-Type': 'application/json'}

def response_error_generic(data):
    return process_data(data), 500, {'Content-Type': 'application/json'}

def response_error_not_found(data):
    return process_data(data), 404, {'Content-Type': 'application/json'}

def response_error_auth(data):
    return process_data(data), 401, {'Content-Type': 'application/json'}