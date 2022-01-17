import requests, os

auth_url = "https://ullu.app/ulluCore/oauth/token"
img_url = "https://ullu2-files.ullu.app"
media_url = "https://ullu.app/ulluCore/api/ullu2/media/fetchAllMediaSlider/cdiOpn?familySafe=no&platform=ANDROID_APK"
content_url = "https://ullu.app/ulluCore/api/ullu2/media/getMediaByTitleYearSlugAndFamilySafe/cdiOpn?familySafe=no&titleYearSlug="
episode_data_url = "https://ullu.app/ulluCore/api/ullu2/media/isAllowedW/cdiOpn"

# write your mail and password here before using
EMAIL = ""
PASSWORD = ""
def get_medias():
    mids, titles, slugs, thumbnails = [], [], [], []
    response = requests.get(media_url).json()
    for i in response:
        mids.append(i["mediaId"])
        titles.append(i["title"])
        slugs.append(i["titleYearSlug"])
        thumbnails.append(img_url+i["landscapePosterId"])
    return mids, titles, slugs, thumbnails

def get_contents(slug):
    response = requests.get(content_url + slug).json()
    seasons_data = response['seasons_']
    id_container, titles_container = {}, {}
    for sidx, season_data in enumerate(seasons_data):
        for eidx, episode_data in enumerate(season_data['episodes_']):
            try: id_container[sidx][eidx]
            except KeyError:
                if id_container=={}:
                    id_container[sidx]={}
                    titles_container[sidx]={}
                try: id_container[sidx][eidx]
                except KeyError:
                    id_container[sidx][eidx]=[]
                    titles_container[sidx][eidx] = []
            id_container[sidx][eidx].append(
                episode_data['mainContent']['id'])
            titles_container[sidx][eidx].append(
                episode_data['mainContent']['contentMetaData']['title'])
    return titles_container, id_container
    
def get_access_token():
    data = f"grant_type=password&scope=read%20write&username={EMAIL}&password={PASSWORD}&client_id=consumerWeb&client_secret=consumerWeb%40123"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
    }
    response = requests.post(auth_url,headers=headers, data=data).json()
    token = f'{str(response["token_type"]).capitalize()} {str(response["access_token"])}'
    return token

def get_episode_data(content_id, media_id, auth_token):
    headers = {
        "content-type": "application/json",
        "authorization": auth_token,
    }
    data = f'{{"contentId":"{content_id}","mediaId":"{media_id}","platform":"ANDROID_APK","userRole":"CONSUMER"}}'
    response = requests.post(episode_data_url, headers=headers, data=data).json()
    auth_cookie = f"cookie: G_ENABLED_IDPS=google; G_AUTHUSER_H=0; CloudFront-Key-Pair-Id={response['cookieKeyPairId']}; CloudFront-Signature={response['cookieSignature']}; CloudFront-Policy={response['cookiePolicy']}"
    return response["fileURL"], auth_cookie

def play(cid, mid, title):
    token = get_access_token()
    a=get_episode_data(cid, mid, token)
    os.system(f"ffplay -window_title '{title}' -headers '{a[1]}' {a[0]}")

def main():
    mids, titles, slugs, _ = get_medias()
    for i,j in enumerate(titles):
        print(f"{i+1}. {j}")
    show_idx = int(input("Enter show index: "))-1
    mid = mids[show_idx]
    titles, cids = get_contents(slugs[show_idx])
    for i, _ in enumerate(titles):
        print(f"{i+1}. season-{i+1}")
    season_idx = int(input("Select season: "))-1
    for i, j in enumerate(titles[season_idx]):
        print(f"{i+1}. {titles[season_idx][j][0]}")
    episode_idx = int(input("Select episode: "))-1
    cid = cids[season_idx][episode_idx][0]
    title = titles[season_idx][episode_idx][0]
    play(cid, mid, title)

if __name__ == '__main__':
    main()
    
