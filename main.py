# Crawling dockerhub for all Dockerfile, and checking this Dockerfile whether has malicious behaviors
import sys
import threading

import crawl
import parse2cmds

class detecting_thread(threading.Thread):
    def __init__(self,image):
        threading.Thread.__init__(self)
        
        # image read from file contains "\n"
        self.image = image.strip()

    def run(self):
        dockerfile = crawl.resolve_images_info(self.image)
        sourceEntry = trace_entry_images(dockerfile)
        

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
