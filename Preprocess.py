from imports import *

def load_data():
  data=pd.read_csv('data/Text summarization data.csv')
  return(data)


def count_frequency(list):
  frequency={}
  for element in list:
    if element in frequency:
      frequency[element]+=1
    else:
      frequency[element]=1
  return(frequency)
  
def word_tokenizer(text, tokenizer, n_gram, keep_ponctuation):
  lemmatizer= WordNetLemmatizer()
  stemmer= PorterStemmer()
  stop_words=stopwords.words('english')
  sentences=sentence_tokenizer(text)[0]
  if tokenizer=='word':
    tokens=[]
    ngram_tokens=[]
    if (n_gram>1):
      for sentence in sentences:
        if keep_ponctuation==False:
          sentence = re.sub('[^a-zA-Z]+', ' ', sentence) #remove numbers
          sentence = re.sub(r'[^\w\s]', '', sentence) #remove ponc
          tokens_to_add=[token for token in word_tokenize(sentence) if ((not token in stop_words) & (len(token)>2))]
          ngram_tokens += [' '.join(item) for item in list(ngrams(tokens_to_add,n_gram)) ]
      return (ngram_tokens)
  
    else:
      for sentence in sentences:
        if keep_ponctuation==False:
          sentence = re.sub('[^a-zA-Z]+', ' ', sentence) #remove numbers
          sentence = re.sub(r'[^\w\s]', '', sentence) #remove ponc
          tokens_to_add=[token for token in word_tokenize(sentence) if ((not token in stop_words) & (len(token)>2))]
          tokens+= tokens_to_add
      return(tokens)
      
          
  if tokenizer=='lemma':
    lemma=[]
    ngram_lemma=[]
    if (n_gram>1):
      for sentence in sentences:
        if keep_ponctuation==False:
          sentence = re.sub('[^a-zA-Z]+', ' ', sentence) #remove numbers
          sentence = re.sub(r'[^\w\s]', '', sentence) #remove ponc
          lemma_to_add=[lemmatizer.lemmatize(token) for token in word_tokenize(sentence) if not lemmatizer.lemmatize(token) in stop_words]
          ngram_lemma += [' '.join(item) for item in list(ngrams(lemma_to_add,n_gram)) ]
      return (ngram_lemma)
  
    else:
      for sentence in sentences:
        if keep_ponctuation==False:
          sentence = re.sub('[^a-zA-Z]+', ' ', sentence) #remove numbers
          sentence = re.sub(r'[^\w\s]', '', sentence) #remove ponc
          lemma_to_add=[lemmatizer.lemmatize(token) for token in word_tokenize(sentence) if not lemmatizer.lemmatize(token) in stop_words]
          lemma+= lemma_to_add
      return(lemma)
  
  if tokenizer=='stem':
    stems=[]
    ngram_stems=[]
    if (n_gram>1):
      for sentence in sentences:
        if keep_ponctuation==False:
          sentence = re.sub('[^a-zA-Z]+', ' ', sentence) #remove numbers
          sentence = re.sub(r'[^\w\s]', '', sentence) #remove ponc
          stems_to_add=[stemmer.stem(token) for token in word_tokenize(sentence) if not stemmer.stem(token) in stop_words]
          ngram_stems += [' '.join(item) for item in list(ngrams(stems_to_add,n_gram)) ]
      return (ngram_stems)
  
    else:
      for sentence in sentences:
        if keep_ponctuation==False:
          sentence = re.sub('[^a-zA-Z]+', ' ', sentence) #remove numbers
          sentence = re.sub(r'[^\w\s]', '', sentence) #remove ponc
          stems_to_add=[stemmer.stem(token) for token in word_tokenize(sentence) if not stemmer.stem(token) in stop_words]
          stems+= stems_to_add
      return(stems)
   

  
def num_tokens_without_punctuation(text):
  return(len(word_tokenizer(text,'word', 1, False )))
  
def sentence_tokenizer(text):
  sent_tokenized=[]
  sentences=text.split('\n')
  for sentence in sentences:
    sent_tokenized+=sent_tokenize(sentence)
  sent_tokenized=[element for element in sent_tokenized if len(element)>3]
  return(sent_tokenized, len(sent_tokenized))
  
def filter_articles(data):
  #articles withh >2 sentences
  data=data.loc[data['article_sentence_count']>=3]
  #remove dialogues
  data = data.loc[(data['article_text'].str.count('[A-Z]\w*:') <= 5) |(data['article_text'].str.contains('intervi', case = False)) ]
  return(data)

