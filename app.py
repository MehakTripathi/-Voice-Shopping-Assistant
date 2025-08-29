from flask import Flask, render_template, request, jsonify
import re, json, os

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "shopping_data.json")

# load or init persistent store (simple JSON file)
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        store = json.load(f)
else:
    store = {"shopping_list": [], "history": []}

def save_store():
    with open(DATA_FILE, "w") as f:
        json.dump(store, f, indent=2)

def parse_command(command):
    command = command.lower().strip()
    qty = 1
    m = re.search(r"(\d+)", command)
    if m:
        qty = int(m.group(1))

    # simple action detection
    if any(k in command for k in ("add ", "buy ", "i need", "need ", "please add", "put ")):
        # strip common verbs
        item = re.sub(r'^(add|buy|i need|need|please add|put)\s*', '', command).strip()
        # remove quantity words like "2 bottles of"
        item = re.sub(r'\b\d+\b', '', item).strip()
        item = re.sub(r'of\b', '', item).strip()
        return ("add", item, qty)
    if any(k in command for k in ("remove ", "delete ", "take off ", "remove from")):
        item = re.sub(r'^(remove|delete|take off|remove from)\s*', '', command).strip()
        return ("remove", item, qty)
    if any(k in command for k in ("find ", "search ", "look for ")):
        item = re.sub(r'^(find|search|look for)\s*', '', command).strip()
        return ("search", item, qty)
    return ("unknown", command, qty)

# simple categorizer (very small mapping)
CATEGORY_MAP = {
    "milk": "Dairy", "cheese": "Dairy", "yogurt": "Dairy",
    "apple": "Produce", "apples": "Produce", "banana": "Produce", "oranges": "Produce",
    "bread": "Bakery", "eggs": "Dairy", "water": "Beverages", "juice": "Beverages",
    "toothpaste": "Personal Care", "shampoo": "Personal Care", "soap": "Personal Care"
}

def categorize(item):
    for k, v in CATEGORY_MAP.items():
        if k in item:
            return v
    return "Other"

@app.route('/')
def index():
    return render_template('index.html', shopping_list=store['shopping_list'])

@app.route('/api/list', methods=['GET'])
def get_list():
    return jsonify(store['shopping_list'])

@app.route('/api/voice', methods=['POST'])
def voice():
    payload = request.get_json() or {}
    command = payload.get('command', '').strip()
    if not command:
        return jsonify({"error": "No command provided"}), 400

    action, item, qty = parse_command(command)
    item = item.strip()
    resp = {"action": action, "item": item, "quantity": qty}

    if action == "add" and item:
        entry = {"item": item, "quantity": qty, "category": categorize(item)}
        store['shopping_list'].append(entry)
        store['history'].append({"action": "add", "item": item})
        save_store()
        resp['message'] = f"Added {qty} × {item}"
        resp['list'] = store['shopping_list']
        return jsonify(resp)
    elif action == "remove" and item:
        before = len(store['shopping_list'])
        store['shopping_list'] = [e for e in store['shopping_list'] if e['item'] != item]
        after = len(store['shopping_list'])
        store['history'].append({"action": "remove", "item": item})
        save_store()
        if before == after:
            resp['message'] = f"Item not found: {item}"
        else:
            resp['message'] = f"Removed {item}"
        resp['list'] = store['shopping_list']
        return jsonify(resp)
    elif action == "search" and item:
        found = [e for e in store['shopping_list'] if item in e['item']]
        resp['message'] = f"Search results for '{item}'"
        resp['results'] = found
        return jsonify(resp)
    else:
        return jsonify({"message": "Sorry, I didn't understand the command.", "raw": command}), 200

@app.route('/api/suggestions', methods=['GET'])
def suggestions():
    # basic suggestions based on history or simple seasonal mock data
    suggestions = [
        {"item": "bread", "reason": "Frequently bought"},
        {"item": "eggs", "reason": "Often bought with milk"},
        {"item": "almond milk", "reason": "Substitute for milk"}
    ]
    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
