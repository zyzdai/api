import json
import os
import threading
import time
import uuid

from flask import Flask, request, jsonify, make_response, send_from_directory, redirect, render_template, send_file
from module import ttson,edge_tts,tools,fanqie,jm,rar2zip,_51cg,dddd_ocr
app = Flask(__name__)

# 设置允许上传的文件类型
ALLOWED_EXTENSIONS = {'xbs'}
XBS_REBUILD_PATH = './xbsrebuild_linux'
# 初始化全局变量
# 是否完成
is_done = False
update_xbs_path = ''
xbs_check_result = {}
# 待删除的文件
to_delete_files = []

def xbs2json(xbs_path):
    global to_delete_files
    out_path = os.path.join(app.config["JSON"],str(uuid.uuid4())+'.json')
    to_delete_files.append(out_path)
    cmd = f'./{XBS_REBUILD_PATH} xbs2json -i {xbs_path} -o {out_path}'
    os.system(cmd)
    if not os.path.exists(out_path):
        print('xbsrebuild failed')
        exit(0)
    else:
        return out_path

def json2xbs(json_path):
    out_path = os.path.join(app.config["UPDATE_XBS"],str(uuid.uuid4())+'.xbs')
    cmd = f'./{XBS_REBUILD_PATH} json2xbs -i {json_path} -o {out_path}'
    os.system(cmd)
    if not os.path.exists(out_path):
        print('xbsrebuild failed')
        exit(0)
    else:
        return out_path

# 定义允许上传文件的函数
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def updatePwd(xbs_path):
    global update_xbs_path,is_done
    tmp = xbs2json(xbs_path)
    os.remove(xbs_path)
    # 打开文件修改密码
    with open(tmp,'r') as f:
        data = json.load(f)
        for key, value in data.items():
            if isinstance(value, dict):
                if 'password' in value:
                    del value['password']
                if 'lastModifyTime' in value:
                    # 1708308624.367167
                    value['lastModifyTime'] = str(time.time())
                with open(tmp,'w') as f:
                    json.dump(data,f,indent=4)
    update_xbs_path = json2xbs(tmp)
    os.remove(tmp)
    is_done = True



# 定义首页路由,上传文件
@app.route('/nopwd', methods=['GET', 'POST'])
def index():
    global xbs_path,is_done,to_delete_files
    is_done = False
    if request.method == 'POST':
        file = request.files['file']
        # 保存文件到uploads文件夹,重命名xbs
        if file and allowed_file(file.filename):
            filename = str(uuid.uuid4())+".xbs"
            xbs_path = os.path.join(app.config['XBS'], filename)
            to_delete_files.append(xbs_path)
            file.save(xbs_path)
            updatePwd(xbs_path)
            return jsonify({'redirect': request.url})
    return render_template('index.html')
@app.route('/download', methods=['GET'])
def download_file():
    global update_xbs_path
    return send_file(update_xbs_path, as_attachment=True)
# 刷新结果
@app.route('/refresh', methods=['GET'])
def refresh_result():
    global is_done,xbs_check_result
    if is_done:
        # 构建更新后xbs下载链接
        return jsonify({'status': 'finished', 'message': '完成','xbs_check_result':xbs_check_result})
    else:
        return jsonify({'status': 'running', 'message': '尚未完成','xbs_check_result':xbs_check_result})

@app.route('/')
def tts():
    tools.clearTmpFiles()
    return 'welcome to my tts!'

@app.route('/ttson', methods=['GET', 'POST'])
def go_ttson():
    voice_id = request.args.get('voice_id')
    speed_factor = request.args.get('speed_factor')
    text = request.args.get('text')
    pitch_factor = request.args.get('pitch_factor')
    is_None = tools.isEmpty((voice_id, speed_factor, text, pitch_factor))
    if is_None:
        return jsonify({"code": "异常", "message": "参数不能为空"})
    url = ttson.create(voice_id, speed_factor, text, pitch_factor)
    return redirect(url)

