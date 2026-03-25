import json
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
# 配置文件路径
VOTE_FILE_PATH = "vote_data.json"

# 初始化投票文件（如果不存在）
def init_vote_file():
    default_data = {
        "version": "1.0",
        "lastUpdated": "2026-03-24T00:00:00.000Z",
        "voteData": {
            "洛茜": 0,
            "弭弗": 10,
            "李芷妍": 0,
            "庄方宜": 0,
            "卡缪": 0
        },
        "icon": {
            "洛茜": "/static/avatars/luoxi.png",
            "弭弗": "/static/avatars/mifu.png",
            "李芷妍": "/static/avatars/lizhiyan.png",
            "庄方宜": "/static/avatars/zhuangfangyi.png",
            "卡缪": "/static/avatars/kamui.png"
        }
    }
    if not os.path.exists(VOTE_FILE_PATH):
        with open(VOTE_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)

# 读取投票数据
def get_vote_data():
    init_vote_file()
    with open(VOTE_FILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# 更新投票数据
def update_vote_data(role_name):
    data = get_vote_data()
    if role_name in data["voteData"]:
        data["voteData"][role_name] += 1
        # 更新最后修改时间（简化版，实际可加时间戳）
        from datetime import datetime
        data["lastUpdated"] = datetime.utcnow().isoformat() + "Z"
        with open(VOTE_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    return False

# 主页路由（渲染抽卡工具+投票区域）
@app.route('/')
def index():
    vote_data = get_vote_data()
    return render_template('index.html', vote_data=vote_data)

# 投票接口
@app.route('/vote', methods=['POST'])
def vote():
    role_name = request.json.get('role_name')
    if not role_name:
        return jsonify({"success": False, "msg": "角色名不能为空"}), 400
    
    if update_vote_data(role_name):
        return jsonify({
            "success": True,
            "msg": "投票成功",
            "new_votes": get_vote_data()["voteData"][role_name]
        })
    else:
        return jsonify({"success": False, "msg": "角色不存在"}), 404

# 获取最新投票数据接口（用于前端刷新）
@app.route('/get_votes', methods=['GET'])
def get_votes():
    return jsonify(get_vote_data())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
