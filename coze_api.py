import requests
import json
from helper import cookie_process
import hashlib
import zlib
from helper import generate_amz_time, generate_local_message_id, uuid_generator, randDID
from aws_signature import AWSsignature


def generate_bogus_signature(cookie, data, headers):
    msToken = cookie_process(cookie, headers)
    url = f"https://complete-mmx-coze-helper.hf.space?msToken={msToken}"
    get_bogus_signature = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"}).json()
    print(get_bogus_signature)
    bogus = get_bogus_signature["data"]["bogus"]
    signature = get_bogus_signature["data"]["signature"]
    return bogus, signature

def image_processing(cookie, image, headers):
    msToken = cookie_process(cookie,headers)
    url = f"https://www.coze.com/api/playground/upload/auth_token?msToken={msToken}"
    data = {"scene":"bot_task"}
    resp = requests.post(url, headers=headers, json=data).json()
    # Get data from response
    try:
        session_token = resp["data"]["auth"]["session_token"]
        access_key = resp["data"]["auth"]["access_key_id"]
        secret_key = resp["data"]["auth"]["secret_access_key"]
        upload_host = resp["data"]["upload_host"]
        service_id = resp["data"]["service_id"]
    except:
        return 'Error'

    if upload_host == "image-upload-us.ciciai.com":
        region = "ap-singapore-1"
    elif upload_host == "image-upload-sg.ciciai.com":
        region = "ap-singapore-1"

    # Initiate image upload
    amzdate = generate_amz_time()
    headers_amz_global = {
        "x-amz-date": amzdate,
        "x-amz-security-token": session_token
    }
    FileSize = str(len(image))
    request_parameters = f'Action=ApplyImageUpload&FileExtension=.png&FileSize={FileSize}&ServiceId={service_id}&Version=2018-08-01'
    signature = AWSsignature(access_key, secret_key, request_parameters, headers_amz_global)

    # Check if signature is correct
    datestamp = amzdate.split('T')[0]
    url = f"https://{upload_host}/?Action=ApplyImageUpload&FileExtension=.png&FileSize={FileSize}&ServiceId={service_id}&Version=2018-08-01"
    headers_amz = headers_amz_global
    headers_amz["Authorization"] = f"AWS4-HMAC-SHA256 Credential={access_key}/{datestamp}/{region}/imagex/aws4_request, SignedHeaders=x-amz-date;x-amz-security-token, Signature={signature}"
    resp = requests.get(url, headers=headers_amz).json()
    # Upload image
    upload_url = 'https://' + resp["Result"]["UploadAddress"]["UploadHosts"][0] + '/upload/v1/' + resp["Result"]["UploadAddress"]["StoreInfos"][0]["StoreUri"]

    headers_amz["Authorization"] = resp["Result"]["UploadAddress"]["StoreInfos"][0]["Auth"]
    headers_amz["Content-Type"] = "application/octet-stream"
    session_key = resp["Result"]["InnerUploadAddress"]["UploadNodes"][0]["SessionKey"]


    # Content-Length
    headers_amz["Content-Length"] = FileSize

    # Content-Crc32
    crc32 = hex(zlib.crc32(image) & 0xffffffff)[2:]
    headers_amz["Content-Crc32"] = crc32

    # Disposition
    headers_amz["Content-Disposition"] = "attachment; filename=\"undefined\""
    resp = requests.post(upload_url, headers=headers_amz, data=image).json()
    data = {"SessionKey": session_key}
    headers_amz_global = {
        "x-amz-content-sha256": hashlib.sha256(json.dumps(data).encode('utf-8')).hexdigest(),
        "x-amz-date": amzdate,
        "x-amz-security-token": session_token
    }

    # Commit image upload
    request_parameters = f'Action=CommitImageUpload&ServiceId={service_id}&Version=2018-08-01' # Alphabetic order
    signature = AWSsignature(access_key, secret_key, request_parameters, headers_amz_global, method="POST", payload=json.dumps(data))
    headers_amz = headers_amz_global
    headers_amz["Authorization"] = f"AWS4-HMAC-SHA256 Credential={access_key}/{datestamp}/{region}/imagex/aws4_request, SignedHeaders=x-amz-content-sha256;x-amz-date;x-amz-security-token, Signature={signature}"

    url_commit = f"https://{upload_host}/?Action=CommitImageUpload&Version=2018-08-01&ServiceId={service_id}"
    resp = requests.post(url_commit, headers=headers_amz, json=data).json()
    return resp


