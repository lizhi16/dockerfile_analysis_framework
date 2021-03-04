import dataset
from sklearn import feature_extraction  
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorize

#vectorizer=CountVectorizer()
# n_features: dimension of vector
#vectorizerH = HashingVectorizer(n_features = 6, norm = None) 
def judge(corpus):
# https://blog.csdn.net/Eastmount/article/details/50473675
    
    vectorizer = CountVectorizer()

    transformer = TfidfTransformer()
 
    tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))
 
    word = vectorizer.get_feature_names()

    weight = tfidf.toarray()

    print ('Start Kmeans:')
    from sklearn.cluster import KMeans
    clf = KMeans(n_clusters=20)
    s = clf.fit(weight)
    print s
 
    print(clf.cluster_centers_)
    
    print(clf.labels_)
    i = 1
    while i <= len(clf.labels_):
        print i, clf.labels_[i-1]
        i = i + 1
 
    print(clf.inertia_)

data, label = dataset.build_dataset()
judge(data)