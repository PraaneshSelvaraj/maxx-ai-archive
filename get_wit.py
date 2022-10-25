from wit import Wit

def get_intent(res):
    try:
        intent_raw= res['intents'][0]['name']
        confidence =res['intents'][0]['confidence']
        print(str(intent_raw) + " " +str(confidence))
        if(confidence >= 0.8):
            intent = intent_raw
        else: intent=None
    except:
        intent=None
    
    return intent

def get_res(message_text, access_token):
    try:
        client = Wit(access_token)
        res = client.message(message_text)
    except:
        res=None
    return res

def get_search(res):
    try:
        return res['entities']['search:search'][0]['value']
    except:
        return None

def get_service(res):
    try:
        a=res['entities']['service:service'][0]['value']
        return a.strip()
    except:
        return None

def get_service_type(res):
    try:
        return res['entities']['service_type:service_type'][0]['value']
    except:
        return None

def get_playlist(res):
    try:
        return res['entities']['playlist:playlist'][0]['value'].strip()
    except:
        return None

def get_alarm_time(res):
    try:
        b=res['entities']['wit$datetime:datetime'][0]['value']
        print(b)
        d,t = b.split("T")
        time, _ = t.split(".")
        hour , min, sec =time.split(":")
        return d, hour, min, sec
    except:
        return None

def get_data_time(res):
    try:
        return res['entities']['wit$datetime:datetime'][0]['value']
    except:
        return None

def get_map_places(res):
    try:
        return res['entities']['map_places:map_places'][0]['value'].strip()
    except:
        return None

def get_network_device(res):
    try:
        return res['entities']['network_device:network_device'][0]['value']
    except:
        return None

def get_accent(res):
    try:
        return res['entities']['accent:accent'][0]['value']
    except:
        return None

def get_speak(res):
    try:
        return res['entities']['speak:speak'][0]['value']
    except:
        return None