# encoding=utf-8
import argparse
import base64
import json
import sqlite3

import ddddocr
from flask import Flask, request,g
import hashlib

parser = argparse.ArgumentParser(description="使用ddddocr搭建的最简api服务")
parser.add_argument("-p", "--port", type=int, default=9898)
parser.add_argument("--ocr", action="store_true", help="开启ocr识别")
parser.add_argument("--old", action="store_true", help="OCR是否启动旧模型")
parser.add_argument("--det", action="store_true", help="开启目标检测")

args = parser.parse_args()

app = Flask(__name__)

DATABASE = 'data.db'

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
# Execute the SQL command to modify the table
        cursor.execute('''CREATE TABLE IF NOT EXISTS rule (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            host TEXT,
                            path TEXT,
                            input TEXT,
                            img TEXT,
                            title TEXT,
                            type TEXT,
                            idcard TEXT,
                            code INTEGER
                            )''')

        cursor.execute('''CREATE INDEX IF NOT EXISTS index_path ON rule (path)''')
# Commit the changes to the database
        db.commit()

# 重写row_factory方法，返回字典
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(DATABASE)
        db.row_factory = dict_factory
        g._database = db
# execute a query
        cursor.execute('SELECT * FROM rule WHERE path = ?',[path])
        rows = cursor.fetchall()
        app.logger.info(rows)
        if rows:
            return json.dumps({"code":531,"data":rows})
        else:
            return json.dumps({"code":533,"info": "未找到规则"})
    except Exception as e:
        return set_ret(e, "json")
@app.route('/captchaHostAdd',methods=['POST'])
def addOcr():
    try:
        rsp = request.get_json()
        path = get_path_md5(rsp['path'])
        app.logger.info(path)
        db = get_db()
        cursor = db.cursor()
# execute a query
        cursor.execute('SELECT * FROM rule WHERE path = ?',[path])
        data = cursor.fetchone()
        app.logger.info(data)
        app.logger.info('-------')
        if  data is None:
#add rsp to sqlite
            rsp['code'] = 531
            rsp['path'] = path
            columns = ', '.join(rsp.keys())
            placeholders = ', '.join('?' * len(rsp))
            sql = 'INSERT INTO rule ({}) VALUES ({})'.format(columns, placeholders)
            values = [int(x) if isinstance(x, bool) else x for x in rsp.values()]
            app.logger.info(sql)
            app.logger.info(values)
            cursor.execute(sql, values)
# 获取受影响的行数
            rowcount = cursor.rowcount
# 判断是否插入成功
            if rowcount > 0:
                app.logger.info("插入成功")
            else:
                app.logger.info("插入失败")
#提交事务
            db.commit()
            app.logger.info('-------')
            return json.dumps({"code": 200})
        return set_ret("not in", "json")
    except Exception as e:
        return set_ret(e, "json")


if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=args.port)
