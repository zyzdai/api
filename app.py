import os
from io import BytesIO
import uuid
from flask import Flask, request, jsonify, make_response
from module import edge_tts, tools, fanqie, jm, rar2zip, _51cg, dddd_ocr,manwa,reecho
app = Flask(__name__)

@app.route('/')
def index():
    return 'ok'

@app.route('/edge_tts', methods=['GET'])
def go_edge_tts():
    text = request.args.get('text')
    voice = request.args.get('voice')
    rate = request.args.get('rate')
    is_None = tools.isEmpty((text, voice, rate))
    if is_None:
        return jsonify({"code": "异常", "message": "参数不能为空"})
    filePath = edge_tts.create(text, voice, rate)
    data = BytesIO(open(filePath, 'rb').read())
    # 删除临时文件
    os.remove(filePath)
    response = make_response(data)
    # 设置响应头部信息，指定附件名称
    response.headers.set('Content-Disposition', 'attachment',
                         filename=f'{uuid.uuid4()}.mp3')
    response.headers.set('Content-Type', 'audio/mpeg')
    return response

@app.route('/edge_tts_post', methods=['POST'])  # Changed to POST
def go_edge_tts_post():
    data = request.json  # Expecting JSON data in the POST request
    text = data.get('text')
    voice = data.get('voice')
    rate = data.get('rate')

    is_None = tools.isEmpty((text, voice, rate))
    if is_None:
        return jsonify({"code": "异常", "message": "参数不能为空"})

    filePath = edge_tts.create(text, voice, rate)
    data = BytesIO(open(filePath, 'rb').read())
    # 删除临时文件
    os.remove(filePath)

    response = make_response(data)
    # 设置响应头部信息，指定附件名称
    response.headers.set('Content-Disposition', 'attachment',
                         filename=f'{uuid.uuid4()}.mp3')
    response.headers.set('Content-Type', 'audio/mpeg')
    
    return response

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
    data = BytesIO(open(outfile, 'rb').read())
    # 删除临时文件
    os.remove(outfile)
    response = make_response(data)
    # 设置响应头部信息，指定附件名称
    response.headers.set('Content-Disposition', 'attachment',
                         filename=f'{uuid.uuid4()}.jpg')
    response.headers.set('Content-Type', 'image/jpeg')
    return response


@app.route('/manwa', methods=['GET', 'POST'])
def go_manwa():
    url = request.args.get('url')
    if len(url) <= 0:
        return jsonify({"code": "异常", "message": "url参数不能为空"})
    key = request.args.get('key')
    if len(key) <= 0:
        return jsonify({"code": "异常", "message": "key参数不能为空"})
    iv = request.args.get('iv')
    if len(iv) <= 0:
        return jsonify({"code": "异常", "message": "iv参数不能为空"})
    decrypted_bytes = manwa.decrypt_image(url,key,iv)
    img_io = BytesIO(decrypted_bytes)
    response = make_response(img_io)
    # 设置响应头部信息，指定附件名称
    response.headers.set('Content-Disposition', 'attachment',
                         filename=f'{uuid.uuid4()}.jpg')
    response.headers.set('Content-Type', 'image/jpeg')
    return response

@app.route('/rar2zip')
def go_r2z():
    url = request.args.get('url')
    if len(url) <= 0 or url.find('http') == -1:
        return jsonify({"code": "异常", "message": "rarurl参数异常"})

    zipName = rar2zip.r2z(url)
    data = BytesIO(open(zipName, 'rb').read())
    # 删除临时文件
    os.remove(zipName)
    response = make_response(data)
    # 设置响应头部信息，指定附件名称
    response.headers.set('Content-Disposition', 'attachment',
                         filename=f'{uuid.uuid4()}.zip')
    response.headers.set('Content-Type', 'application/zip')
    return response


@app.route('/51cg', methods=['GET', 'POST'])
def cg_decrypt_image():
    url = request.args.get('url')
    if len(url) <= 0:
        return jsonify({"code": "异常", "message": "url参数不能为空"})
    key = request.args.get('key')
    if len(key) <= 0:
        return jsonify({"code": "异常", "message": "key参数不能为空"})
    iv = request.args.get('iv')
    if len(iv) <= 0:
        return jsonify({"code": "异常", "message": "iv参数不能为空"})
    decrypted_bytes = _51cg.decrypt_image(url, key, iv)
    img_io = BytesIO(decrypted_bytes)
    response = make_response(img_io)
    # 设置响应头部信息，指定附件名称
    response.headers.set('Content-Disposition', 'attachment',
                         filename=f'{uuid.uuid4()}.jpg')
    response.headers.set('Content-Type', 'image/jpeg')
    return response


@app.route('/guangbomi', methods=['GET', 'POST'])
def go_guangbomi():
    url = request.args.get('url')
    if len(url) <= 0:
        return jsonify({"code": "异常", "message": "url参数不能为空"})
    m3u8_url = tools.get_m3u8(url)
    return m3u8_url


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


@app.route('/reecho', methods=['GET'])
def go_reecho():
    text = request.args.get('text')
    voiceId = request.args.get('voiceId')
    mode = request.args.get('mode')
    is_None = tools.isEmpty((text, voiceId, mode))
    if is_None:
        return jsonify({"code": "异常", "message": "text、voice、mode参数不能为空"})
    aud_io = BytesIO(reecho.get_reecho(text, voiceId, mode))
    response = make_response(aud_io)
    response.headers.set('Content-Disposition', 'attachment',
                         filename=f'{uuid.uuid4()}.mp3')
    response.headers.set('Content-Type', 'audio/mpeg')
    return response



if __name__ == '__main__':
    app.config["MODULE"] = 'module'
    app.config["TMP"] = 'tmp'
    os.makedirs(app.config["MODULE"], exist_ok=True)
    os.makedirs(app.config["TMP"], exist_ok=True)
    app.run(host="0.0.0.0", port=8000)
