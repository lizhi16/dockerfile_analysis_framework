import crawl
import download
import parse2cmds

basePath = "./results/"
"""
judge if urls indicate a images's layers
"""
def identify_urls_layers(image):
    urls = []

    tags = crawl.resolve_tags(image)
    if len(tags) == 0:
        return False

    for tag in tags:
        url = download.judge_url_layers(image, tag)
        urls = urls + url

    #return urls
    with open(basePath + "urls_layers.csv", "a+") as log:
        for url in urls:
            log.write(image + ", " + str(url) + "\n")

    return True


"""
trace the keywords in dockerfile
"""
def trace_keywords(image):
    # get dockerfile from dockerhub
    dockerfile = crawl.resolve_images_info(image)
    if dockerfile == None or dockerfile == "":
        return

    # resolve the dockerfile
    #dockerfile = parse2cmds.parse_dockerfile(dockerfile)
    try:
        dockerfile = parse2cmds.parse_dockerfile(dockerfile)
    except:
        failed_resolve.append(image)
        #print ("[ERR] Dockerfile resolve failed: ", self.image)
        return

    # trace the source of the scripts
    sourceEntry = parse2cmds.trace_entry_images(dockerfile)
    write_log(image, sourceEntry, "images")

    # identify the keywords
    keywords = ["base64 "]
    identify = parse2cmds.identify_keywords(dockerfile, keywords)
    write_log(image, identify, "keywords")

# log the detection results
def write_log(image, results, filename):
    path = "./results/" + filename + ".csv"
    with open(path, "a+") as log:
        for item in results:
            log.write(image + ", " + item + ", ")
            for obj in results[item]:
                log.write(obj.replace("\n", " "))
            log.write("\n") 