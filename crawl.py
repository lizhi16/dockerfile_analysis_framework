# Crawling dockerhub for all Dockerfile
import requests

def resolve_images_info(image):
    # get Dockerfile in dockerhub
    Dockerfile = resolve_Dockerfile_from_dockerhub(image)
    if Dockerfile != "":
        #print ("dockerfile:", Dockerfile)
        return Dockerfile

    # get Dockerfile in github
    user = image.split('/')[0]
    imageName = image.split('/')[1]

    githubRepo = check_github_repo(user, imageName)
    if githubRepo != "":
        url = "https://raw.githubusercontent.com" + githubRepo + "/Dockerfile"
        #print (url)
        Dockerfile = resolve_Dockerfile_from_github(url)
        if Dockerfile != "":
            #print ("github:", Dockerfile)
            return Dockerfile

    # get build history in dockerhub
    tagsHistory = check_tags(image)
    if tagsHistory:
        for item in tagsHistory:
            return tagsHistory[item]

    return None


def get_url(url):
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
            return ""
    except:
        return ""

def check_tags(image):
    # the build history to the tags
    tagsHistory = {}

    # crawl the images tags
    url = 'https://hub.docker.com/v2/repositories/{}/tags/'.format(str(image))
    content = get_url(url)
    if content == "":
        return tagsHistory
    content = content.json()

    try:
        tags = content["results"]
        if len(tags) == 0:
            return tagsHistory

        for tag in tags:
            # get image's tags
            tagName = tag["name"]

            # get build history of each tag, "history" is a list []
            history = resolve_tags_to_imageHistory(image, tag["name"])
            if history != "":
                tagsHistory[tagName] = history
        
        return tagsHistory
    
    except Exception as e:
        return tagsHistory

# Getting the Dockerfile from "tags" page.
def resolve_tags_to_imageHistory(image, tag):
    # content of build history
    imageHistory = ""

    url = 'https://hub.docker.com/v2/repositories/{}/tags/{}/images'.format(str(image),str(tag))
    content = get_url(url)
    if content == "":
        return imageHistory
    content = content.json()

    try:
        # [0] is needed, also only one result
        for commands in content[0]["layers"]:
            if "set -ex" in commands["instruction"] or "set -eux" in commands["instruction"] or "exit 101" in commands["instruction"]:
                continue
            if "ENTRYPOINT" not in commands["instruction"] and "CMD" not in commands["instruction"]:
                imageHistory = imageHistory + "\n" + commands["instruction"].strip().replace("/bin/sh -c", "RUN").replace(" in ", " ").replace("]", "").replace("[", "")
            else:
                imageHistory = imageHistory + "\n" + commands["instruction"].strip().replace(" in ", " ").replace("\" \"", " ")
        return imageHistory
    
    except Exception as e:
        return imageHistory

def check_github_repo(user, imageName):
    # github address
    githubRepo = ""

    url = 'https://hub.docker.com/api/audit/v1/build/?include_related=true&offset=0&limit=50&object=%2Fapi%2Frepo%2Fv1%2Frepository%2F{}%2F{}%2F'.format(str(user),str(imageName))
    content = get_url(url)
    if content == "":
        return githubRepo
    content = content.json()

    try:
        if content["meta"]["total_count"] != 0:
            for object in content["objects"]:
                commit = object["commit"]
                if "source_repo" in object:
                    githubRepo = object["source_repo"] + "/" + commit
                    break
        
        return githubRepo
    
    except Exception as e:
        return githubRepo

def resolve_Dockerfile_from_github(url):
    # image's Dockerfile
    Dockerfile = ""
    Dockerfile = get_url(url)
    
    return Dockerfile

def resolve_Dockerfile_from_dockerhub(image):
    # image's Dockerfile
    Dockerfile = ""

    url = 'https://hub.docker.com/v2/repositories/{}/dockerfile/'.format(str(image))
    content = get_url(url)
    if content == "":
        return Dockerfile
    content = content.json()

    try:
        if content["contents"] != "":
            Dockerfile = content["contents"]
    except Exception as e:
        return Dockerfile

    return Dockerfile