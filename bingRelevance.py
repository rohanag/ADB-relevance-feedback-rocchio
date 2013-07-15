#Porter stemmer taken from http://tartarus.org/martin/PorterStemmer/python.txt
#List of stop words taken from http://www.lextek.com/manuals/onix/stopwords2.html
from __future__ import division
import urllib2
import urllib
import base64
import json
import sys
import math
import re
import porter as port   #for Stemming

#posWeight() Returns positional weight for a word, proportional to its distance
#from the nearst query term in the document
#For Example, for a query "woods", and a document "tiger woods plays golf", the positional weight for golf = 3/2,
#positional weight for tiger = 3/1. So closer terms get bigger weights.
def posWeight(i,searchString,words):
    slist = searchString.split()
    #Taken an arbitrary large value in Matches, Matches stores the index of search terms where found in words
    matches = [10000]
    for s in slist:
        matches += [ii for ii,x in enumerate(words) if x==s.lower()]
    #store min distance from any search term from i
    dist = sorted([math.fabs(x-i) for x in matches])[0]
    if dist == 0:
        return 3
    else:
        return dist

#getweight() Returns weights, given the word and url/doc
def getweight(word,url):
    p = port.PorterStemmer()
    stemmedword = p.stem(word, 0,len(word)-1)
    if url not in invl[word]:
        return 0
    tf = invl[word][url] #term frequency
    tf2 = 0

    #Example:
    #If the query has 'fruits',but the document has 'fruit' in it,we would want that 'fruits' should get the term frequency of                      #itself(if it is present) plus the term frequency of 'fruit' ideally,so that 'fruits' has some weight,else its weight will                      #be zero and that doc will not be retrieved
    if stemmedword in invl and stemmedword != word and stemmedword not in stopwords:
        if url in invl[stemmedword]:
            tf2 = invl[stemmedword][url] #term frequency for stemmed word

    df=len(invl[word]) #document frequency
    tfidf=(tf+tf2)*math.log(10.0/df) #TF-IDF weight is the TermFrequency of the word times the Inverse Document Frequency
    return tfidf

#Printing transcript
f=open('Transcript.txt','w')

#Extracting Command-Line Arguements
if len(sys.argv)==4:
    searchstring=sys.argv[3]
    precision=float(sys.argv[2])
    key=sys.argv[1]
else:
    print "Argument Missing/Extra.Program terminating...."
    exit()

#Storing the list of all stop words
stopwords = [line.strip() for line in open('stopwords.txt')]
stopwords = set(stopwords)

