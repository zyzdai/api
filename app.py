import os
import threading
from flask import Flask, request, jsonify, make_response, send_from_directory, redirect
from module import ttson,edge_tts,tools,fanqie,jm,rar2zip,_51cg,dddd_ocr,randomImg
app = Flask(__name__)

@app.route('/')
def rImg():
    img = randomImg.img()
    return redirect(img)

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

@app.route('/qqttson', methods=['GET', 'POST'])
def go_qqttson():
    voice_id = request.args.get('voice_id')
    speed_factor = request.args.get('speed_factor')
    text = request.args.get('text')
    pitch_factor = request.args.get('pitch_factor')
    is_None = tools.isEmpty((voice_id, speed_factor, text, pitch_factor))
    if is_None:
        return jsonify({"code": "异常", "message": "参数不能为空"})
    url = ttson.create(voice_id, speed_factor, text, pitch_factor)
    filepath = ttson.convert_to_wav(url)
    r = os.path.split(filepath)
    try:
        response = make_response(
            send_from_directory(r[0], r[1], as_attachment=True))
        return response
    except Exception as e:
        return jsonify({"code": "异常", "message": "{}".format(e)})


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
    # 启动清理 tmp 目录的线程
    clean_thread = threading.Thread(target=tools.clean_tmp_directory)
    clean_thread.start()
    app.run(host="0.0.0.0", port=8000)


