import os
import re
data_folder = os.listdir('../data collection/output')
num_docs = len(data_folder)
original_char_count = 0
original_word_count = 0
article_dict = {}
for game in data_folder:
    filename = '../data collection/output/' + game + '/' + game + '.txt'
    article = ""
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            original_char_count += len(line)
            original_word_count += len(line.split(" "))
            article += line
    article = re.sub(r'[\"“”].*?[\"“”]', '', article)
    article_dict[game] = article



print("Number of articles:", num_docs)
print("Average number of words per article before preprocessing", original_word_count / num_docs)
print("Average number of characters per article before preprocessing", original_char_count / num_docs)
print("")

with open('keywords.txt', 'r') as keyword_file:
    keywords = []
    for line in keyword_file:
        keywords.append(line.strip())

preprocessed_char_count = 0
preprocessed_word_count = 0
for article_name in article_dict:
    article = article_dict[article_name]
    article_sentences = re.split(r'\n', article)
    new_article = ""
    for sentence in article_sentences:
        for term in keywords:
            if term in sentence:
                new_article += sentence + "\n"
                preprocessed_char_count += len(sentence)
                preprocessed_word_count += len(sentence.split(" "))
                break
    preprocessed_article = open("output/" + article_name + ".txt", 'w', encoding="utf-8")
    preprocessed_article.write(new_article)
    preprocessed_article.close()


    
print("Average number of words per article after preprocessing", preprocessed_word_count / num_docs)
print("Average number of characters per article after preprocessing", preprocessed_char_count / num_docs)
