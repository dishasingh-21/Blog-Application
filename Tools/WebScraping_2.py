import requests, csv, urllib3
from datetime import datetime
from bs4 import BeautifulSoup
from base64 import b64decode, b64encode

page_urls = ["https://dev.to/top/week","https://dev.to/latest", "https://dev.to/top/month", "https://dev.to/top/year"]
for page_url in page_urls:
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "lxml")
    print("Scraping started..")
    title_tags = soup.find_all('h2', attrs={'class':'crayons-story__title'})
    print('1st phase over..')
    links=[]
    titles=[]
    for tag in title_tags:
        a_tag = tag.find('a')
        if a_tag and a_tag.get('href'):
            links.append(a_tag.get('href'))
        titles.append(tag.text.strip())
    print('links list filled..Now data addition in csv starts..')
    for title, link in zip(titles, links):
        res = requests.get(link)
        soup = BeautifulSoup(res.content, "lxml")
        blog = soup.find('div', attrs={'class':'crayons-article__body text-styles spec__body'})
        blog_text = b64encode(str(blog).encode()).decode('utf-8') if blog else "Blog content not found"
        with open('blog_data.csv', 'a', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([title, blog_text, datetime.now()])
            print('done this one..go on')
            
    print('And all done..')

