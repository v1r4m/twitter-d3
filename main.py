import time
import json
import requests, re
import argparse
import subprocess


def notify(title, message):
    script = f'display notification "{message}" with title "{title}" sound name "Glass"'
    subprocess.run(['osascript', '-e', script], check=False)

class Twitter:
# fetch main.js
# if null is returned, raise exception on main loop 
    def fetchMainJs(self,id):
        url = 'https://twitter.com/'+id
        headers ={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            js_content = response.text
            pattern = r'src="(https://abs.twimg.com/responsive-web/client-web/main.[^"]+)"'
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
            pattern = r'queryId:"([A-Za-z0-9-]+)",operationName:"UserByScreenName",operationType:"query",metadata:\{featureSwitches:(\[.*?\]),fieldToggles:(\[.*?\])\}'
            pattern2 = r'"Bearer ([A-Za-z0-9\-!@#$%^&*()]+)"'
            match = re.search(pattern, js_content)
            match2 = re.search(pattern2, js_content)
            if match:
                queryId = match.group(1)
                featureSwitches = json.loads(match.group(2))
                fieldToggles = json.loads(match.group(3))
                if match2:
                    bearer = match2.group(1)
                    return queryId, bearer, featureSwitches, fieldToggles
                else:
                    print("couldn't fetch bearer")
            else:
                print("couldn't fetch queryId")

    def fetchGuest(self,id):
        url = 'https://twitter.com/'+id
        headers ={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            js_content=response.text
            f = open('a.txt','w')
            f.write(js_content)
            f.close()
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
            print(link)
            queryId, bearer, featureSwitches, fieldToggles = self.fetchQueryIdBearer(link)
            guest = self.fetchGuest(id)
            base_url = 'https://api.twitter.com/graphql/' + queryId + '/UserByScreenName'
            variables = {
                "screen_name": id,
                "withSafetyModeUserFields": True
            }
            features = {name: True for name in featureSwitches}
            field_toggles = {name: True for name in fieldToggles}
            payload = {
                "variables": json.dumps(variables),
                "features": json.dumps(features),
                "fieldToggles": json.dumps(field_toggles)
            }
            headers = {
                'X-Guest-Token': guest,
                'Authorization': "Bearer " + bearer,
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'x-twitter-active-user': 'yes',
                'x-twitter-client-language': 'en',
                'Referer': 'https://twitter.com/',
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
                    if upTweet > 0:
                        notify(f'@{id}', f'New tweet (+{upTweet})')
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

