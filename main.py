# Crawling dockerhub for all Dockerfile, and checking this Dockerfile whether has malicious behaviors
import sys
import threading

from dockerfile_analysis import cmd2words
import parse2cmds

# using for debug
failed_resolve = []
results = {}

class detecting_thread(threading.Thread):
    def __init__(self, image):
        threading.Thread.__init__(self)
        
        # image read from file contains "\n"
        self.image = image.strip()

    def run(self):
        commands = parse2cmds.dockerfile2cmds(self.image)
        if "RUN" not in commands:
            return
        
        words = cmd2words.docker_bash_parser(commands)
        if len(words) == 0:
            return

        results[self.image] = words

def main():
    global results
    images = open(sys.argv[1], "r").readlines()
    index = 1
    total = len(images)

    cores = 8
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

            if index % 1000 == 0:
                log()
                results = {}

            thread.start()
            analyze_thread.append(thread)

    for t in analyze_thread:
        t.join()
    
    log()

def log():
    try:
        prefix = sys.argv[1].split("/")[2]
    except:
        prefix = "-1"

    with open("./results/words-" + prefix + ".list", "a+") as log:
        for item in results:
            log.write(str(item) + "; " + str(results[item]) + "\n")

if __name__ == '__main__':
    main()
