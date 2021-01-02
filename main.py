# Crawling dockerhub for all Dockerfile, and checking this Dockerfile whether has malicious behaviors
import sys
import threading

import crawl
import parse2cmds

# using for debug
failed_resolve = []

class detecting_thread(threading.Thread):
    def __init__(self,image):
        threading.Thread.__init__(self)
        
        # image read from file contains "\n"
        self.image = image.strip()

    def run(self):
        # get dockerfile from dockerhub
        dockerfile = crawl.resolve_images_info(self.image)
        if dockerfile == None:
            return
        #print (dockerfile)

        # resolve the dockerfile
        #dockerfile = parse2cmds.parse_dockerfile(dockerfile)
        try:
            dockerfile = parse2cmds.parse_dockerfile(dockerfile)
        except:
            failed_resolve.append(self.image)
            print ("[ERR] Dockerfile resolve failed: ", self.image)
            return

        sourceEntry = parse2cmds.trace_entry_images(dockerfile)

        # save the analysis results
        with open("./results/images.csv", "a+") as log:
            for item in sourceEntry:
                log.write(self.image + ", " + item + ", ")
                for obj in sourceEntry[item]:
                    log.write(obj.replace("\n", " "))
                log.write("\n")

def main():
    images = open(sys.argv[1], "r").readlines()
    index = 1
    total = len(images)

    cores = 16
    analyze_thread = []

    for image in images:
        # check format
        if "/" not in image:
            continue
        
        # output the rate of processing
        index = index + 1
        if index % 100 == 0:
            print ("Completing: [" + str(index) + "/" + str(total) + "]")

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

if __name__ == '__main__':
    main()

    # using for debug
    with open("./results/failed_resolve.list", "a+") as log:
        for item in failed_resolve:
            log.write(item + "\n")
