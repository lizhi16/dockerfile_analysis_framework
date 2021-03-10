import os
import sys
import parser

docPath = "./dataset/"

def read_raw_dockerfile_data():
    words_dict = {}
    with open(docPath + sys.argv[1], "r") as log:
        for line in log.readlines():
            image = line.split(";", 1)[0]
            dockerfile = line.split("; ", 1)[1].strip('b').strip("\'").replace("\\n", "\n")
            
            try:
                words = parser.dockerfile2bash(dockerfile)
                if len(words) != 0:
                    words_dict[image] = words
                else:
                    print (image)
            except:
                print (image)
                continue

    with open(docPath + sys.argv[1] + "-words.list", "w+") as log:
        for image in words_dict:
            log.write(image + "-marked; " + str(words_dict[image]) + "\n")

    return words_dict

read_raw_dockerfile_data()
#print(len(read_data()))

