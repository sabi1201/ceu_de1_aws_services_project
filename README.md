# Comparing Media Sentiment on the “AI Bubble” Across Countries Using AWS
Table of Contents
- [Introduction](#introduction)
- [Problem Definition](#problem-definition)
- [Dataset and Data Sources](#data-sources)
- [The Approach](#the-approach)
  - [1. Creating and Organizing an S3 Bucket](#1-creating-and-organizing-an-s3-bucket)
  - [2. Article Collection and Language Detection](#2-collecting-the-articles-and-storing-raw-text)
  - [3. Translation of Non-English Articles](#3-translating-non-english-articles-to-english)
  - [4. Sentiment Analysis](#4-running-sentiment-analysis-on-all-articles)
  - [5. Sentiment Comparison Across Countries](#5-aggregating-sentiment-results-and-comparing-countries)
  - [6. Key Phrase Analysis](#6-additional-key-phrase-analysis)
- [Findings and Results](#findings)
- [Conclusion](#conclusion)
- [AWS Cost Breakdown](#aws-cost-breakdown)
- [Reproducibility](#reproducibility)


## Introduction

Artificial intelligence has seen enormous growth in recent years. Large investments, rapid technological progress, and constant media attention have led many to describe the current moment as an **“AI boom.”** At the same time, journalists and analysts increasingly question whether this growth is sustainable or whether it shows the signs of a financial bubble that could eventually burst.

News media play a key role in shaping how this debate is presented to the public. Articles about AI often go beyond technical developments and address broader issues such as investment risk, economic expectations, and long-term societal impact. Because countries differ in their economic conditions, regulatory environments, and technology ecosystems, it is reasonable to expect that media coverage of a potential “AI bubble” may vary across regions.

Understanding these differences can provide insight into how global narratives around AI are formed and communicated.

## Problem Definition
**Research Question**: *How does the sentiment of news coverage about a potential “AI bubble” differ across countries and regions?*

While individual articles can be read and interpreted on their own, it is difficult to compare tone across multiple countries in a systematic way. This difficulty increases when articles are written in different languages, as subjective interpretation and translation choices can introduce bias. Without a standardized analytical approach, cross-country comparisons risk being inconsistent or anecdotal.

To address this, we apply a data-driven approach using [AWS serverless services](https://aws.amazon.com/ru/console/). We collect news articles from a diverse set of countries that discuss the idea of an AI bubble, translate all non-English articles into English, and then apply automated sentiment analysis. This allows us to compare sentiment signals across countries in a consistent and reproducible way.

Importantly, this project does not attempt to determine whether AI truly represents a financial bubble. Instead, it focuses on how the topic is discussed in different regions and whether there are observable differences in tone across international news coverage.

## Data Sources

The dataset used in this project consists of 12 news articles that explicitly discuss the idea of a potential “AI bubble.” All articles were published by established news outlets and focus on the economic, technological, or societal implications of rapid AI growth.

The articles were selected with the goal of capturing geographic and linguistic diversity, rather than maximizing the number of sources. The final dataset includes coverage from Europe, Asia, Australia, Latin America, and Central Asia, allowing for a cross-country comparison of how the same topic is discussed in different regions. Articles were written in multiple languages, including English, German, French, Russian, Hindi, Japanese, Portuguese, and Thai.

All articles were published within a similar recent timeframe (primarily 2024–2025), ensuring that they reflect a comparable stage in the public debate around AI and its economic implications. Importantly, all selected articles directly engage with the question of whether current developments in artificial intelligence represent sustainable progress or speculative excess.

Article selection was guided by two main criteria:

- Relevance: each article explicitly discusses the concept of an AI boom or bubble.

- Accessibility: sources had to be freely available without requiring paid subscriptions.

While this accessibility constraint limited the pool of possible sources, the selected outlets remain representative of mainstream national and international media within their respective regions. The dataset includes a mix of general news organizations and business-focused publications, helping to reduce reliance on a single editorial perspective.

| Country / Region | News outlet |
|------------------|---------|
| Germany          | [Handelsblatt](https://live.handelsblatt.com/blasen-bei-ki-werten-platzen-sie-bald-oder-geht-da-noch-was/) |
| United Kingdom   | [The Guardian](https://www.theguardian.com/technology/2025/dec/01/ai-bubble-us-economy) |
| Australia        | [9 News](https://www.9news.com.au/technology/are-we-in-an-ai-tech-bubble-what-happens-if-it-bursts-explainer/c11d1f63-a085-419d-bc62-030911459304) |
| Russia           | [Meduza](https://meduza.io/feature/2025/10/13/eksperty-vse-chasche-nazyvayut-bum-iskusstvennogo-intellekta-finansovym-puzyrem-eto-priznayut-dazhe-sami-razrabotchiki-ii) |
| India            | [The Times of India](https://navbharattimes.indiatimes.com/business/business-news/ai-bubble-on-the-verge-of-bursting-bigger-crisis-than-2008-what-are-the-challenges-for-india-what-it-should-do/articleshow/124362358.cms) |
| Japan            | [The Japan Times](https://www.japantimes.co.jp/news/2025/11/14/japan/media/japan-media-ai-threat/) |
| Brazil           | [CNN Brasil](https://www.cnnbrasil.com.br/economia/mercado/resultados-da-oracle-sinalizam-bolha-de-ia-entenda-debate/) |
| France           | [La Gazette France](https://www.lagazettefrance.fr/index.php/article/une-bulle-de-l-intelligence-artificielle) |
| Poland           | [Vestbee](https://www.vestbee.com/insights/articles/are-we-in-an-ai-bubble-we-asked-european-investors) |
| Uzbekistan       | [Qaz Inform](https://qazinform.com/news/uzbekistan-to-lay-off-over-2000-government-employees-amid-ai-integration-c7d87e) |
| Kazakhstan       | [The Astana Times](https://astanatimes.com/2025/10/kazakhstan-advances-ai-digital-ecosystem-development-under-governments-digital-headquarters/) |
| Thailand         | [Bangkok BizNews](https://www.bangkokbiznews.com/world/1206507) |

The full list of article URLs is included in the repository for transparency and reproducibility.

## The Approach
To answer our research question, we built a small but complete data analysis pipeline using AWS-managed, serverless services. The goal was to take a set of international news articles discussing a potential “AI bubble” and process them in a way that allows consistent comparison across countries and languages.

At a high level, our approach consisted of the following steps:

1. Creating a dedicated cloud storage location to keep all data and results organized
2. Collecting and storing raw article text
3. Translating non-English articles into English to enable uniform analysis
4. Applying automated sentiment analysis
5. Aggregating and visualizing the results for comparison across countries
6. Extracting key phrases to add qualitative context to the sentiment findings

All steps were implemented in Python using AWS APIs (via `boto3`) and organized into notebooks that can be executed sequentially or as part of an automated pipeline.

### 1. Creating and Organizing an S3 Bucket

The first step in our workflow was to create a dedicated Amazon [S3](https://aws.amazon.com/ru/s3/) bucket to store all intermediate and final outputs of the project. Using a single bucket for the entire pipeline helped keep the project reproducible and ensured that data from different stages (raw text, translations, analysis results, and visualizations) remained clearly separated and easy to track.

We used Amazon S3 because it is a fully serverless storage service that integrates seamlessly with other AWS services such as Translate and Comprehend.

To ensure that the pipeline could be rerun without errors, we first checked whether the bucket already existed. If it did not, the bucket was created in the selected AWS region; otherwise, the existing bucket was reused.

```python
new_bucket = "aruzhan-sabira-hw3"
s3 = boto3.client("s3")
default_region = 'eu-west-1'
bucket_names = [bucket["Name"] for bucket in s3.list_buckets()["Buckets"]]
if new_bucket not in bucket_names:
    bucket_configuration = {"LocationConstraint": default_region}
    response = s3.create_bucket(Bucket=new_bucket, CreateBucketConfiguration=bucket_configuration)
    print(f"Created new bucket: {new_bucket}")
else:
    print(f"Using existing bucket: {new_bucket}")
```

### 2. Collecting the Articles and Storing Raw Text 

After setting up storage, we collected our dataset by scraping the full text of 12 news articles about a potential “AI bubble” from different countries. Because we later compare sentiment across countries and languages, our first goal was to create a consistent “raw text” dataset that could be processed by AWS services.

We used a simple and reproducible scraping approach:

- download each page with requests
- extract the main text using `BeautifulSoup`
- store the raw extracted text both locally (for quick inspection) and in Amazon S3 (for the rest of the pipeline)

We also used [Amazon Comprehend](https://aws.amazon.com/ru/comprehend/) at this stage to automatically detect the dominant language of each scraped article. That allowed us to separate English articles from non-English ones early in the pipeline, which made the next translation step cleaner.

**Main pipeline logic (simplified)**

We defined a list of article URLs and looped through them:
```python
ARTICLE_URLS = [ ... 12 URLs ... ]

for url in ARTICLE_URLS:
    text_content = scrape_article_text(url)
    language_code, confidence = detect_language(text_content)
```
To scrape the page, we used a user-agent header and extracted text from the `<article>` tag when possible (falling back to other main page elements if needed):
```python
response = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(response.content, "html.parser")
main_content = soup.find("article") or soup.find("main") or soup.body
article_text = main_content.get_text(separator="\n", strip=True)
```
For language detection, we called Amazon Comprehend’s dominant language detection on a truncated portion of the text (Comprehend has request size limits):
```python
response = comprehend_client.detect_dominant_language(Text=text_content[:4900])
language_code = response["Languages"][0]["LanguageCode"]
```
Finally, we saved each article as a `.txt` file locally and uploaded it to S3. Based on the detected language, the article was stored under an English or non-English “raw text” location in the bucket:
```python
if language_code == "en":
    s3_key_prefix = "raw_articles/english/"
else:
    s3_key_prefix = "raw_articles/non-english/"

s3_client.upload_file(local_file_path, S3_BUCKET_NAME, s3_key_prefix + local_file_name)
```
At the end of this step, we had a complete raw-text dataset stored in S3, separated by language. This raw dataset becomes the input for the next stage of the project (translation of non-English articles into English).

### 3. Translating Non-English Articles to English

Because our dataset includes articles written in multiple languages, we needed to convert all non-English texts into English before running sentiment analysis. This step ensures we analyze all articles using the same language and the same sentiment model, making cross-country comparison meaningful.

We used [AWS Translate](https://aws.amazon.com/ru/translate/) to translate the non-English articles stored in S3. The input of this step is the “non-English raw articles” folder in our bucket, and the output is a separate “translated articles” folder containing English versions of the same files.

**Main pipeline logic (simplified)**

We first listed all objects stored under the non-English prefix in S3:
```python
file_list_response = s3_client.list_objects_v2(
    Bucket=S3_BUCKET_NAME,
    Prefix=S3_INPUT_PREFIX
)
```
Then we looped over each file and translated it:
```python
for obj in file_list_response["Contents"]:
    input_key = obj["Key"]
    if input_key.endswith("/"):
        continue
    translate_and_upload_file(S3_BUCKET_NAME, input_key)
```
**Handling AWS Translate size limits**

AWS Translate has limits on how much text can be sent in a single request. To avoid failures on long articles, we translated each file in byte-safe chunks and then merged the translated parts back together.
```python
translation_response = translate_client.translate_text(
    Text=string_chunk,
    SourceLanguageCode="auto",
    TargetLanguageCode="en"
)
translated_text_parts.append(translation_response["TranslatedText"])
```
After translating a file, we uploaded the final English text back to S3:
```python
output_key = S3_OUTPUT_PREFIX + os.path.basename(input_key)

s3_client.put_object(
    Bucket=bucket_name,
    Key=output_key,
    Body=full_translated_text.encode("utf-8"),
    ContentType="text/plain"
)
```
At the end of this step, every non-English article had an English version stored in S3. These translated files were then used as input for our sentiment analysis stage.

### 4. Running Sentiment Analysis on All Articles
Once all articles were available in English (either originally written in English or translated in the previous step), we ran sentiment analysis using **AWS Comprehend**. This allowed us to quantify the tone of each article in a consistent way.

We used Comprehend’s synchronous sentiment API (`detect_sentiment`) to produce a sentiment label (POSITIVE / NEGATIVE / NEUTRAL / MIXED) along with confidence scores. For reproducibility and easier downstream processing, we stored each article’s sentiment output as a small JSON file in S3.

At this point, English-language text existed in two places in S3 and we processed both folders:

- the folder containing articles that were originally in English
- the folder containing translated versions of non-English articles

To comply with AWS Comprehend input size limits, sentiment analysis was performed on a safe portion of each article’s text. The core sentiment analysis call was:
```python
response = comprehend_client.detect_sentiment(
    Text=string_chunk,
    LanguageCode="en"
)
```
For each article, we stored the sentiment label and confidence scores as a JSON file and uploaded the result back to S3. Each result file includes:

- the source article identifier
- the detected sentiment
- confidence scores for positive, negative, neutral, and mixed sentiment
- a timestamp of the analysis

At the end of this step, every article had a corresponding sentiment result stored in S3. These sentiment outputs served as the input for the final aggregation and comparison stage of the analysis.

### 5. Aggregating Sentiment Results and Comparing Countries

After running sentiment analysis on each article, the output consisted of one JSON file per article stored in Amazon S3. In this final processing step, we aggregated these individual results into a single dataset and created a country-level comparison that could be used directly in the report.

The main goals of this step were to:

1. collect all sentiment outputs from S3,
2. structure them into a tabular format,
3. associate each article with a country or region,
4. compute average sentiment scores per country.

We first listed and downloaded all sentiment result files stored in the S3 results folder:
```python
pages = s3_client.get_paginator("list_objects_v2").paginate(
    Bucket=S3_BUCKET_NAME,
    Prefix=S3_RESULTS_PREFIX
)
```
Each JSON file was read and added to a list that was later converted into a Pandas DataFrame.
AWS Comprehend returns sentiment confidence scores as a nested object. To make analysis easier, we flattened these scores into separate numeric columns:
```python
df_scores = pd.json_normalize(df["ConfidenceScores"])
df = pd.concat([df.drop("ConfidenceScores", axis=1), df_scores], axis=1)
```
This resulted in one row per article with explicit positive, negative, neutral, and mixed sentiment scores. Then, each article was mapped to a country or region using a predefined mapping based on the source outlet. Finally, we grouped the data by country/region and computed the average sentiment scores.
The resulting table summarizes sentiment differences across countries and serves as the main quantitative output of the analysis.

| Country/Region             | Dominant_Sentiment | Positive | Negative | Neutral |
| -------------------------- | ------------------ | -------- | -------- | ------- |
| Australia (9 News)         | NEUTRAL            | 5.73%    | 0.31%    | 93.11%  |
| Brazil (CNN Brazil)        | NEUTRAL            | 0.40%    | 9.87%    | 89.65%  |
| France (La Gazette)        | NEUTRAL            | 9.86%    | 0.26%    | 89.47%  |
| Germany (Handelsblatt)     | NEUTRAL            | 0.23%    | 1.36%    | 97.43%  |
| India (Times of India)     | NEUTRAL            | 3.35%    | 35.67%   | 49.37%  |
| Japan (Japan Times)        | NEUTRAL            | 0.08%    | 1.50%    | 98.39%  |
| Kazakhstan (Astana Times)  | NEUTRAL            | 0.19%    | 0.00%    | 99.81%  |
| Poland (Vestbee)           | NEUTRAL            | 13.03%   | 0.05%    | 86.89%  |
| Russia (Meduza)            | NEUTRAL            | 7.70%    | 2.29%    | 89.27%  |
| Thailand (Bangkok BizNews) | NEUTRAL            | 3.38%    | 0.64%    | 95.95%  |
| The Guardian (USA)         | NEUTRAL            | 0.28%    | 0.11%    | 99.58%  |
| Uzbekistan (Qaz Inform)    | NEUTRAL            | 0.67%    | 0.07%    | 99.26%  |

This table provides a compact overview of how sentiment related to the “AI bubble” varies across countries, even when the dominant sentiment label is neutral.

### 6. Additional Key Phrase Analysis
While sentiment analysis showed that coverage of the potential “AI bubble” is largely neutral across countries, it does not explain what aspects of the topic are emphasized by different media outlets. To address this, we extracted key phrases from each article to better understand the thematic focus behind the sentiment scores.

We applied AWS Comprehend’s key phrase extraction to the English text of all articles (both originally English and translated). This allowed us to identify the most salient concepts discussed in each article using a consistent language and model.

The core extraction step was performed with:
```python
response = comprehend_client.detect_key_phrases(
    Text=text_chunk,
    LanguageCode="en"
)
```
Because raw key phrase extraction often includes irrelevant website or metadata terms, we filtered the output by keeping only high-confidence phrases and removing common navigation or boilerplate patterns. This resulted in a concise set of meaningful phrases for each article.

| Media Source | Top Key Phrases |
|-------------|----------------|
| The Guardian (USA) | The question, the AI bubble, the fallout, Edua... |
| Poland (Vestbee) | the biggest, invitation-only event, an AI bubb... |
| Australia (9 News) | an AI tech bubble, the valuations, the company... |
| Japan (Japan Times) | a lawsuit, the Tokyo District Court, Generativ... |
| Kazakhstan (Astana Times) | ’s Presidency, ’s Presidency, Digital Ecosyste... |
| Uzbekistan (Qaz Inform) | 2,000 government employees, AI integration ... |
| Thailand (Bangkok BizNews) | DOLLAR AI BUBBLE, BIG TECH FEARS MARCH, LOANS ... |
| India (The Times of India) | The boom, Artificial Intelligence, the form, a... |
| Germany (Handelsblatt) | AI values, The numerous headlines warning, an ... |
| Russia (Meduza) | the AI boom, a financial bubble, tech companie... |
| Brazil (CNN Brazil) | an AI bubble, the debate, the company, office ... |
| France (La Gazette) | An artificial intelligence bubble, The huge ca... |


For reporting purposes, we stored a short summary of the most prominent key phrases per article alongside the media source and sentiment label. These per-article summaries were aggregated into a single table and saved as a CSV file in Amazon S3. 

## Findings
Our sentiment analysis shows a striking consistency across countries: all analyzed articles are classified as neutral by AWS Comprehend. This indicates that media coverage of a potential “AI bubble” is generally cautious, analytical, and balanced rather than overtly optimistic or alarmist.

However, looking beyond the dominant sentiment label reveals important variation in sentiment confidence scores. While neutrality dominates everywhere, the degree of neutrality and the relative presence of negative or positive signals differ across regions.

To illustrate this, we computed and visualized the average sentiment confidence scores (positive, negative, neutral) for each country/media source.

<img width="1179" height="590" alt="image" src="https://github.com/user-attachments/assets/86488b24-8265-49dc-827e-6a7315cc16f0" />

The chart highlights several important patterns:

- Neutral sentiment dominates everywhere, often exceeding 90% confidence, confirming that discussion of the AI bubble is largely framed in an analytical and explanatory manner.
- India (The Times of India) stands out with a notably higher negative sentiment confidence, suggesting stronger concern about risks or potential downsides compared to other countries.
- Government- or policy-oriented articles (e.g. Kazakhstan, Uzbekistan) exhibit extremely high neutral confidence, indicating descriptive or informational coverage rather than evaluative commentary.

These differences suggest that, while the overall tone is neutral, regional context influences how strongly risks or concerns are emphasized.

**Insights from key phrase analysis**

Key phrase extraction adds qualitative context to the sentiment findings. Across nearly all articles, the concept of an “AI bubble” appears as a central framing device. Beyond this shared reference point, articles diverge in focus:

- Financial and business-oriented outlets emphasize valuations, companies, investors, and market dynamics.
- Several Asian and Central Asian sources focus more on government strategy, public sector adoption, and digital infrastructure.
- Some articles highlight legal, economic, or social consequences, such as regulation, lawsuits, or workforce impact.

This helps explain why sentiment remains neutral overall: many articles discuss potential risks without adopting a strongly negative stance, instead presenting multiple perspectives or outlining possible future scenarios.

## Conclusion

In this project, we analyzed how media outlets in different countries discuss the idea of a possible “AI bubble” using a small but diverse set of news articles. By combining web scraping with AWS services for translation, sentiment analysis, and key phrase extraction, we built a reproducible pipeline to compare coverage across languages and regions.

The results show that discussion of the AI bubble is largely neutral in tone worldwide. At the same time, articles differ in what they focus on: some emphasize market valuations and investor behavior, while others highlight government policy, public sector adoption, or broader economic effects. This suggests that the AI bubble is a shared global topic, but one that is framed differently depending on regional context and media priorities.

Overall, the project demonstrates how AWS serverless AI services can be used to analyze international media narratives in a structured and scalable way, even with a relatively small dataset.

## Cost

## Reproducibility: How to Run This Project Yourself

1) Fork the repository and open a Codespace
2) Configure AWS credentials (two options)

You need AWS credentials with permission to use at least:
- S3
- Translate
- Comprehend

Option A: Use Codespaces Secrets

Option B: Configure credentials inside the Codespace terminal

Enter:

- AWS Access Key ID
- AWS Secret Access Key
- Default region name: eu-west-1

3) Install Python dependencies

From the repository root, run:
`pip install -r requirements.txt`

4) Run the full pipeline

The project includes a pipeline script that executes the notebooks

`python pipeline.py`

This will run the notebooks in sequence (bucket setup → scraping → translation → sentiment → comparison → key phrases) and save executed versions in the `executed_notebooks/` folder.

5) Where to find outputs

After a successful run, you can find raw scraped article text, translated articles, sentiment JSON outputs, aggregated tables (CSV), charts (if saved) in S3.
