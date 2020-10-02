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
korean = re.compile('[가-힣]+')


###유투버 동영상 URL크롤링
def get_URL(creater, work):
    if work == 'want':
        driver = webdriver.Chrome(os.path.join(dirr, 'chromedriver.exe'))
    elif work == "not want":
        driver = webdriver.Chrome(os.path.join(dirr, 'chromedriver.exe',chrome_options=options))
    
    #크롤링할 유튜버의 계정
    videos_url = 'https://www.youtube.com/{}/videos'.format(creater)
    driver.get(videos_url)
    
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
    return video_url_list


###댓글 크롤링
def get_comments(url_list, work):
    if work == 'want':
        driver = webdriver.Chrome(os.path.join(dirr, 'chromedriver.exe'))
    elif work == "not want":
        driver = webdriver.Chrome(os.path.join(dirr, 'chromedriver.exe',chrome_options=options))
    
    global videos_dic
    videos_dic={}
    
    #url_list의 하나하나의 url에 들어감
    for video in url_list:
        video_url = 'https://www.youtube.com{}'.format(video)
        driver.get(video_url)
        last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
        
        #스크롤 맨 밑까지 내리기
        while True:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);") 
            time.sleep(2.0) 
            new_page_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_page_height == last_page_height: 
                break
            last_page_height = new_page_height
            
        #해당 URL의 제목, 댓글, 좋아요개수, 닉네임 크롤링
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        title = soup.find('yt-formatted-string',{'class': 'style-scope ytd-video-primary-info-renderer'}).text
        comments = soup.find_all('yt-formatted-string',{'id':'content-text'})
        one_video_dic={}
        for comment in range(1,len(comments)+1):
            nickname=driver.find_element(By.XPATH,'/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/ytd-comments/ytd-item-section-renderer/div[3]/ytd-comment-thread-renderer[{}]/ytd-comment-renderer/div[1]/div[2]/div[1]/div[2]/a/span'.format(comment)).text
            like = driver.find_element(By.XPATH,'/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/ytd-comments/ytd-item-section-renderer/div[3]/ytd-comment-thread-renderer[{}]/ytd-comment-renderer/div[1]/div[2]/ytd-comment-action-buttons-renderer/div[1]/span[2]'.format(comment)).text
            n_comment=driver.find_element(By.XPATH,'/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/ytd-comments/ytd-item-section-renderer/div[3]/ytd-comment-thread-renderer[{}]/ytd-comment-renderer/div[1]/div[2]/ytd-expander/div/yt-formatted-string[2]'.format(comment)).text
            #re 정규식을 이용하여 온전한 한국어만 크롤링
            one_video_dic[nickname]=[' '.join(korean.findall(n_comment)),like]
        videos_dic[' '.join(korean.findall(title))]=one_video_dic
    return videos_dic
        
        
#url_list=get_URL('channel/UCmRiRqCH-QMlHIX90t9v6Yw', 'want')
videos_dic=get_comments(['/watch?v=STNlCT9bVrE'], 'want')
dd =  pd.DataFrame(videos_dic)





