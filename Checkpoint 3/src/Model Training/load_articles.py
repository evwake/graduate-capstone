import pandas as pd
import os

RECAP_ARTICLE_DIRECTORY = "../../data/Recap Articles"
CONVERTED_ARTICLE_DIRECTORY = "../../data/Converted Articles"


def load_articles():
    converted_article_filenames = os.listdir(
        CONVERTED_ARTICLE_DIRECTORY)
    articles = {}
    for filename in converted_article_filenames:
        recap_article = ""
        converted_article = ""
        with open(f'{RECAP_ARTICLE_DIRECTORY}/{filename}', encoding='utf-8') as f:
            for line in f.readlines():
                recap_article += line.strip() + " "

        with open(f'{CONVERTED_ARTICLE_DIRECTORY}/{filename}', encoding='utf-8') as f:
            for line in f.readlines():
                converted_article += line.strip() + " "

        articles[filename] = {"recap": recap_article,
                              "converted": converted_article}
    return articles