def check_articles(data, n, m , number):
  #randomly samples number acrticles from the range [n,m]
  data.reset_index(inplace=True, drop=True)
  indexes= sample(list(range(n,m)),number)
  for i in indexes:
    print("Article text: ")
    print(data.loc[i, "article_text"])
    print("Article summary: ")
    print(data.loc[i, "summary_text"])
    
    

def clean_text(row, transformations):
  for key in transformations.keys():
  	row=row.replace(key,transformations[key])
  row=re.sub("(__+)", ' ', str(row)).lower()   #remove _ if it occors more than one time consecutively
  row=re.sub("(--+)", ' ', str(row)).lower()   #remove - if it occors more than one time consecutively
  row=re.sub("(~~+)", ' ', str(row)).lower()   #remove ~ if it occors more than one time consecutively
  row=re.sub("(\+\++)", ' ', str(row)).lower()   #remove + if it occors more than one time consecutively
  row=re.sub("(\.\.+)", ' ', str(row)).lower()   #remove . if it occors more than one time consecutively
  row=re.sub(r"[<>()|&©ø\[\]\",;?~*!]", ' ', str(row)).lower() #remove <>()|&©ø"',;?~*!
  combined_pat = r'|'.join((r'https?://[^ ]+', r'www.[^ ]+'))
  row=clean3 = re.sub(combined_pat, '', row)
  row = re.sub("(\s+)",' ',str(row)).lower() #remove multiple spaces

  patterns_to_remove = ['\w+\.com.', 'CLICK HERE.*', '\(CNN\)', 'NEW\:', 'All righs reserved\.', '\w+\.net.']
  for pattern in patterns_to_remove:
    row=re.sub(pattern, '',row)
          
  return (row)

def create_dictionaries(corpus):
    stop_words=stopwords.words('english')
    words = dict()
    stems = dict()
    lemmas = dict()
    stemmer= PorterStemmer()
    lemmatizer= WordNetLemmatizer()
	
    i=0
    for text in corpus:
      if i%10000==0:
        print( str(i) + ' articles proceeeded') 
    # Removing stop words
      text = re.sub(r'[^\w\s]', '', text) 
      words_list = [token for token in word_tokenize(text)]

      for term in words_list:
            # dictionary of words
        if term in stop_words:
          continue
        if term in words:
          words[term] += 1
        else:
          words[term] = 1
            # dictionary of stems        
        stemed = stemmer.stem(term)
        if stemed in stop_words:
          continue
        if stemed in stems:
          stems[stemed] += 1
        else:
          stems[stemed] = 1
            # dictionary of lemmas        
        lemma = lemmatizer.lemmatize(term)
        if lemma in stop_words:
          continue
        if lemma in lemmas:
          lemmas[lemma] += 1
        else:
          lemmas[lemma] = 1
      i+=1
    return words, stems, lemmas
  
def most_freq_terms(dict, n=15):
  #sort dictionnary by terms frequncies
  sorted_dict= sorted(dict.items(), key=lambda item: item[1], reverse=True)
  n_freq_dict={}
  for i in range(n):
    n_freq_dict[sorted_dict[i][0]]=sorted_dict[i][1]
  return(n_freq_dict)
            
def plot_frequent_terms(dict, n,doc='articles', term_='words'):
    n_freq_terms=most_freq_terms(dict, n)
    fig = plt.figure(figsize=(12,6))
    ax = fig.add_subplot(111)
    terms = list(key for key in n_freq_terms.keys())
    frequencies = [n_freq_terms[term] for term in terms]
    ax.barh(y = terms, width = frequencies, color = 'red')
    fig.suptitle(doc + 'most ' + str(n)+' Frequent'+term_)
    ax.xlabel('Frequency')
  

def open_stories(pa):
    articles = [] #initialize the articles list()
    i=0
    for file in pa:
        #if i % 10000 ==0:  # to check if txet  files are being loaded
            #print(str(i) + "processed")
        f=open(os.getcwd()+"/stories/"+file, "r",encoding="utf8")
        articles.append(f.read())
        f.close()
        i+=1
    return(articles)
  
def open_summaries(pa):
    #do the same for the summaries
    summaries = [] #initialize the list
    i=0
    for file in pa:
        if i % 10000 ==0:
            print(str(i) + "processed")
        f=open(os.getcwd()+"/summaries/"+file, "r",encoding="utf8")
        summaries.append(f.read())
        f.close()
        i+=1
    return(summaries)

