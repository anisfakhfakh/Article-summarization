from imports import *
from Preprocess import *

def text_freq_dict(text, tokenizer='word', n_gram=1, keep_ponctuation=False):
  #dictionnary containing the ngrams frequencies
  tokens_dict={}
  ngrams_dict={}
  tokens= word_tokenizer(text, tokenizer, n_gram, keep_ponctuation)
  if n_gram==1:
    for term in tokens:
      if term in tokens_dict:
        tokens_dict[term]+=1
      else:
        tokens_dict[term]=1
    return(tokens_dict)
  else:
    for term in tokens:
      if term in tokens_dict:
        tokens_dict[term]+=1
      else:
        tokens_dict[term]=1
    for i in range(1,n_gram+1):
      igrams_dict={}
      igrams_tokens=word_tokenizer(text, tokenizer, i, keep_ponctuation)
      for term in igrams_tokens:
        if term in igrams_dict:
          igrams_dict[term]+=1
        else:
          igrams_dict[term]=1
      ngrams_dict.update(igrams_dict)
    return(ngrams_dict)

def sentence_scoring(text, tokenizer='word', n_gram=1, keep_ponctuation=False):
  #score sentences by n-grams
  freq_table=text_freq_dict(text, tokenizer, n_gram, keep_ponctuation)
  max_freq=max(freq_table.values())
  f=lambda x: x/max_freq
  #normalize the frequencies
  freq_table=valmap(f, freq_table)
  sentence_scores={}
  sentences=sentence_tokenizer(text)[0]
  #calculate score of every sentence
  for sentence in sentences:
    sentence_ngram_count=0
    sentence_dict=text_freq_dict(sentence, tokenizer, n_gram, keep_ponctuation)
    for ngram_item in sentence_dict.keys():
      if ngram_item in freq_table.keys():
        sentence_ngram_count+= sentence_dict[ngram_item]
        if sentence in sentence_scores:
          sentence_scores[sentence]+=(freq_table[ngram_item]*sentence_dict[ngram_item])
        else:
          sentence_scores[sentence]=freq_table[ngram_item]*sentence_dict[ngram_item]
    # if empty sentence (after removing stop words): attribute score=0 
    if ((sentence in sentence_scores.keys()) and (sentence_scores[sentence]>0)):
      sentence_scores[sentence]= sentence_scores[sentence]/sentence_ngram_count
    else:
      sentence_scores[sentence]=0
  return(sentences,sentence_scores)
      
def avg_scoring(sentence_scores) :     
  scores_sum= sum(sentence_scores.values())
  #calculate avergae score
  avg_score=scores_sum/len(sentence_scores)
  return(avg_score)

def sum_by_threshold(text,factor=1,tokenizer='word', n_gram=1):
  #consider sentences with scores superior to certain threshold
  sentences,sentence_scores=sentence_scoring(text, tokenizer, n_gram)
  avg_score=avg_scoring(sentence_scores)
  f_threshold=factor*avg_score
  summary=""
  count=0
  for sent in sentences:
    if sentence_scores[sent]>=f_threshold:
      summary=summary+sent+" "
      count+=1
  return(summary[:-1], count)

def sum_by_count(text,count,tokenizer='word', n_gram=1):
  #count= number of sentences of hypothesis summary
  #select certain number of sentences
  sentences,sentence_scores=sentence_scoring(text, tokenizer, n_gram)
  filtered_sent=list(sent for sent,score in sorted(sentence_scores.items(), key=lambda item: item[1],reverse=True))[:count]
  #make sure summary sentences follow the same order in th article
  sentences=[sentence for sentence in sentences  if (sentence in filtered_sent)]
  summary=" ".join(sentences)
  return(summary[:-1], count)

def check_summary(article, original_summ, synth_summ, synth_summ2,width=100):
  f = lambda text: textwrap.dedent(text).strip()
  #original article
  print("ARTICLE:")
  print(textwrap.fill(f(article), width=width), '\n')
  #summary given by the dataset
  print("ORIGINAL SUMMARY:")
  print(textwrap.fill(f(original_summ), width=width), '\n')
  #summary obtained by threshold method
  print("SUMMARY BY THRESHOLD:")
  print(textwrap.fill(f(synth_summ), width=width), '\n')
  #summary obtained by count method
  print("SUMMARY BY COUNT:")
  print(textwrap.fill(f(synth_summ2), width=width), '\n')

def predict_summary(df,index, n_gram=2, token_type="word", factor=1):
  df=df.loc[index, :]	
  for i in index:
    text=df.loc[i,"article_text"]
    factor=factor
    summ1, count1=sum_by_threshold(text,factor,tokenizer=token_type,n_gram=n_gram)
    df.loc[i,"Summarization by threshold_"+str(n_gram)+"-gram_"+token_type+"_"+str(factor)+"-factor"]=summ1
  df=df[["Summarization by threshold_"+str(n_gram)+"-gram_"+token_type+"_"+str(factor)+"-factor"]]
  df.index.name = 'id'
  return(df)

def predict_summary2(df,index, n_gram=2, token_type="word"):
  df=df.loc[index, :]	
  for i in index:
    text=df.loc[i,"article_text"]
    count=df.loc[i,"summary_sentence_count"]
    summ2, count2=sum_by_count(text,count,tokenizer=token_type,n_gram=n_gram)
    df.loc[i,"Summarization by count"+str(n_gram)+"-gram_"+token_type]=summ2
  df=df[["Summarization by count"+str(n_gram)+"-gram_"+token_type]]
  df.index.name = 'id'
  return(df)
    
def generate_column_names(sum_type, n_gram, token_type, factor):
  if sum_type=="threshold":
    name1="Summarization by threshold_"+str(n_gram)+"-gram_"+token_type+"_"+str(factor)+"-factor"
    name2=name1+" score"
    return(name1, name2)
  elif sum_type=="count":
    name1="Summarization by count"+str(n_gram)+"-gram_"+token_type
    name2=name1+" score"
    return(name1, name2)

def get_params(stat_data, name):
  if "threshold" in name:
    params=re.findall(r"Summarization by threshold_(.*)-gram_(.*)_(.*)-factor score", name)[0]
    stat_data.loc[name, 'type']="threshold"
    stat_data.loc[name, 'n-gram']=int(params[0])
    stat_data.loc[name, 'token']=params[1]
    stat_data.loc[name, 'factor']=float(params[2])
  elif "count" in name:
    params=re.findall(r"Summarization by count(.*)-gram_(.*) score",name)[0]
    stat_data.loc[name, 'type']="count"
    stat_data.loc[name, 'n-gram']=int(params[0])
    stat_data.loc[name, 'token']=params[1]
  return(stat_data)
  
    