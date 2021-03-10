import os

docPath = "../dataset/"

# method: 
# 0. whole images
# 1. slide windows
def build_dataset(method):
    data = []
    label = []
    images = read_raw_cmds_data()
    for image in images:
        if method == 0:
            words = ""
            for command in images[image]:
                words = words + " " + clean_data(command)
            data.append(words)
            label.append(image)
        elif method == 1:
            windows = 3
            try:
                for i in range(len(images[image]) - windows):
                    command = images[image]
                    words = ""
                    for j in range(windows):
                        words =  words + " " + clean_data(command[i + j])

                    if len(words.strip()) == 0:
                        continue
                
                    data.append(words)
                    label.append(image)
            except:
                words = ""
                for i in range(len(images[image])):
                    command = images[image]
                    words =  words + " " + clean_data(command[i]) 

                if len(words.strip()) == 0:
                    continue
                
                data.append(words)
                label.append(image)


    return data, label


# TODO: it is a test version
def clean_data(words_list):
    doc = ""

    # pass parametes
    for word in words_list:
        if "apt-get" == word or "apt" == word or "install" == word or "yum" == word or "git" == word:
            continue
            
        if not word.startswith("-") and len(word) < 15:
            try:
                tmp = int(word)
            except:
                doc = doc + " " + word
    
    return doc

# read commands' words
def read_raw_cmds_data():
    paths = []
    files = os.walk(docPath)  
    for path, dirs, files in files:  
        for file in files:
            if "word" not in file:
                continue
            paths.append(os.path.join(path, file))

    images = {}
    for path in paths:
        with open(path, "r") as log:
            lines = log.readlines()
            for info in lines:
                info = info.strip()
                try:
                    image = info.split("; ", 1)[0]
                    cmds = []
                    # commands
                    for items in info.split("; ", 1)[1].strip("[]").split("], ["):
                        cmd = []
                        # words and paras
                        for item in items.split(", "):
                            cmd.append(item.strip("'"))
                        cmds.append(cmd)
                    images[image] = cmds
                except:
                    continue

    return images

#print(len(read_data()))