def chat(cookie, question, headers):
    false = False
    true = True

    msToken = cookie_process(cookie, headers)
    print(headers)
    # Get conversation id
    url = f"https://www.coze.com/api/conversation/get_message_list?msToken={msToken}"
    # data = {"cursor":"0","count":15,"bot_id":"7381456780318408722","draft_mode":true,"scene":4}
    data = {"cursor": "0", "count": 15, "bot_id": "7381086531060137992", "draft_mode": false, "scene": 2,
            "biz_kind": "", "insert_history_message_list": []}
    resp = requests.post(url, headers=headers, json=data).json()
    print(resp)
    if '700012014' in str(resp):
        return 'Banned'
    conversation_id = resp["conversation_id"]


    # Clear conversation
    url = f"https://www.coze.com/api/conversation/clear_message?msToken={msToken}"
    data = {"bot_id": "7381086531060137992", "conversation_id": conversation_id, "scene": 2}
    if '700012014' in str(resp):
        return 'Banned'
    resp = requests.post(url, headers=headers, json=data).json()


    # Get conversation id
    url = f"https://www.coze.com/api/conversation/get_message_list?msToken={msToken}"
    data = {"cursor": "0", "count": 15, "bot_id": "7381086531060137992", "draft_mode": false, "scene": 2,
            "biz_kind": "", "insert_history_message_list": []}
    resp = requests.post(url, headers=headers, json=data).json()
    if '700012014' in str(resp):
        return 'Banned'
    conversation_id = resp["conversation_id"]


    # Initiate chat
    uri = str(question["Result"]["Results"][0]["Uri"])
    width = str(question["Result"]["PluginResult"][0]["ImageWidth"])
    height = str(question["Result"]["PluginResult"][0]["ImageHeight"])


    uuid_gen = uuid_generator()
    local_mess_id = generate_local_message_id()
    device_id = randDID()


    data = {"bot_id": "7381086531060137992", "conversation_id": conversation_id, "local_message_id": local_mess_id,
            "content_type": "mix",
            "query": "{\"item_list\":[{\"type\":\"image\",\"image\":{\"key\":\"" + uri + "\",\"image_thumb\":{\"url\":\"blob:https://www.coze.com/" + uuid_gen + "\",\"width\":" + width + ",\"height\":" + height + "},\"image_ori\":{\"url\":\"blob:https://www.coze.com/" + uuid_gen + "\",\"width\":" + width + ",\"height\":" + height + "},\"feedback\":null}},{\"type\":\"text\",\"text\":\"Special requirements:\\n\\nIf it's multiple choice:\\n\\\\begin{ex}…. \\\\choice{}{}{}{} ….\\\\end{ex} \\nDemo multiple choice:\\n\\\\begin{ex}\\nQuestion 1\\n\\\\choice\\n\\t{Answer 1}\\t\\n\\t{Answer 2}\\t\\n\\t{Answer 3}\\t\\n\\t{Answer 4}\\n\\\\end{ex}\\n\\nIf it contains table, do not use \\\\tabular, just take the content\\n\\nConvert:\\n\\\\int into \\\\displaystyle\\\\int\\n\\\\frac{}{} into \\\\dfrac\\n\\\\angle into \\\\widehat{angle_name}\\n\\\\( \\\\) into $ $  (You must contain this for mathematic one) \\\\triangle{triangle_name}\\nUse \\\\backsim if needed\"}]}",
            "extra": {}, "scene": 2, "bot_version": "1718634020343", "draft_mode": false, "stream": true,
            "chat_history": [], "mention_list": [], "device_id": device_id, "space_id": "7338883679957041154"}


    bogus, signature = generate_bogus_signature(cookie, data, headers)
    url = f"https://www.coze.com/api/conversation/chat?msToken={msToken}&X-Bogus={bogus}&_signature={signature}"


    resp = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
    all_content = b""
    for line in resp.iter_lines():
        if line:
            print(line)
            if b'"content":"' and b'"assistant"' and b'"type":"answer"' in line:
                content = line.split(b'"content":"')[1].split(b'","')[0]
                all_content += content
                # print(content.decode('unicode_escape').encode('latin1').decode('utf8'), end="")
            # if b'event:error' in all_content:
            #     return 'Error'
            if b'Out of Daily Quota!' in all_content:
                # Update accounts use to 50
                return 'Quota'
            if b'Coze is temporarily unavailable' in all_content:
                return 'Wait'
    if b'You have exceeded the daily limit for sending messages to the bot. Please try again later.' in all_content:
        return 'Quota'
    if not all_content:
        return 'Error'
    # print('\n')
    all_content = all_content.decode('unicode_escape').encode('latin1').decode('utf8')
    return all_content


def report_ms_token(cookie, headers):
    import logging
    sign_url = "https://complete-mmx-coze-helper.hf.space/report"
    try:
        # Request to get the URL and data for reporting msToken
        msToken = cookie_process(cookie, headers)
        response = requests.get(sign_url)
        sign_response = response.json()
        url = sign_response['data'].get('url')
        sign_response['data'].pop('url', None)

        # Reporting msToken with the received data
        report_response = requests.post(f"{url}/web/report?msToken={msToken}", json=sign_response['data'], headers=headers)

        # Extracting msToken from the cookies
        cookies = report_response.cookies
        msToken = cookies.get('msToken')

        # Set the msToken in the cookies, remove the old one then set the new one
        if msToken:
            old_msToken = headers["Cookie"].split('msToken=')[1].split(';')[0]
            headers["Cookie"] = headers["Cookie"].replace(old_msToken, msToken)


        if not msToken:
            raise Exception("msToken not found in cookies")

        logging.info("msToken refreshed successfully: %s", msToken)
        return msToken, headers, headers["Cookie"]

    except Exception as e:
        logging.error("Failed to report msToken: %s", str(e))
        return None