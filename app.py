import os
import threading
from flask import Flask, request, jsonify, make_response, send_from_directory, redirect,render_template
from module import ttson,edge_tts,tools,fanqie,jm,rar2zip,_51cg,dddd_ocr
app = Flask(__name__)


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
@app.route('/dddd_ocr_b64', methods=['POST'])
def go_dddd_ocr_b64():
    data = request.data.decode('utf-8')
    if len(data) <= 0:
        return jsonify({"code": "异常", "message": "data参数不能为空"})
    code = dddd_ocr.get_captcha_fromB64(data)
    return jsonify({"code": "正常", "message": "{}".format(code)})

@app.route('/dddd_ocr', methods=['GET', 'POST'])
def go_dddd_ocr_url():
    url = request.args.get('url')
    if len(url) <= 0:
        return jsonify({"code": "异常", "message": "url参数不能为空"})
    code = dddd_ocr.get_captcha(url)
    return jsonify({"code": "正常", "message": "{}".format(code)})


if __name__ == '__main__':
    app.config["MODULE"] = 'module'
    app.config["TMP"] = 'tmp'
    os.makedirs(app.config["MODULE"], exist_ok=True)
    os.makedirs(app.config["TMP"], exist_ok=True)

    # 启动清理 tmp 目录的线程
    clean_thread = threading.Thread(target=tools.clean_tmp_directory)
    clean_thread.start()
    app.run(host="0.0.0.0", port=8000)


