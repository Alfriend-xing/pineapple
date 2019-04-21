#coding=utf-8
from flask import Flask,render_template,url_for,jsonify
import json
import random
import time
from module import Job,mksession


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/jobinfo/')
def index_job():
    return render_template('jobinfo.html',data=[{'title':'Python开发1','selery':'12k','resbon':'1.aaa<br>2.bbb<br>3.ccc<br>4.ddd<br>5.eee'},
    {'title':'Python开发1','selery':'12k','resbon':'1.aaa<br>2.bbb<br>3.ccc<br>4.ddd<br>5.eee'},
    {'title':'Python开发1','selery':'12k','resbon':'1.aaa<br>2.bbb<br>3.ccc<br>4.ddd<br>5.eee'},
    {'title':'Python开发1','selery':'12k','resbon':'1.aaa<br>2.bbb<br>3.ccc<br>4.ddd<br>5.eee'},
    {'title':'Python开发1','selery':'12k','resbon':'1.aaa<br>2.bbb<br>3.ccc<br>4.ddd<br>5.eee'}])

@app.route('/jobtrend/')
def trend_job():
    return render_template('jobtrend.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'),500

@app.route('/api/job/<int:page>')
def job_api(page):
    session=mksession()
    res=[]
    data=session.query(Job).order_by(Job.id.desc())\
        .limit(10).offset((page-1)*10)
    for i in data:
        if not i.name:
            break
        res.append({'name':i.name,
        'selery':i.selery,
        'city':i.city,
        'date':i.creat_time,
        'msg':i.msg.replace('\n','<br>') if i.msg else 'null'})
    return jsonify(res)
if __name__ == '__main__':
    app.run(host='0.0.0.0')







