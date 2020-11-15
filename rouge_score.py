from imports import *

def R_score(data, max_n=1, alpha=0.5, score="F1"):
  scores={"F1":"f", "Precision":"p", "Recall":"r"}
  assert(score in scores.keys())
  S=scores[score]
  #set rouge score parameters
  evaluator=rouge.Rouge(metrics = ['rouge-n'], max_n=max_n, alpha=alpha,
                        limit_length = False, stemming=True)
  scores_data=pd.DataFrame()
  index=data.index
  columns=data.columns[4:]
  for i in index:
    #reference summary
    ref=data.loc[i, "summary_text"]
    for col in columns:
      hyp = data.loc[i, col]
      # hypothesis summaries
      scores_data.loc[i, col+ " score"]= evaluator.get_scores(hyp, ref)['rouge-'+str(max_n)][S]
  return(scores_data)

def plot_distribution(scores_data, column_name, n_bins=30):
  _, ax = plt.subplots(figsize = (12,6))
  _, bins, _ = plt.hist(scores_data[column_name], n_bins, density=1, alpha=0.5)
  plt.ylabel('Distribution')
  plt.title("F-1 distribution for "+ column_name)
  plt.xlabel('Rouge Scores F-1 Values')
  mu, sigma = scipy.stats.norm.fit((scores_data[column_name]))
  best_fit_line = scipy.stats.norm.pdf(bins, mu, sigma)
  plt.plot(bins, best_fit_line)
  plt.show()
  print("\n")
  
