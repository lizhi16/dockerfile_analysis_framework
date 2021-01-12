import json
import requests

#registryBase='https://registry-1.docker.io'
#authBase='https://auth.docker.io'
#authService='registry.docker.io'

def get_url(url, headers):
    if headers == "":
        headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    } 

    try:
        content = requests.get(url, headers=headers)
        while content.status_code == 429:
            time.sleep(60)
            content = requests.get(url,headers=headers)

        if content.status_code == 200:
            return content
        else:
            print (content.status_code)
            return ""
    except:
        return ""

# get token to access the registry 
def auth_repo_token(image):
	url= "https://auth.docker.io/token?service=registry.docker.io&scope=repository:{}:pull".format(str(image))
	
	content = get_url(url, "")
	try:
		token = content.json()["token"]
		return token
	except:
		return ""

# get images' manifest
def get_image_manifest(image, tag):
    if "/" not in image:
        image = "library/" + image

    # get token
    token = auth_repo_token(image)
    if token == "":
        print ("[ERR] Token get failed...")
        return 
    
    # get the manifest
    headers = {
        'Authorization': f"Bearer {token}",
        'Accept': 'application/vnd.docker.distribution.manifest.v2+json',
    }

    url = "https://registry-1.docker.io/v2/{}/manifests/{}".format(str(image), str(tag))
    content = get_url(url, headers)

    if content != "":
        return content.json()
    else:
        return None

# function1: url in layers
def judge_url_layers(image, tag):
    urls = []
    # get manifest
    manifest = get_image_manifest(image, tag)

    # error situations
    if manifest == None:
        return False
    elif "layers" not in manifest:
        return False

    for item in manifest['layers']:
        if "urls" in item:
            urls.append(item["urls"])

    return urls



