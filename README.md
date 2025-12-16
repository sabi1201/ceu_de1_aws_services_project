## Introduction

Artificial intelligence has seen enormous growth in recent years. Large investments, rapid technological progress, and constant media attention have led many to describe the current moment as an **“AI boom.”** At the same time, journalists and analysts increasingly question whether this growth is sustainable or whether it shows the signs of a financial bubble that could eventually burst.

News media play an important role in shaping how this debate is understood by the public. However, coverage of AI does not look the same everywhere. Economic conditions, political priorities, and local technology ecosystems differ across countries, and these differences may influence how risks and opportunities related to AI are discussed. As a result, reporting on a potential “AI bubble” may vary in tone from one region to another.

Comparing media coverage across countries is not straightforward, especially when articles are written in different languages. Cloud-based AI services make it possible to address this challenge by translating text and applying consistent analysis methods. In this project, we use AWS managed services to analyze and compare the sentiment of news articles about a potential AI bubble from multiple countries and regions.

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

1. Creating a dedicated cloud storage location to keep all data and results organized.
2. Collecting and storing raw article text.
3. Translating non-English articles into English to enable uniform analysis.
4. Applying automated sentiment analysis.
5. Aggregating and visualizing the results for comparison across countries.

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
