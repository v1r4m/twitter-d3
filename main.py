import time
import json
import requests, re
import argparse

class Twitter:
# fetch main.js
# if null is returned, raise exception on main loop 
    def fetchMainJs(self,id):
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
    def fetchQueryIdBearer(self,link):
        url=link
        response = requests.get(url)
        if response.status_code==200:
            js_content = response.text
            f = open('a.txt','w')
            f.write(js_content)
            f.close()
            pattern = r'queryId:"([A-Za-z0-9-]+)",operationName:"UserByScreenName",operationType:"query",metadata:{featureSwitches:(\[.*?\])'
            pattern2 = r'{return"Bearer ([A-Za-z0-9\-!@#$%^&*()]+)";}'
            match = re.search(pattern, js_content)
            match2 = re.search(pattern2, js_content)
            if match:
                queryId = match.group(1)
                featureSwitches = match.group(2)
                #print(queryId)
                if match2:
                    bearer = match2.group(1)
                    #print(bearer)
                    return queryId, bearer, featureSwitches
                else:
                    print("couldn't fetch bearer")
            else:
                print("couldn't fetch queryId")

    def fetchGuest(self,id):
        url = 'https://twitter.com/'+id
        response = requests.get(url)
        if response.status_code == 200:
            js_content=response.text
            pattern = r'document\.cookie="gt=(\d+);'
            match = re.search(pattern,js_content)
            if match:
                guest = match.group(1)
                #print(guest)
                return guest
            else:
                print("couldn't fetch guest")

    def finalApi(self,id):
        try:
            link = self.fetchMainJs(id)
            queryId, bearer, featureSwitches = self.fetchQueryIdBearer(link)
            guest = self.fetchGuest(id) #뭔가 이렇게 세번부르는게 최선인가? 최적화할수있을거같은데 잘뒤지면
            base_url = 'https://api.twitter.com/graphql/' + queryId + '/UserByScreenName'
            #true/false 가져오는 방법을 모르겠어서 일단은 featureSwitches는 이대로...

            #metadata:{
            # featureSwitches:[
            # "hidden_profile_likes_enabled",
            # "hidden_profile_subscriptions_enabled",
            # "responsive_web_graphql_exclude_directive_enabled",
            # "verified_phone_label_enabled",
            # "subscriptions_verification_info_is_identity_verified_enabled",
            # "subscriptions_verification_info_verified_since_enabled",
            # "highlights_tweets_tab_ui_enabled",
            # "responsive_web_twitter_article_notes_tab_enabled",
            # "creator_subscriptions_tweet_preview_api_enabled",
            # "responsive_web_graphql_skip_user_profile_image_extensions_enabled",
            # "responsive_web_graphql_timeline_navigation_enabled"],
            # 
            # fieldToggles:["withAuxiliaryUserLabels"]}}
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

            #variables, featrues, fieldToggles 동적으로 가져와야 할수도 있음
            # (t/f어디서 가져오는지 생각해보기, 혹시 all true로 보내도 정상출력되는지 테스트해보기)

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
            return response
        except Exception as e:
            print('exception'+str(e))
            return
    def mainloop(self,id,interval):
        response = self.finalApi(id)
        data = response.json()
        prevTweet = data['data']['user']['result']['legacy']['statuses_count']
        prevMedia = data['data']['user']['result']['legacy']['media_count']
        prevFav = data['data']['user']['result']['legacy']['favourites_count']
        print('Total Tweet :', prevTweet)
        print('Total Media :',prevMedia)
        print('Total Fav(Likes) :', prevFav)
        time.sleep(interval)
        while True:
            try:
                response = self.finalApi(id)
                if response.status_code == 200: #'200'으로 하면 안됨 ㅡㅡ 
                    data = response.json()
                    totalTweet = data['data']['user']['result']['legacy']['statuses_count']
                    #######################
                    #TODO: RT한 트윗이 계폭하거나, 삭제되면 트윗수가 어떻게 변하는지 실험해봐야됨
                    #만약 변화가 있다면 (-)마이너스 변화는 무시하고 (+)플러스 변화만 로깅해야함
                    #######################
                    totalMedia = data['data']['user']['result']['legacy']['media_count']
                    totalFav = data['data']['user']['result']['legacy']['favourites_count']
                    #print(totalTweet,totalMedia,totalFav) #트윗,미디어,하트
                    upTweet = totalTweet-prevTweet
                    upMedia = totalMedia-prevMedia
                    upFav = totalFav-prevFav
                    print()
                    print('Total Tweet : '+str(totalTweet)+' (+'+str(upTweet)+' in last '+str(interval)+'s)')
                    print('Total Media : '+str(totalMedia)+' (+'+str(upMedia)+' in last '+str(interval)+'s)')
                    print('Total Fav(Likes) : ', str(totalFav)+' (+'+str(upFav)+' in last '+str(interval)+'s)')
                    #변화량을 3가지 그래프 축으로 그려야됨
                    #Tweet과 Media는 같이올라가는걸 고려해야함!! 
                    #그렸다치고
                    prevTweet = totalTweet
                    prevMedia = totalMedia
                    prevFav = totalFav
                    time.sleep(interval)
                else:
                    print(response.text)
                    time.sleep(10)
            except Exception as e:
                print('exception'+str(e))
                time.sleep(10)
    def __init__(self):
        pass
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='your twitter private account stalker. see more info: https://github.com/v1r4m/twitter-d3')
    parser.add_argument('twitter_id', help='Twitter id(without @)')
    parser.add_argument('-set_interval', '-s', default=60, type=int, help='polling interval(default: 60(seconds))')

    args = parser.parse_args()

    twitter = Twitter()
    twitter.mainloop(id=args.twitter_id, interval=args.set_interval)


# your bearer token never expires, but has very low rate limit.
# so you have to set X-Guest-Token, to let twitter know that you are not logged in, and not affected by rate limit. (maybe?)
# Unfortunately, X-Guest-Token is not hard-coded, so you have to catch valid guest token on twitter

# html에서 document.cookie = "gt=17294.... 에도 있고, 리퀘스트를 두번보냈을때 쿠키를 뒤져도 나온다!
# Max-Age=9000 이니까 고려해서 보낼것

