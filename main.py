from configparser import ConfigParser
import time
config = ConfigParser()
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

while True:
    try:
        link = fetchMainJs()
        queryId, bearer = fetchQueryIdBearer(link)
        url = 'https://api.twitter.com/graphql/'+queryId+'/UserByScreenName?variables=%7B%22screen_name%22%3A%22'+id+'%22%2C%22withSafetyModeUserFields%22%3Atrue%7D&features=%7B%22hidden_profile_likes_enabled%22%3Atrue%2C%22hidden_profile_subscriptions_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22subscriptions_verification_info_is_identity_verified_enabled%22%3Atrue%2C%22subscriptions_verification_info_verified_since_enabled%22%3Atrue%2C%22highlights_tweets_tab_ui_enabled%22%3Atrue%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%7D&fieldToggles=%7B%22withAuxiliaryUserLabels%22%3Afalse%7D'
        headers = {
            'X-Guest-Token':config['token']['guest'],
            'Authorization':"Bearer "+bearer
        }
        response = requests.get(url,headers=headers)
        if response.status_code == '200':
            data = response.json()
            print(data)
            time.sleep(10)
        else:
            print(response.text)
            time.sleep(10)
    except:
        print('exception')
        time.sleep(10)
# your bearer token never expires, but has very low rate limit.
# so you have to set X-Guest-Token, to let twitter know that you are not logged in, and not affected by rate limit. (maybe?)
# Unfortunately, X-Guest-Token is not hard-coded, so you have to catch valid guest token on twitter
# how? it is written on js code -> .withEndpoint(lt.Z).requestGuestToken()['catch']
# how do we implement this? let me think about it...