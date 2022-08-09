#This script works, but the site blocked me and I have no money for a proxy
import asyncio
import time
import aiohttp
from bs4 import BeautifulSoup
import re
import csv

start_time= time.time()

headers={
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.37"
}



with open("data.csv","w",newline='') as f:
    writer= csv.writer(f)
    writer.writerow(
        (
            "Name_anime", 
            "Count_of_series",
            "Genre",
            "Topics",
            "Years",
            "Age_limit"
        )   
    )

    
def get_urls():
    with open("index.html","r",encoding="utf-8") as file:
        src = file.read()
    
    soup = BeautifulSoup(src,"html.parser")

    anime = soup.find_all("div", class_="all_anime_global")
    urls = []
    
    for link in anime:
        url=link.find("a").get('href')
        urls.append(f"https://jut.su/{url}")

    return urls

def get_name_count_series():   
    with open("index.html","r",encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src,"html.parser")
    all_anime=soup.find_all("div",class_="all_anime")
    all_anime_name=[]
    all_count_series=[]
    #take name and count of series
    for anime in all_anime:
        anime_name=anime.find(class_="aaname").text
        all_anime_name.append(anime_name)
        anime_series= anime.find(class_="aailines").text.strip()
        list_num=re.split("[а-я]|' '",anime_series)
        
        i = 0
        while i < len(list_num):
            if list_num[i]=="":
                del list_num[i]
            else:
                i += 1
        list_num=[int(i.strip()) for i in list_num]
        count_series=max(list_num)
        
        all_count_series.append(count_series)
    return all_anime_name, all_count_series   



async def get_info(session,url,count_anime, all_anime_name, all_count_series): 
    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()
        soup = BeautifulSoup(response_text, "html.parser")
        try:
            info = soup.find("div",class_="under_video_additional the_hildi").text.strip()
            info = re.sub("Аниме","",info)
            info = re.sub(r"(\s(и)\s)",",",info)
            info=re.split("[:|.|,]",info)

            genre=[]
            topics=[]
            years=[]
            old=re.search(r"\d\d\+","".join(info))
            try:
                old=old.group(0)
            except:
                old=""
            for i in info:
                if i =='Жанры' or i =='Жанр':
                    j=1
                    while info[j]!='Тема' and info[j]!='Темы' and info[j]!='Годы выпуска' and info[j]!='Год выпуска':
                        genre.append(info[j].strip())
                        j+=1
       
                if i =='Темы' or i =='Тема':
                    k=j+1
                    while info[k]!='Годы выпуска' and info[k]!='Год выпуска':
                        topics.append(info[k].strip())
                        k+=1
                if i =='Годы выпуска' or i =='Год выпуска':
                    try:
                        l=k+1
                    except:
                        l=j+1
                    try:
                        while info[l]!='Оригинальное название':
                            years.append(info[l].strip())
                            l+=1
                        break 
                    except:
                        break
            del j
            try:
                del k
            except:
                pass
            del l
            with open("data.csv","a",newline='') as f:
                writer= csv.writer(f)
                writer.writerow(
                    (
                        all_anime_name[count_anime-1],
                        all_count_series[count_anime-1],
                        ",".join(genre),
                        ",".join(topics if topics!=[] else "-"),
                        ",".join(years),
                        old
                        )
                )
            print(f"[INFO] Anime number {count_anime}/{len(all_anime_name)} complited")
        except:
            print(f"[ERROR] Anime number {count_anime}/{len(all_anime_name)}, name {all_anime_name[count_anime-1]}")
        
    
async def gather_data():
    async with aiohttp.ClientSession() as session:
        count_anime=0
        print("[INFO] Starting download all information")
        
        all_anime_name, all_count_series= get_name_count_series()
        tasks = []
        #take genre, topics, years and age limit
        for url in get_urls():
            task = asyncio.create_task( get_info(session,url,count_anime, all_anime_name, all_count_series))
            tasks.append(task)
            count_anime+=1

        await asyncio.gather(*tasks)
def main():

    asyncio.run(gather_data())

if __name__=="__main__":
    main()
    finish_time=time.time()-start_time
    print(f"Script running time - {finish_time}")





    

