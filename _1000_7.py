import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import re
import requests
import csv
import sqlalchemy

start_time=time.time()

headers={
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}

engine = sqlalchemy.create_engine("postgresql+psycopg2://postgres:rootroot@localhost:5432/anime")
connection = engine.connect()

with connection.begin() as trans:
    connection.execute("DROP TABLE IF EXISTS anime")

with connection.begin() as trans:
    connection.execute("""CREATE TABLE IF NOT EXISTS anime(
                        anime_id serial PRIMARY KEY,
                        anime_name text,
                        count_of_series int,
                        genre text,
                        topics text,
                        years text,
                        age_limit text

    )""")

# with open("data.csv","w",newline='') as f:
#     writer= csv.writer(f)
#     writer.writerow(
#         (
#             "Name_anime", 
#             "Count_of_series",
#             "Genre",
#             "Topics",
#             "Years",
#             "Age_limit"
#         )   
#     )

#this function takes the link from each element of the main page
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
#this function takes the main page with all anime
def get_data():
    print("Wait for the program to take the site code itself (do not touch or click anything)")
    # time.sleep(3)
    # driver = webdriver.Chrome(
    #         executable_path=r"C:\Users\ЯкименкоЄвгенійСергі\source\repos\1000-7\chromedriver"   
    #     )
    # try:
        
    #     driver.get(url="https://jut.su/anime/")
    #     time.sleep(3)
    #     count=0
    #     while True:
    #         find_more_elem = driver.find_element(by=By.CLASS_NAME,value="load_more_anime")
            
    #         if find_more_elem:
    #             actions = ActionChains(driver)
    #             actions.move_to_element(find_more_elem).perform()
    #             count+=1
    #             print(f"[INFO] {count} page complited")
    #             time.sleep(10)
            
    #         if count==28:
    #             with open("index.html","w",encoding="utf-8") as f:
    #                 f.write(driver.page_source)
    #             break
    # except Exception as ex:
    #     print(ex)
    # finally:
    #     driver.close()
    #     driver.quit()
#this function takes all the information from each anime by clicking on the link
def get_info():   
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
        
      
    count_anime=0       
    urls= get_urls()
    print("[INFO] Starting download all information")
    #take genre, topics, years and age limit
    for url in urls:
        src = requests.get(url=url,headers=headers)
        count_anime+=1
        soup = BeautifulSoup(src.text,"html.parser")
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
            
            # with open("data.csv","a",newline='') as f:
            #     writer= csv.writer(f)
            #     writer.writerow(
            #         (
            #             all_anime_name[count_anime-1],
            #             all_count_series[count_anime-1],
            #             ",".join(genre),
            #             ",".join(topics if topics!=[] else "-"),
            #             ",".join(years),
            #             old
            #             )
            #     )

            
            with connection.begin() as trans:
                connection.execute("""INSERT INTO anime(anime_name,count_of_series,genre,topics,years,age_limit)
                                    VALUES(%s,%s,%s,%s,%s,%s)
                """,(all_anime_name[count_anime-1],
                    all_count_series[count_anime-1],
                    ",".join(genre),
                    ",".join(topics if topics!=[] else "-"),
                    ",".join(years),
                    old))

            print(f"[INFO] Anime number {count_anime}/{len(all_anime_name)} complited")
        except:
            print(f"[ERROR] Anime number {count_anime}/{len(all_anime_name)}, name {all_anime_name[count_anime-1]}")
        

        



def main():
    get_data()
    get_info()
if __name__=="__main__":
    main()
    finish_time=time.time()-start_time
    print(f"Script running time - {finish_time}")


    

