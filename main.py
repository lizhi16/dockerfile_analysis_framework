# Crawling dockerhub for all Dockerfile, and checking this Dockerfile whether has malicious behaviors
import sys
import threading
import crawler

# using for debug
failed_resolve = []
results = {}

class detecting_thread(threading.Thread):
    def __init__(self, image):
        threading.Thread.__init__(self)
        # image read from file contains "\n"
        self.image = image.strip()

    def run(self):
        dockerfile = crawler.resolve_images_info(self.image)
        if dockerfile == None or dockerfile == "":
            print ("[ERR] not dockerfile", self.image)
            return
            
        results[self.image] = dockerfile

def main():
    global results
    images = open(sys.argv[1], "r").readlines()
    index = 1
    total = len(images)

    cores = 16
    analyze_thread = []

    for image in images:
        # check format
        if "/" not in image and not image.startswith("/"):
            continue
        
        # output the rate of processing
        index = index + 1
        if index % 1000 == 0:
            print ("Completing: [" + str(index) + "/" + str(total) + "]")
            write_log()
            results = {}

        thread = detecting_thread(image)
        # keep the threads < cores numbers
        if len(threading.enumerate()) <= cores:
            thread.start()
            analyze_thread.append(thread)
        else:
            for t in analyze_thread:
                t.join()

            thread.start()
            analyze_thread.append(thread)

    for t in analyze_thread:
        t.join()
    
    write_log()
    
def write_log():
    global results
    try:
        prefix = sys.argv[1].split("/")[2]
    except:
        prefix = "-1"

    with open("./results/words-" + prefix + ".list", "a+") as log:
        for item in results:
            try:
                itemText = u' '.join(results[item]).encode("utf-8").strip()
                log.write(str(item) + "; " + itemText + "\n")
            except:
                log.write(str(item) + "; " + "\n")


if __name__ == '__main__':
    main()
