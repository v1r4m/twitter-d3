from configparser import ConfigParser
config = ConfigParser()
config.read('conf.ini')

id = config['victim']['id']

import requests, re

url = 'https://twitter.com/'+id+'/main.js' 
response = requests.get(url)
if response.status_code == 200:
    js_content = response.text
    pattern = r'src="(https://abs.twimg.com/responsive-web/client-web-legacy/main.[^"]+)"'
    match = re.search(pattern, js_content)
    if match:
        link = match.group(1)
        print(link)
    else:
        print("couldn't fetch main.js")
else:
    print(f"Failed to retrieve the JavaScript file. Status code: {response.status_code}")
    
# 위에서 얻은 정보로 config 채우기

url = 'https://api.twitter.com/graphql/'+config['token']['url']+'/UserByScreenName?variables=%7B%22screen_name%22%3A%22'+id+'%22%2C%22withSafetyModeUserFields%22%3Atrue%7D&features=%7B%22hidden_profile_likes_enabled%22%3Atrue%2C%22hidden_profile_subscriptions_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22subscriptions_verification_info_is_identity_verified_enabled%22%3Atrue%2C%22subscriptions_verification_info_verified_since_enabled%22%3Atrue%2C%22highlights_tweets_tab_ui_enabled%22%3Atrue%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%7D&fieldToggles=%7B%22withAuxiliaryUserLabels%22%3Afalse%7D'
headers = {
    'X-Guests-Token':config['token']['guest'],
    'Authrization':config.get('token', 'bearer', raw=True)
}

response = requests.get(url,headers=headers)
data = response.json()
print(data)