import os
import sqlite3
from flask import Flask, render_template, request, jsonify, url_for

app = Flask(__name__)

# 数据库路径（Vercel 临时目录可写）
DB_PATH = '/tmp/votes.db'

# 角色列表（与前端一致）
ROLES = ['洛茜', '弭弗', '李芷妍', '庄方宜', '卡缪']

# 头像文件名映射（文件需放在 static/avatars/ 下）
AVATAR_FILES = {
    '洛茜': 'luoxi.png',
    '弭弗': 'mifu.png',
    '李芷妍': 'lizhiyan.png',
    '庄方宜': 'zhuangfangyi.png',
    '卡缪': 'kamui.png'
}

def init_db():
    """初始化 SQLite 数据库，如果表不存在则创建，并插入初始票数"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS votes
                 (role TEXT PRIMARY KEY, count INTEGER)''')
    for role in ROLES:
        c.execute('INSERT OR IGNORE INTO votes (role, count) VALUES (?, 0)', (role,))
    conn.commit()
    conn.close()

def get_votes_from_db():
    """从数据库读取所有角色票数，返回字典"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT role, count FROM votes')
    rows = c.fetchall()
    conn.close()
    return {role: count for role, count in rows}

def update_vote(role):
    """为指定角色增加一票，返回更新后的票数，如果角色不存在则返回 None"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 先检查角色是否存在
    c.execute('SELECT count FROM votes WHERE role = ?', (role,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    new_count = row[0] + 1
    c.execute('UPDATE votes SET count = ? WHERE role = ?', (new_count, role))
    conn.commit()
    conn.close()
    return new_count

# 启动时初始化数据库
init_db()

@app.route('/')
def index():
    """主页：渲染模板，并注入初始投票数据"""
    votes = get_votes_from_db()
    # 构建图标映射：前端需要完整的静态文件 URL
    icon_map = {}
    for role in ROLES:
        if role in AVATAR_FILES:
            icon_map[role] = url_for('static', filename=f'avatars/{AVATAR_FILES[role]}')
        else:
            icon_map[role] = url_for('static', filename='avatars/default.png')
    vote_data = {
        'voteData': votes,
        'icon': icon_map
    }
    return render_template('index.html', vote_data=vote_data)

@app.route('/get_votes')
def get_votes():
    """获取最新投票数据（用于前端刷新）"""
    votes = get_votes_from_db()
    icon_map = {}
    for role in ROLES:
        if role in AVATAR_FILES:
            icon_map[role] = url_for('static', filename=f'avatars/{AVATAR_FILES[role]}')
        else:
            icon_map[role] = url_for('static', filename='avatars/default.png')
    return jsonify({
        'voteData': votes,
        'icon': icon_map
    })

@app.route('/vote', methods=['POST'])
def vote():
    """处理投票请求"""
    data = request.get_json()
    role = data.get('role_name')
    if not role or role not in ROLES:
        return jsonify({'success': False, 'message': '无效的角色名'}), 400
    new_votes = update_vote(role)
    if new_votes is None:
        return jsonify({'success': False, 'message': '角色不存在'}), 404
    return jsonify({'success': True, 'new_votes': new_votes})
