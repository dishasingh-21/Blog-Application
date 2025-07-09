import requests, csv
from datetime import datetime
from bs4 import BeautifulSoup
from base64 import b64decode, b64encode
#hashnode code

page_urls = ['https://hashnode.com/featured', 'https://hashnode.com/feed?source=main-header']
for page_url in page_urls:
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "lxml")
    print('scraping started successfully..')
    title_tags = soup.find_all('div',attrs={'class':'flex flex-col gap-1'})
    print("titles fetched..")
    links = []
    titles = []
    for tag in title_tags:
        h1_tag = tag.find('h1')
        if h1_tag and h1_tag.text:
            titles.append(h1_tag.text.strip())
        a_tag = tag.find('a')
        if a_tag and a_tag.get('href'):
            links.append(a_tag.get('href'))

    print("all links fetched..")
    print("Phase-I over")
    print("Fetching indiviudal blog data")
    for title, link in zip(titles,links):
        res = requests.get(link)
        soup = BeautifulSoup(res.content, "lxml")
        print("Scraping starts..")
        blog = soup.find('div', attrs={'id', 'post-content-wrapper'})
        blog_text = b64encode(str(blog).encode()).decode('utf-8')
        with open('blog_data.csv', 'a', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([title, blog_text, datetime.now()])
            print("done this one.. go on")

#designboom code

'''page_urls = ['https://www.designboom.com/architecture/', 'https://www.designboom.com/readers/', 'https://www.designboom.com/design/', 'https://www.designboom.com/art/']
for page_url in page_urls:
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "lxml")
    print('scraping started successfully..')
    title_link_tags = soup.find_all('a',attrs={'class':'p--p-title x-p'})
    print("titles fetched..")
    links = []
    titles = []
    for tag in title_link_tags:
        titles.append(tag.text.strip())
        links.append(tag.get('href'))

    print("all links fetched..")
    print("Phase-I over")
    print("Fetching indiviudal blog data")
    for title, link in zip(titles,links):
        res = requests.get(link)
        soup = BeautifulSoup(res.content, "lxml")
        print("Scraping starts..")
        blog = soup.find('div', attrs={'class', 'page-content'})
        blog_text = b64encode(str(blog).encode()).decode('utf-8')
        with open('blog_data.csv', 'a', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([title, blog_text, datetime.now()])
            print("done this one.. go on")'''

'''page_url = 'https://www.designboom.com/technology/'
response = requests.get(page_url)
soup = BeautifulSoup(response.content, "lxml")
print('scraping started successfully..')
title_link_tags = soup.find_all('a',attrs={'class':'p--p-title x-p'})
print("titles fetched..")
links = []
titles = []
for tag in title_link_tags:
    titles.append(tag.text.strip())
    links.append(tag.get('href'))

print("all links fetched..")
print("Phase-I over")
print("Fetching indiviudal blog data")
for title, link in zip(titles,links):
    res = requests.get(link)
    soup = BeautifulSoup(res.content, "lxml")
    print("Scraping starts..")
    blog = soup.find('div', attrs={'class', 'page-content'})
    blog_text = b64encode(str(blog).encode()).decode('utf-8')
    with open('blog_data.csv', 'a', encoding='utf-8', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([title, blog_text, datetime.now()])
        print("done this one.. go on")'''

#substack code
'''page_urls = []
for i in range(1,5):
    page_urls.append(f'https://read.write.as/p/{i}')
print("process starts..")
for page_url in page_urls:
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "lxml")
    title_tag = soup.find_all('h2', attrs={'class':'post-title'})
    titles=[]
    links=[]
    for tag in title_tag:
        a_tag = tag.find('a')
        if a_tag:
            links.append(a_tag.get('href'))
            titles.append(a_tag.text.strip())
    
    for title in titles:
        print(title)

    print("phase-1 done..")
    for title, link in zip(titles, links):
        res = requests.get(link)
        soup = BeautifulSoup(res.content, "lxml")
        blog = soup.find('div', attrs={'class':'e-content'})
        with open('blog_data.csv', 'a', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([title, blog.text.strip(), datetime.now()])
            print("this one done..go on")

    print("phase-2 done..")

print('all data stored successfully..')'''

#blot.im blog code
'''page_urls = []
page_urls.append('https://qeig.blot.im/archives')
print("process starts..")
for page_url in page_urls:
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "lxml")
    title_tag = soup.find_all('section', attrs={'class':'archives'})
    titles=[]
    links=[]
    for tag in title_tag:
        a_tags = tag.find_all('a')
        for a_tag in a_tags:
            links.append('https://qeig.blot.im'+a_tag.get('href'))
            t = a_tag.find('span',attrs={'class':'title'})
            if t:
                titles.append(t.text.strip())
    
    for title in titles:
        print(title)

    print("phase-1 done..")
    for title, link in zip(titles, links):
        res = requests.get(link)
        soup = BeautifulSoup(res.content, "lxml")
        blog = soup.find('section', attrs={'class':'entry'})
        blog_text = b64encode(str(blog).encode()).decode('utf-8')
        with open('blog_data.csv', 'a', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([title, blog_text, datetime.now()])
            print("this one done..go on")

    print("phase-2 done..")

print('all data stored successfully..')'''

#listed.to code
'''page_url = 'https://listed.to/'
response = requests.get(page_url)
soup = BeautifulSoup(response.content, "lxml")
profile_urls = soup.find_all('li', attrs={'class':'author active-author'},limit=15)
profile_links=[]
for profile_url in profile_urls:
    a_tag = profile_url.find('a')
    if a_tag:
        profile_links.append(a_tag.get('href'))

for profile_link in profile_links:
    resp = requests.get(profile_link)
    soup = BeautifulSoup(resp.content, "lxml")
    title_tags = soup.find_all('div', attrs={'class':'author-post'})
    links=[]
    titles=[]
    for tag in title_tags:
        a_tag = tag.find('a')
        if a_tag:
            links.append(a_tag.get('href'))
            titles.append(a_tag.text.strip())

    print("phase-1 over..")

    for title, link in zip(titles, links):
        res = requests.get(link)
        soup = BeautifulSoup(res.content, "lxml")
        blog = soup.find('div', attrs={'class':'post-body p1'})
        blog_content = b64encode(str(blog).encode()).decode('utf-8')
        with open('blog_data.csv', 'a', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([title, blog_content, datetime.now()])
            print("this one done..go on")

        print("phase-2 over..")

print("All tasks completed successfully..")
'''