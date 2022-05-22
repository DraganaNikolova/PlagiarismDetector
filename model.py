class detectPlagiarism:
    """A class containing all needed function for determing if a document is plagiat"""
    
    def __init__(self, document):
        # list of features describing a document
        self.document = document
        # features for the existing documents
        df = pd.read_pickle('dataset_v2.pkl')
    
    # 30% importance links
    
    def checkLinks(self):
        """Function finding same links in the existing documents.
           If the same number of documents it's larger than 50%
           the compared documents are returned with a percentage of same links"""
        dict = {}
        for index, row in df.iterrows():
            common = 0
            for link in list(dict.fromkeys(list(self.document['links'])[0])):
                if link in row['links']:
                    common = common + 1
                    
            try:
                if common >= len(list(dict.fromkeys(list(row['links']))))/2:
                    dict[row['filePath']] = 30*(100*float(common)/float(len(list(dict.fromkeys(list(row['links']))))))/100
            except: pass
        return dict
    
    # 30% importance metadata
    
    def skipByOneChar(self, first, second, n):
        """Returning the imbalance of two strings"""
        imbalance = 0
        a = 0
        b = 0
        i = 0
        while (i < n and imbalance <= 1):
            if (first[a] == second[b]):
                #  When both string character at position a and b is same
                a += 1
                b += 1
            else :
                a += 1
                imbalance += 1
            i += 1

        if (imbalance == 0):
            #  In case, last character is extra in first string
            return 1
        return imbalance

    def differBySingleChar(self, first, second):
        """Function that checks if two strings only differ by a single character"""
        #  Get the size of given string 
        n = len(first)
        m = len(second)
        imbalance = 0
        if (n == m):
            i = 0
            #  Case A when both string are equal size
            while (i < n and imbalance <= 1):
                if (first[i] != second[i]):
                    imbalance += 1
                i += 1

        elif (n - m == 1 or m - n == 1):
            #  When one string contains extra character
            if (n > m) :
                imbalance = self.skipByOneChar(first, second, m)
            else :
                imbalance = self.skipByOneChar(second, first, n)

        if (imbalance == 1):
            return True
        else: return False
    
    def has_latin(self, text):
        """Function that checks if string contains latin letters"""
        return bool(re.match('[A-Za-z]', text))

    def to_cyrillic(self, text):
        """Function that converts latin to cyrillic"""
        from transliterate import translit
        return translit(text, "mk")

    def check_author(self):
        """Function that checks if a document's names author, name of the student and the 
           name of the person who made the last modification are the same"""
        score = 0
        
        # Latin to cyrillic
        author = self.to_cyrillic(list(self.document['author'])[0]).lower()
        nameStudent = self.to_cyrillic(list(self.document['nameStudent'])[0]).lower()
        lastModified = self.to_cyrillic(list(self.document['last_modified_by'])[0]).lower()

        # There is no equal pair -> biggest difference
        if author != nameStudent and author != lastModified and nameStudent != lastModified:
            score = 1

        # 1 pair is not equal -> mild
        if (author == nameStudent and author == lastModified and nameStudent != lastModified) or (author != nameStudent and author == lastModified and nameStudent == lastModified) or (author == nameStudent and author != lastModified and nameStudent == lastModified) or (author != nameStudent and author != lastModified and nameStudent == lastModified) or (author == nameStudent and author != lastModified and nameStudent != lastModified) or (author != nameStudent and author == lastModified and nameStudent != lastModified):
            score = 0.5

        # each name is equal
        if author == nameStudent == lastModified:
            score = 0

        # pass if the surname is same in each
        first = nameStudent.split(' ')[0]
        second = nameStudent.split(' ')[1]
        if (first in author and first in lastModified) or (second in author and second in lastModified):
            score = 0
        elif (first in author or first in lastModified) or (second in author or second in lastModified):
            score = 0.5
        try:
            # check if two string are different by a single character ("Динишев", "Динисев")
            if self.differBySingleChar(first, author.split(' ')[0]) is True or self.differBySingleChar(first, author.split(' ')[1]) is True or self.differBySingleChar(second, author.split(' ')[0]) is True or self.differBySingleChar(second, author.split(' ')[1]) is True or self.differBySingleChar(first, lastModified.split(' ')[0]) is True or self.differBySingleChar(first, lastModified.split(' ')[1]) is True or self.differBySingleChar(second, lastModified.split(' ')[0]) is True or self.differBySingleChar(second, lastModified.split(' ')[1]) is True:
                score = 0
        except: 
            pass
        return score
    
    def checkTime(self):
        """Function that checks if a document's created and modified dates have a small distance.
           Small distance is considered to be below 1 hour"""
        from datetime import datetime
        created = list(self.document['created'])[0]
        modified = list(self.document['modified'])[0]
        
        duration = created - modified
        duration_in_h = duration.total_seconds()/60/60

        if duration_in_h > 1:
            return 0
        else: return 1
     
    def checkRevisions(self):
        """Function that checks the number of revision.
           If a document doesn't have revisions, it is considered to have a
           percentage of plagiarism"""
        revision = list(self.document['revision'])[0]
        
        if revision > 1:
            return 0
        else: return 1    
    
    def checkMetadata(self):
        author = self.check_author()
        time = self.checkTime()
        revisions = self.checkRevisions()
        
        return (author + time + revisions)*10
    
    # 30% importance text
    
    def make_n_grams(self, n, text):
        """Function that makes n grams from text"""
        import nltk
        from nltk.util import ngrams

        result = []
        ngrams_result = ngrams(sequence=nltk.word_tokenize(text), n=n)
        for ngram in ngrams_result:
            result.append(ngram)
        return result

    def compare(self, ngrams1, ngrams2):
        """Function that finds same ngrams between two texts"""
        common=[]
        if len(ngrams1) > len(ngrams2):
            main = ngrams1
            second = ngrams2
        else: 
            main = ngrams2
            second = ngrams1

        for gram in main:
            if gram in second:
                common.append(gram)
        try: return 30*(100*float(len(common))/float(len(ngrams2)))/100
        except: return 0

    def checkText(self, n):
        """Function that compares the ngrams for the document to the ngrams of the existing documents"""
        import pandas as pd

        ngramsDocument = self.make_n_grams(n, list(self.document['text'])[0])

        dict = {}
        for index, row in df.iterrows():
            ngrams_result = self.make_n_grams(n, row['text'])
            comparison_result = self.compare(ngramsDocument, ngrams_result)
            if comparison_result != 0:
                dict[row['filePath']] = comparison_result

        return dict
        
    # 10% similarity in text based on a context
    
    def calculate_similarity(self, second_document):
        """Function that calculates the text similarity between two documents"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as np

        corpus = []
        corpus.append(list(self.document['text'])[0])
        corpus.append(second_document)
        _stopwords = {'a', 'а', 'ако', 'ама', 'ах', 'ај', 'ајде', 'бе', 'беа', 'без', 'беше', 'би', 'биде', 'бил', 'било', 'в', 'веќе', 'ви', 'вие', 'во', 'воопшто', 'вратата', 'врз', 'ги', 'го', 'да', 'дали', 'два', 'две', 'дека', 'до', 'добро', 'додека', 'друг', 'други', 'друго', 'дури', 'е', 'еден', 'една', 'еднаш', 'едно', 'еј', 'за', 'зад', 'зарем', 'зашто', 'знам', 'зошто', 'и', 'или', 'им', 'има', 'имаше', 'исто', 'итн', 'каде', 'како', 'кај', 'кога', 'кое', 'кои', 'колку', 'кон', 'кој', 'која', 'ли', 'малку', 'ме', 'мене', 'ми', 'миг', 'многу', 'може', 'можеби', 'можел', 'можеше', 'мора', 'мошне', 'му', 'на', 'навистина', 'над', 'нас', 'не', 'неа', 'него', 'неговата', 'неговите', 'неговото', 'неколку', 'некој', 'некоја', 'нема', 'немаше', 'нешто', 'ни', 'нив', 'нивните', 'ние', 'низ', 'никогаш', 'никој', 'ниту', 'ништо', 'но', 'нѐ', 'ова', 'оваа', 'овде', 'овој', 'од', 'оди', 'одма', 'околу', 'она', 'оние', 'ох', 'па', 'пак', 'по', 'повеќе', 'повторно', 'под', 'покрај', 'полека', 'понекогаш', 'после', 'потоа', 'пред', 'преку', 'при', 'рече', 'сè', 'само', 'своите', 'својата', 'својот', 'се', 'себе', 'сега', 'секогаш', 'секој', 'сето', 'сеуште', 'си', 'сите', 'сме', 'со', 'сосема', 'сте', 'сум', 'сѐ', 'таа', 'така', 'таму', 'те', 'ти', 'тие', 'тоа', 'тогаш', 'токму', 'толку', 'тој', 'треба', 'тука', 'туку', 'уште', 'што', 'ја', 'јас', 'ќе'}

        vect = TfidfVectorizer(min_df=1, stop_words=_stopwords)  
        tfidf = vect.fit_transform(corpus)                                                                                                                                                                                                                       
        pairwise_similarity = tfidf * tfidf.T

        return pairwise_similarity.toarray()[0][1]
    
    def checkTextSimilarity(self):
        """Function that compares the ngrams for the document to the ngrams of the existing documents"""
        import pandas as pd

        dict = {}
        for index, row in df.iterrows():
            text_partner = row['text']
            
            similarity = self.calculate_similarity(text_partner)
            
            # Multiple by 10 because the similarity can be max 10 and the text similarity is 10% of whole plagiarism
            dict[row['filePath']] = similarity * 10 

        return dict
    
    # main function
    def calculatePlagiarism(self, n):
        """Function that returns dictionary for each document that contains simillarity based
           on the passed document. The values in the dictionary are percentage of plagiarism"""
        
        links = self.checkLinks() # returns dictionary
        metaData = self.checkMetadata() # returns percentage
        text = self.checkText(n) # returns dictionary
        similarityText = self.checkTextSimilarity()
        
        plagiarism = {} # result dictionary
        
        for key in links:
            summary = links[key] + metaData + similarityText[key]
            plagiarism[key] = summary
                
        for key in text:
            linkValue = 0
            try: linkValue = links[key]
            except: pass
            
            if text[key] + linkValue == 60:
                summary = 100
            else: summary = text[key] + linkValue + metaData + similarityText[key]
            
            plagiarism[key] = summary  
            
        return plagiarism

    