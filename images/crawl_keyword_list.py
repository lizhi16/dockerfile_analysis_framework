from treelib import Tree, Node
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as Expect

options = Options()
options.headless = True
browser = webdriver.Firefox(options=options)
keywordsFile = "./keyWordList.txt"

wordDict = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '_'
]

dictTree = Tree()
root = Node(data="")
dictTree.add_node(root)
parents = []

def init_tree():
    for firstWord in wordDict:
        node1layer = Node(data=firstWord)
        dictTree.add_node(node1layer, parent = root)
        parents.append(node1layer)

        for secWord in wordDict:
            node2layer = Node(data=secWord)
            dictTree.add_node(node2layer, parent = node1layer)

def add_leaf_node(root):
    for word in wordDict:
        node = Node(data=word)
        dictTree.add_node(node, parent = root)

def cut_accepted_leaves(leaves):
    global parents
    
    flag = 1
    for node in dictTree.leaves():
        if node not in leaves or node in parents:
            dictTree.remove_node(node.identifier)
            flag = 0

    if flag == 0:
        cut_accepted_leaves(leaves)

def traversal_paths_to_leaf():
    # flag is used to judge whether end recursive
    flag = 1
    leaves = dictTree.leaves()
    for path in dictTree.paths_to_leaves():
        keyWord = ""
        for node in path:
            keyWord = keyWord + dictTree[node].data

        leaf = dictTree[path[-1]]
        # Judging whether this keyword can be used to search in docker hub
        status = check_keyword_search_results(keyWord)
        if status == 1:
            dictTree.remove_node(leaf.identifier)
            cut_accepted_leaves(leaves)
            with open(keywordsFile, 'a+') as keyword_list:
                 keyword_list.write(keyWord + "\n")
            #keywordList.append(keyWord)
        # no results
        elif status == -2:
            dictTree.remove_node(leaf.identifier)
            cut_accepted_leaves(leaves)
        # If it can't, add a new character behind this keyword
        elif status == -1:
            return
        else:
            add_leaf_node(leaf)
            flag = 0

    if flag == 0:
        traversal_paths_to_leaf()

def check_number(number):
    num = str(number).split(',')
    # num over 1,000,000
    if len(num) > 2:
        return 0
    # num less 1,000
    elif len(num) == 1:
        return 1

    try:
        imageNum = int(num[0]) * 1000 + int(num[1])
        if imageNum < 2500:
            return 1
    except Exception as e:
        return 0

    return 0

def check_keyword_search_results(keyWord):
    # root node is ""
    if keyWord == "":
        return -1

    print ("Check the Keywords:", keyWord)

    url = "https://hub.docker.com/search?q={}&type=image".format(keyWord)
    for i in range(5):
        try:
            browser.get(url)
            break
        except Exception as e:
            print ("retry...")
            continue
            pass

    element = Wait(browser, 10).until(
        Expect.presence_of_element_located((By.ID, "searchResults"))
    )

    if 'no results' in element.text:
        print ("There doesn't have search results...")
        #return 0
        return -2

    soup = BeautifulSoup(browser.page_source,'html.parser')
    links = soup.find_all('div',class_="styles__currentSearch___35kW_")
    for link in links:
        if "-" in link.div.text and "of" in link.div.text:
            num = link.div.text.split()[4]
            imageNum = check_number(num)
            return imageNum
    return 0

def main():
    init_tree()
    traversal_paths_to_leaf()
    browser.quit()

if __name__ == '__main__':
    main()
