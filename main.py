from configparser import ConfigParser
import time
import json
config = ConfigParser()
#todo: args로 받아오게 만들기
config.read('conf.ini')


id = config['victim']['id']

import requests, re

# fetch main.js
# if null is returned, raise exception on main loop 
def fetchMainJs():
    url = 'https://twitter.com/'+id+'/main.js' 
    response = requests.get(url)
    if response.status_code == 200:
        js_content = response.text
        pattern = r'src="(https://abs.twimg.com/responsive-web/client-web-legacy/main.[^"]+)"'
        match = re.search(pattern, js_content)
        if match:
            link = match.group(1)
            return link
        else:
            print("couldn't fetch main.js")
    else:
        print(f"Failed to retrieve the JavaScript file. Status code: {response.status_code}")
    
# 위에서 얻은 정보로 config 채우기
# fetch queryId, bearer token
def fetchQueryIdBearer(link):
    url=link
    response = requests.get(url)
    if response.status_code==200:
        js_content = response.text
        f = open('a.txt','w')
        f.write(js_content)
        f.close()
        pattern = r'queryId:"([A-Za-z0-9-]+)",operationName:"UserByScreenName"'
        pattern2 = r'{return"Bearer ([A-Za-z0-9\-!@#$%^&*()]+)";}'
        match = re.search(pattern, js_content)
        match2 = re.search(pattern2, js_content)
        if match:
            queryId = match.group(1)
            print(queryId)
            if match2:
                bearer = match2.group(1)
                print(bearer)
                return queryId, bearer
            else:
                print("couldn't fetch bearer")
        else:
            print("couldn't fetch queryId")

def fetchGuest(id):
    url = 'https://twitter.com/'+id
    response = requests.get(url)
    if response.status_code == 200:
        js_content=response.text
        pattern = r'document\.cookie="gt=(\d+);'
        match = re.search(pattern,js_content)
        if match:
            guest = match.group(1)
            print(guest)
            return guest
        else:
            print("couldn't fetch guest")

while True:
    try:
        link = fetchMainJs()
        queryId, bearer = fetchQueryIdBearer(link)
        guest = fetchGuest(id) #뭔가 이렇게 세번부르는게 최선인가? 최적화할수있을거같은데 잘뒤지면
        base_url = 'https://api.twitter.com/graphql/' + queryId + '/UserByScreenName'
        variables = {
            "screen_name": id,
            "withSafetyModeUserFields": True
        }
        features = {
            "hidden_profile_likes_enabled": True,
            "hidden_profile_subscriptions_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "subscriptions_verification_info_is_identity_verified_enabled": True,
            "subscriptions_verification_info_verified_since_enabled": True,
            "highlights_tweets_tab_ui_enabled": True,
            "responsive_web_twitter_article_notes_tab_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True
        } #이게 자주 바뀌는 것 같다
        field_toggles = {
            "withAuxiliaryUserLabels": False
        }

        #variables, featrues, fieldToggles 동적으로 가져와야 함!! 

        payload = {
            "variables": json.dumps(variables),
            "features": json.dumps(features),
            "fieldToggles": json.dumps(field_toggles)
        }
        headers = {
            'X-Guest-Token':guest,
            'Authorization':"Bearer "+bearer
        }
        response = requests.get(base_url,params=payload,headers=headers)
        if response.status_code == '200':
            data = response.json()
            print(data)
            time.sleep(10)
        else:
            print(response.text)
            time.sleep(10)
    except Exception as e:
        print('exception'+str(e))
        time.sleep(10)
# your bearer token never expires, but has very low rate limit.
# so you have to set X-Guest-Token, to let twitter know that you are not logged in, and not affected by rate limit. (maybe?)
# Unfortunately, X-Guest-Token is not hard-coded, so you have to catch valid guest token on twitter
# how? it is written on js code -> .withEndpoint(lt.Z).requestGuestToken()['catch']
# how do we implement this? let me think about it...

# html에서 document.cookie = "gt=17294.... 에도 있고, 리퀘스트를 두번보냈을때 쿠키를 뒤져도 나온다!
# Max-Age=9000 이니까 고려해서 보낼것