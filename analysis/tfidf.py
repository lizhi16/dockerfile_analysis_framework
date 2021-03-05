import dataset
import codecs
from sklearn import feature_extraction  
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer

#vectorizer=CountVectorizer()
# n_features: dimension of vector
#vectorizerH = HashingVectorizer(n_features = 6, norm = None) 
def judge(corpus, label):
# https://blog.csdn.net/Eastmount/article/details/50473675
    
    vectorizer = CountVectorizer()

    transformer = TfidfTransformer()
 
    tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))
 
    word = vectorizer.get_feature_names()

    weight = tfidf.toarray()

    print ('Features length: ' + str(len(word)))
    resName = "BHTfidf_Result.txt"
    result = codecs.open(resName, 'w', 'utf-8')
    for j in range(len(word)):
        result.write(word[j] + ' ')
    result.write('\r\n\r\n')
   
    for i in range(len(weight)):
        for j in range(len(word)):
            #print weight[i][j],
            result.write(str(weight[i][j]) + ' ')
        result.write('\r\n\r\n')
 
    result.close()

    print ('Start Kmeans:')
    from sklearn.cluster import KMeans
    clf = KMeans(n_clusters = 500)
    s = clf.fit(weight)
 
    print(clf.cluster_centers_)
    
    print(clf.labels_)
    i = 1
    with open("./class_dockerfile.csv", "w+") as log:
        while i <= len(clf.labels_):
            log.write(str(i) + ", " + str(label[i-1]) + ", " + str(clf.labels_[i-1]) + " \n")
            print (i, label[i-1], clf.labels_[i-1])
            i = i + 1
 
    print(clf.inertia_)

data, label = dataset.build_dataset()
judge(data, label)