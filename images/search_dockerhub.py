import sys
import time
import threading
import requests

def get_images_url(keyword, url):
    if url == "":
        return ""

    # payload={}
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Content-Type': 'application/json',
        'Search-Version': 'v3',
        'Accept': 'application/json',
        'X-DOCKER-API-CLIENT': 'docker-hub/1280.0.0',
        'sec-ch-ua-platform': '"macOS"',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://hub.docker.com/search?q={}&type=image'.format(keyword),
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }

    # response = requests.request("GET", url, headers=headers, data=payload)

    try:
        content = requests.get(url, headers = headers)
        while content.status_code == 429:
            print ("[WARN] wait for 429!")
            time.sleep(60)
            content = requests.get(url, headers=headers)

        if content.status_code == 200:
            return content
        else:
            return ""
    except Exception as e:
        print ("why 429 !!!!!!!!!!!!!", e)
        return ""

class resolve_images_thread(threading.Thread):
    def __init__(self, keyword):
        threading.Thread.__init__(self)
        self.keyword = keyword.strip()
        self.images = {}

    def run(self):
        self.resolve_images_list()

    def resolve_images_list(self):
        url = "https://hub.docker.com/api/content/v1/products/search?page_size=100&q={}&type=image".format(self.keyword)
        while url != "":
            content = get_images_url(self.keyword, url)
            if content == "":
                break 
            
            content = content.json()
            url = content["next"]

            for images in content["summaries"]:
                try:
                    image = str(images["name"])
                    created = str(images["created_at"])
                    updated = str(images["updated_at"])

                    if image not in self.images:
                        self.images[image] = image + ", " + created + ", " + updated
                except:
                    continue

    def get_results(self):
        return self.images

def main():
    cores = 16
    keywords = {}
    with open(sys.argv[1], "r") as log:
        for line in log.readlines():
            line = line.strip()
            if line not in keywords:
                keywords[line] = 1

    crawl_thread = []
    index = 0
    total = str(len(keywords))
    for keyword in keywords:
        index += 1
        print("[" + str(index) + "/" + total + "] " + keyword)

        thread = resolve_images_thread(keyword)
        # keep the threads < cores numbers
        if len(threading.enumerate()) <= cores:
            thread.start()
            crawl_thread.append(thread)
        else:
            for t in crawl_thread:
                if not t.isAlive():
                    continue
                
                t.join()
                imgs = t.get_results()
                save_data(imgs)
                break

            thread.start()
            crawl_thread.append(thread)

    for t in crawl_thread:
        if not t.isAlive():
            continue
        
        t.join()
        imgs = t.get_results()
        save_data(imgs)

def save_data(images):
    with open("./results/all_images.list", "a+") as log:
        for img in images:
            log.write(images[img] + "\n")

if __name__ == "__main__":
    main()
