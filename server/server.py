# -*- coding: utf-8 -*-
# @Time    : 2019/4/30 下午3:57
# @Author  : yu_hsuan_chen@trendmicro.com
# @File    : server
# @Version : 3.6

import os
from flask import Flask, render_template, request, make_response, jsonify, send_from_directory, send_file
from gevent import monkey
from gevent.pywsgi import WSGIServer

monkey.patch_all()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('abc.html')


@app.route('/download/database', methods=['GET'])
def download_database():
    directory = os.getcwd()
    response = make_response(send_from_directory(directory, 'logparser.db', as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format("logparser.db".encode().decode('utf-8'))
    return response


if __name__ == '__main__':
    # app.run(debug=True)
    http_server = WSGIServer(('0.0.0.0', 8080), app)
    http_server.serve_forever()
