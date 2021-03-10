import dataset
import codecs
import numpy as np
from sklearn import feature_extraction  
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import Birch
from sklearn.cluster import DBSCAN

#vectorizer=CountVectorizer()
# n_features: dimension of vector
#vectorizerH = HashingVectorizer(n_features = 6, norm = None) 

class Cluster(object):
    def __init__(self, corpus, label):
        vectorizer = CountVectorizer()
        
        transformer = TfidfTransformer()
        
        tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))
        
        self.word = vectorizer.get_feature_names()
        
        self.weight = tfidf.toarray()

        self.labels = label

    def tfidf_info(self):
        print ('Features length: ' + str(len(self.word)))
        
        resName = "BHTfidf_Result.txt"
        result = codecs.open(resName, 'w', 'utf-8')
        for j in range(len(self.word)):
            result.write(self.word[j] + ' ')
        result.write('\r\n\r\n')
            
        for i in range(len(self.weight)):
            for j in range(len(self.word)):
                result.write(str(self.weight[i][j]) + ' ')
            result.write('\r\n\r\n')
 
        result.close()
        
    def kmeans(self):
        print ('Start Kmeans:')
        from sklearn.cluster import KMeans
        # 500 is the number of clusters
        clf = KMeans(n_clusters = 500)
        s = clf.fit(self.weight)
 
        print(clf.cluster_centers_)
    
        print(clf.labels_)
        i = 1
        with open("./class_dockerfile.csv", "w+") as log:
            while i <= len(clf.labels_):
                log.write(str(i) + ", " + str(label[i-1]) + ", " + str(clf.labels_[i-1]) + " \n")
                print (i, label[i-1], clf.labels_[i-1])
                i = i + 1
                
        print(clf.inertia_)

    def birch_cluster(self):
        print ('Start cluster Birch:')
        self.cluster = Birch(threshold = 0.05, n_clusters = None)
        self.cluster.fit_predict(self.weight)

        cluster_dict = {}
        for index,value in enumerate(self.cluster.labels_):
            index = self.labels[index]
            if value not in cluster_dict:
                cluster_dict[value] = [index]
            else:
                cluster_dict[value].append(index)
        
        with open("birch_class_dockerfile.csv", "w+") as log:
            log.write("class, imageName\n")
            for item in cluster_dict:
                duplicate = []
                for image in cluster_dict[item]:
                    if image in duplicate:
                        continue
                    duplicate.append(image)
                    log.write(str(item) + ", " + str(image) + "\n")

    def dbscan(self):
        # https://blog.csdn.net/cindy_1102/article/details/95316841
        DBS_clf = DBSCAN(eps=1, min_samples=4)
        DBS_clf.fit(self.weight)

        labels = DBS_clf.labels_
        original_corpus = self.labels
        assert len(labels) == len(original_corpus)
        max_label = max(labels)
        number_label = [i for i in range(0, max_label + 1, 1)]
        number_label.append(-1)
        result = [[] for i in range(len(number_label))]
        for i in range(len(labels)):
            index = number_label.index(labels[i])
            result[index].append(original_corpus[i])

        print (result)


data, label = dataset.build_dataset(1)
cluster = Cluster(data, label)
cluster.birch_cluster()