@app.route('/edge_tts', methods=['GET', 'POST'])
def go_edge_tts():
    text = request.args.get('text')
    voice = request.args.get('voice')
    rate = request.args.get('rate')
    is_None = tools.isEmpty((text, voice, rate))
    if is_None:
        return jsonify({"code": "异常", "message": "参数不能为空"})
    filePath = edge_tts.create(text, voice, rate)
    r = os.path.split(filePath)
    try:
        response = make_response(
            send_from_directory(r[0], r[1], as_attachment=True))
        return response
    except Exception as e:
        return jsonify({"code": "异常", "message": "{}".format(e)})

@app.route('/fanqie', methods=['GET'])
def getContent_():
    item_id = request.args.get('item_id')
    if len(item_id) <= 0:
        return jsonify({"code": "异常", "message": "item_id参数不能为空"})
    return fanqie.getContent(item_id)

@app.route('/jm', methods=['GET', 'POST'])
def go_jm():
    url = request.args.get('url')
    if len(url) <= 0:
        return jsonify({"code": "异常", "message": "url参数不能为空"})
    outfile = jm.on_image_loaded(url)
    r = os.path.split(outfile)
    try:
        response = make_response(
            send_from_directory(r[0], outfile, as_attachment=True))
        return response
    except Exception as e:
        return jsonify({"code": "异常", "message": "{}".format(e)})

@app.route('/rar2zip')
def go_r2z():
    url = request.args.get('url')
    if len(url) <= 0 or url.find('http') == -1:
        return jsonify({"code": "异常", "message": "rarurl参数异常"})

    zipName = rar2zip.r2z(url)
    r = os.path.split(zipName)
    try:
        response = make_response(
            send_from_directory(r[0], r[1], as_attachment=True))
        return response
    except Exception as e:
        return jsonify({"code": "异常", "message": "{}".format(e)})

@app.route('/51cg', methods=['GET', 'POST'])
def cg_decrypt_image():
    url = request.args.get('url')
    if len(url) <= 0:
        return jsonify({"code": "异常", "message": "url参数不能为空"})
    out_path = _51cg.decrypt_image(url)
    r = os.path.split(out_path)
    try:
        response = make_response(
            send_from_directory(r[0], r[1], as_attachment=True))
        return response
    except Exception as e:
        return jsonify({"code": "异常", "message": "{}".format(e)})

@app.route('/<opt>/<img_type>', methods=['POST'])
@app.route('/<opt>/<img_type>/<ret_type>', methods=['POST'])
def ocr(opt, img_type='file', ret_type='text'):
    try:
        img = dddd_ocr.get_img(request, img_type)
        if opt == 'ocr':
            result = dddd_ocr.server.classification(img)
        elif opt == 'det':
            result = dddd_ocr.server.detection(img)
        else:
            raise f"<opt={opt}> is invalid"
        return dddd_ocr.set_ret(result, ret_type)
    except Exception as e:
        return dddd_ocr.set_ret(e, ret_type)


@app.route('/slide/<algo_type>/<img_type>', methods=['POST'])
@app.route('/slide/<algo_type>/<img_type>/<ret_type>', methods=['POST'])
def slide(algo_type='compare', img_type='file', ret_type='text'):
    try:
        target_img = dddd_ocr.get_img(request, img_type, 'target_img')
        bg_img = dddd_ocr.get_img(request, img_type, 'bg_img')
        result = dddd_ocr.server.slide(target_img, bg_img, algo_type)
        return dddd_ocr.set_ret(result, ret_type)
    except Exception as e:
        return dddd_ocr.set_ret(e, ret_type)



if __name__ == '__main__':
    app.config["MODULE"] = 'module'
    app.config["TMP"] = 'tmp'
    os.makedirs(app.config["MODULE"], exist_ok=True)
    os.makedirs(app.config["TMP"], exist_ok=True)
    app.config['WORKER'] = 'worker'
    app.config['UPDATE_XBS'] = 'worker/update_xbs'
    app.config['XBS'] = 'worker/xbs'
    app.config['JSON'] = 'worker/json'
    os.makedirs(app.config['WORKER'], exist_ok=True)
    os.makedirs(app.config['XBS'], exist_ok=True)
    os.makedirs(app.config['UPDATE_XBS'], exist_ok=True)
    os.makedirs(app.config['JSON'], exist_ok=True)
    # 启动清理 tmp 目录的线程
    clean_thread = threading.Thread(target=tools.clean_tmp_directory)
    clean_thread.start()
    app.run(host="0.0.0.0", port=8000)


