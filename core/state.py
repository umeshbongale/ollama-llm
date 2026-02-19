order_states = {}

def get_order(session_id):
    if session_id not in order_states:
        order_states[session_id] = {"stage": "browsing"}
    return order_states[session_id]

def reset_order(session_id):
    order_states[session_id] = {"stage": "browsing"}
