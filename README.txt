Rohan Agrawal, UNI: ra2616
Digvijay Singh, UNI: ds3161

List of Files:-----------------------------------------------------------------------

bingRelevance.py
stopwords.txt
porter.py
run.sh
Transcript_bill.txt
Transcript_gates.txt
Transcript_snowleopard.txt

How to Run:--------------------------------------------------------------------------

1.Go to the directory ds3161-proj1 and type: 
python bingRelevance.py <Account-Key> <Precision> <query>

2.Alternatively,you can run the program through our makefile 'run.sh' in the following way:
chmod +x run.sh
./run.sh <Account-key> <Precision> <query>

******There seemed to be a problem in the display/formatting of our output,when the code is run (2).However everything is perfect when run via (1).We could not comprehend the problem.So it is preferable if you run the code using (1) **********

Internal Design:---------------------------------------------------------------------

Outline of the Design: We have used Term Frequency and Inverse Document Frequency to create an Inverted Index. Weights are calculated using tf-idf and positional data (nearness of terms from query terms). New query terms are calculated through the Ide-Dec Hi algorithm.

1. The search results given back by the Bing API are first tokenized. The tokens are then put into an inverted index. We have used the python dictionary data structure for making an inverted index. The design of the inverted index is as follows: Dictionary[word][URL] = Term Frequency + Positional Weight 

While calculating the Term Frequency used in weight calculation, we have used the Porter stemmer (taken from [4]) to calculate term frequencies of root words as well. For example, while calculating the weight value of 'fruits' we have added the term frequency of 'fruit' as well to the result. 

We have added a positional Weight for each term in the index.  Positional Weight is equal to 3.0/(Minimum Distance of Term in a Document from a Query term). For Example, for a query "woods", and a document "tiger woods plays golf", the positional weight for golf = 3/2, positional weight for tiger = 3/1. So closer terms get bigger weights.

2. After the user marks relevant / non relevant documents, the relevant documents are put into a set, and the highest ranked non relevant document's URL is stored (The highest non-relevant document vector is used in the Ide-Dec Hi algorithm).

3. Then for calculating an updated query vector based on user relevance feedback, we have used the Ide-Dec hi model, which is a slight variant of the Rocchio algorithm for query relevance.

4. We show results returned by the bing API, and again ask for relevance / non relevance from user as in Step 2. We repeat steps 1 - 4 until expected precision is reached.

Description of Query-Modification Method---------------------------------------------

The Ide Dec Hi Algorithm calculates an updated query weight vector as follows: 

Add the weight vector of the original query, and the Weight vectors of the relevant documents marked by the user. From this weight vector, subtract the weight vector of the highest ranked non relevant document. This new vector is the updated query vector.

After forming the updated query vector, we take the 2 highest weights from the updated query vector, and add the corresponding terms to the query (provided the terms are not already present in the original query, even in stemmed form). We also stop 'stop words' from being added to the new query (List of Stop words by Salton and Buckley is taken from [5])

For the Ide-Dec Hi algorithm, The weights alpha, beta, gamma are all equal to 1, according to [2].

Bing Search Key:---------------------------------------------------------------------

Digvijay qhoA3ZNi3uIxUpjHcHBedrnxJ9O2LQ1QyzWJ2+Bmddg=
Rohan 	tfXfeYcUCuEk1sgdW/1vUCRnKx5FTqg9eBwCO05Skvc=

References:--------------------------------------------------------------------------

1. Christopher D. Manning, Prabhakar Raghavan, Hinrich Schütze: An Introduction to Information Retrieval, 2009

2. Gerard Salton, Chris Buckley: Improving Retrieval Performance by Relevance Feedback, 1990

3. Amit Singhal, Modern Information Retreival: A Brief Overview, 2001

4. Porter Stemmer in Python, http://tartarus.org/martin/PorterStemmer/python.txt

5. Stop Words used by Salton and Buckley for SMART,
   http://www.lextek.com/manuals/onix/stopwords2.html
