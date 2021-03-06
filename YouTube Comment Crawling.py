# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 23:44:49 2020

@author: SAMSUNG
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from Save_Database import *
import pymysql

import pandas as pd
from bs4 import BeautifulSoup
import os
import time
import re

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument('window-size=1920x1080')
options.add_argument('__log-level=3')
dirr = os.path.dirname(__file__)

#database
uu_db = upload_db()

#re 정규식
korean = re.compile('[가-힣]+')


###유투버 동영상 URL크롤링
def get_URL(creater, work):
    if work == 'want':
        driver = webdriver.Chrome(os.path.join(dirr, 'chromedriver.exe'))
    elif work == "not want":
        driver = webdriver.Chrome(os.path.join(dirr, 'chromedriver.exe'),chrome_options=options)
    videos_url = 'https://www.youtube.com/{}/videos'.format(creater)
    driver.get(videos_url)
    
    #youtuber정보
    youtube_name = driver.find_element(By.XPATH, '/html/body/ytd-app/div/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer/app-header-layout/div/app-header/div[2]/div[2]/div/div[1]/div/div[1]/ytd-channel-name/div/div/yt-formatted-string').text
    try: #구독자 정보 표시 한 경우
        subscriber = driver.find_element(By.XPATH, '/html/body/ytd-app/div/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer/app-header-layout/div/app-header/div[2]/div[2]/div/div[1]/div/div[1]/yt-formatted-string').text.split(' ')[1]
    except:
        subscriber = 'None'
    #유투버 동영상 링크 list
    video_url_list=[]
    
    #스크롤 맨 밑까지 내리기
    last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);") 
        time.sleep(2.0) 
        new_page_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_page_height == last_page_height: 
            break
        last_page_height = new_page_height
    
    #URL요소 찾아서 list에 append
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    videos = soup.find_all('a',{'id': 'thumbnail'})
    for link in videos:
        try:
            video_url_list.append(link['href'])
        except:
            continue
    
    #database에 youtuber정보 입력
    video = len(video_url_list)
    youtuber_col=['youtube_name', 'subscriber', 'video' ]
    youtuber_data = {'youtube_name':[youtube_name], 'subscriber':[subscriber], 'video':[video]}
    youtuber_dataframe=pd.DataFrame(youtuber_data, columns=youtuber_col)
    uu_db.upload_database(youtuber_dataframe,'youtuber')

    driver.close()
    return video_url_list


###댓글 크롤링
def get_comments(url_list, work):
    if work == 'want':
        driver = webdriver.Chrome(os.path.join(dirr, 'chromedriver.exe'))
    elif work == "not want":
        driver = webdriver.Chrome(os.path.join(dirr, 'chromedriver.exe'),chrome_options=options)
    
    #url_list의 하나하나의 url에 들어감
    for video in url_list:
        video_url = 'https://www.youtube.com{}'.format(video)
        driver.get(video_url) 
        time.sleep(6.0)
             
        #댓글 창 로딩
        driver.execute_script("window.scrollTo(0, 400);")
        time.sleep(6.0)
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(6.0)
        
        #page 높이        
        last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
        
        #스크롤 맨 밑까지 내리기
        while True:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);") 
            time.sleep(4.0) 
            new_page_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_page_height == last_page_height: 
                break
            last_page_height = new_page_height
            
        #해당 URL의 제목, 댓글, 좋아요개수, 닉네임 크롤링
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        title = soup.find('yt-formatted-string',{'class': 'style-scope ytd-video-primary-info-renderer'}).text
        
        #video정보 
        video_name = title
        youtube_name = driver.find_element(By.XPATH,'/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[6]/div[3]/ytd-video-secondary-info-renderer/div/div[2]/ytd-video-owner-renderer/div[1]/ytd-channel-name/div/div/yt-formatted-string/a').text
        view_number = driver.find_element(By.XPATH,'/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[5]/div[2]/ytd-video-primary-info-renderer/div/div/div[1]/div[1]/yt-view-count-renderer/span[1]').text
        view_num=''.join(re.findall("\d+",view_number))
        update_date = driver.find_element(By.XPATH,'/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[5]/div[2]/ytd-video-primary-info-renderer/div/div/div[1]/div[2]/yt-formatted-string').text.replace(' ','')
        
        #database에 video정보 입력
        video_col=['video_name', 'youtube_name', 'view_num', 'update_date' ]
        video_data = {'video_name':[video_name], 'youtube_name':[youtube_name], 'view_num':[view_num], 'update_date':[update_date]}
        video_dataframe=pd.DataFrame(video_data, columns=video_col)
        print(video_dataframe)
        uu_db.upload_database(video_dataframe,'videos')
        
        comments = soup.find_all('yt-formatted-string',{'id':'content-text'})
        print('스크롤 내려서 얻은 댓글 개수:',len(comments))
        comments_dic={}
        for comment in range(1,len(comments)+1):
            like = driver.find_element(By.XPATH,'/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/ytd-comments/ytd-item-section-renderer/div[3]/ytd-comment-thread-renderer[{}]/ytd-comment-renderer/div[1]/div[2]/ytd-comment-action-buttons-renderer/div[1]/span[2]'.format(comment)).text
            try:
                #좋아요가 1개 이상인 댓글만 저장
                if int(like) >= 1:
                    #comment 정보 
                    nickname=driver.find_element(By.XPATH,'/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/ytd-comments/ytd-item-section-renderer/div[3]/ytd-comment-thread-renderer[{}]/ytd-comment-renderer/div[1]/div[2]/div[1]/div[2]/a/span'.format(comment)).text
                    n_comment=driver.find_element(By.XPATH,'/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/ytd-comments/ytd-item-section-renderer/div[3]/ytd-comment-thread-renderer[{}]/ytd-comment-renderer/div[1]/div[2]/ytd-expander/div/yt-formatted-string[2]'.format(comment)).text
                    contents = ' '.join(korean.findall(n_comment))
                    if len(contents) >=500:
                        contents = contents[:499]
                    comments_dic[comment]=[nickname, like, contents, video_name]
            except:
                continue
            
        #database에 comment정보 입력
        comments_dataframe=pd.DataFrame(comments_dic).T
        comments_dataframe.columns=['commneter_nickname', 'like_num', 'comment_content', 'video_name']
        print(comments_dataframe.head())
        uu_db.upload_database(comments_dataframe,'comments')
    
        #commnets_no 1부터 정렬
        cpnn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='****', db='youtube_comments')
        curs = cpnn.cursor()
        curs.execute('SET @COUNT = 0;')
        curs.execute('ALTER TABLE comments AUTO_INCREMENT = 1;')
        curs.execute('UPDATE comments SET commnets_no = @COUNT:=@COUNT+1;')
        cpnn.commit()
        cpnn.close()

    driver.close()
        
url_list=get_URL('user/hyeyounga', 'want')
get_comments(url_list, 'want')