pre = 0.0
roun=0
#Till we do not reach the target precision,execute this loop
while pre < precision:
    roun+=1
    f.write("==================================================\n")
    f.write("Round: "+str(roun)+"\n")
    query=urllib2.quote(searchstring)  #URL Encoding the Query

    #Extracting web results from Bing using Bing Search API-Web Results only
    bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Web?Query=%27'+query+'%27&$top=10&$format=json'
    accountKey = str(key)
    accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
    headers = {'Authorization': 'Basic ' + accountKeyEnc}
    req = urllib2.Request(bingUrl, headers = headers)
    response = urllib2.urlopen(req)
    content = response.read()
    result=json.loads(content)  #The extracted content is in JSON format.It needs to be converted into a nested dictionary type
    print "Parameters:\n"
    print "Client Key: "+accountKey
    print "Query: "+searchstring
    f.write("Query: "+searchstring+"\n")
    print "Precision: "+str(precision)
    f.write("Desired Precision: "+str(precision)+"\n")
    print "URL: "+bingUrl
    print "Total number of Results: "+str(len(result['d']['results']))
    if len(result['d']['results']) < 10:
        print 'Less than 10 results, terminating program.......'
        exit()
    print "\nBing Search Results:"
    print "==========================="

    r={} #To store relevant documents
    nr={} #To store non relevant documents
    invl={} #Inverted index
    wordlist=[] #list of total words in all the 10 web results,as returned by Bing
    vector={} #For creating vectors based on the Vector-Model theory
    counter=1
    relevance=0

    #Displaying all results to the user and simultaneously processing them to create the inverted index
    for i in result['d']['results']:
        words=[]
        print "Result "+str(counter)
        f.write("Result "+str(counter)+"\n")
        print "["
        f.write("["+"\n")
        print " URL "+i['Url']
        f.write("URL "+i['Url']+"\n")
        print " Title "+i['Title'].encode('utf-8')
        f.write("Title "+i['Title'].encode('utf-8')+"\n")
        print " Summary: "+i['Description'].encode('utf-8')
        f.write("Summary "+i['Description'].encode('utf-8')+"\n")
        print "]"
        f.write("]"+"\n")
        counter+=1

        #Tokenizing text and lowecasing
        #words=words+re.split(r"\s|(?<!\d)[,.](?!\d)",i['Title'])
        words=words+re.split("\s|(?<!\d)[^\w']+|[^\w']+(?!\d)", i['Title'])
        #words=words+re.split(r"\s|(?<!\d)[,.](?!\d)",i['Description'])
        words=words+re.split("\s|(?<!\d)[^\w']+|[^\w']+(?!\d)", i['Description'])
        words = [x.lower() for x in words]
        words = filter(None, words)

        #Building inverted index as a dictionary of a dictionary
        #invl={
        #       <term1>:
        #               {
        #               <Doc1/URL1>:<tf>,
        #               <Doc2/URL2>:<tf>,
        #               ...........
        #               }
        #       <term2>:
        #               {
        #               <Doc6/URL6>:<tf>,
        #               .............
        #               }
        #       ..........
        #       }

        for wi,w in enumerate(words):
            poswt = 3.0/posWeight(wi,searchstring,words)
            if w in invl:
                if i['Url'] in invl[w]:
                    invl[w][i['Url']]+= 1*poswt
                else:
                    invl[w][i['Url']]= 1*poswt
            else:
                invl[w]={i['Url']: 1*poswt}
        wordlist=wordlist+words

        #Beginning to take user relevance feedback
        while 1:
            feedback=raw_input("\nRelevant (Y/N)?")
            if feedback=='Y' or feedback =='y':
                relevance+=1
                r[i['Url']]=[i['Title'],i['Description']]
                f.write("Relevant: YES\n\n")
                break
            elif feedback=='N' or feedback=='n':
                #For Ide dec hi algorithm,we need to store only the top ranked non relevant document,instead of storing                                 #all of them.Hence only if the collection of non relevant docs in empty,we append an item to it(which will                                      #be the top ranked)
                if len(nr) == 0:
                    nr[i['Url']]=[i['Title'],i['Description']]
                f.write("Relevant: NO\n\n")
                break
            else:
                print "Please enter Y/y or N/n only!"
                continue

    #Inserting query in inverted index,just to make it easier for calculating its vector representation
    for w in re.split(r"[^\w']+",searchstring):
        if w in invl:
            if 'Query' in invl[w]:
                invl[w]['Query']+=1
            else:
                invl[w]['Query']=1
        else:
            invl[w]={'Query':1}




    #Creating vector representations for each document returned by Bing,and the Query
    wordlist=sorted(set(wordlist))
    for u in result['d']['results']:
        vector[u['Url']]=[0]*len(wordlist)  #Initializing the vector of each doc by zero,dimension equal to total words in corpus
        for i,word in enumerate(wordlist):
            vector[u['Url']][i]=getweight(word,u['Url'])
    vector['Query']=[0]*len(wordlist)  #Initializing the vector for the Query
    for i,word in enumerate(wordlist):
        vector['Query'][i]=getweight(word,'Query')

    pre=relevance/10.0
    if relevance == 0:
        print 'Below desired precision but can no longer augment the query. Consider pressing the Y key sometimes too'
        exit()
    print "======================"
    print "FEEDBACK SUMMARY"
    print "Query "+searchstring
    print "Precision "+str(pre)
    if pre>=precision:
        print "Desired precison reached, done"
        exit()

##------------------------------------------------

##              rocchio parameters
##        alpha=1
##        beta=0.75
##        gamma=0.25

##                ide dec hi parameters
    alpha=1
    beta=1
    gamma=1

    #IDE DEC HI ALGORITHM
    new_query=[0]*len(wordlist)  #Initializing the vector for the modified/new query
    new_query=[ x+alpha*y for x,y in zip(new_query,vector['Query']) ]
    for k in list(r.viewkeys()):
        #new_query = [x + (beta*y/len(r)) for x,y in zip(new_query,vector[k] )]  normalization in rocchio algo
        new_query = [x + (beta*y) for x,y in zip(new_query,vector[k] )]
    for k in list(nr.viewkeys()):
        #new_query = [x - (gamma*y/len(nr)) for x,y in zip(new_query,vector[k] )] normalization done for rocchio
        new_query = [x - (gamma*y) for x,y in zip(new_query,vector[k] )]

    #Modifying Query
    count = 0


    #Run till the new words to be added to the old query become 2 in number
    while count < 2:
        wordtoadd = wordlist[new_query.index(max(new_query))]  #Extracting the word with maximum weight from the new query

        #If the word to be added to old query,as calculated, is not already in the Query,and moreover if it is not a stop word
        #only then add it to form the new query
        p1 = port.PorterStemmer()
        stemmed = p1.stem(wordtoadd, 0,len(wordtoadd)-1)
        if wordtoadd not in searchstring.lower() and wordtoadd not in stopwords and stemmed not in searchstring.lower():
            count += 1
            searchstring += ' ' + wordlist[new_query.index(max(new_query))]
            wordlist.remove(wordlist[new_query.index(max(new_query))])  #Removed from corpus,so that it's not considered again
            new_query.remove(max(new_query))
        else:
            wordlist.remove(wordlist[new_query.index(max(new_query))])
            new_query.remove(max(new_query))

    print "Modified Search String: " + searchstring
    f.write("Modified Search String: " + searchstring+"\n")
