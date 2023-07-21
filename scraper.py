# Importing the required libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from bs4 import BeautifulSoup
import pandas as pd


# Handling the cookies pop-up if it appears
def pass_cookies_page():
    try:
        cookies_button_xpath = "//button[@aria-label='Reject all']"
        cookies_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
                        (By.XPATH, cookies_button_xpath)))
        cookies_button = driver.find_element(By.XPATH, cookies_button_xpath)
        cookies_button.click()
    except Exception as e:
        print('An error has occurred: ', e)

# Scrolling down the webpage to load more videos
def scroll_down(no_of_videos):
    for i in range(no_of_videos // 28 + 1):  # Scrolling down in batches of 28 videos per scroll
        time.sleep(3)  # Wait for the page to load
        print('Scrolling down...')
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)  # Scroll down using END key

# Converting views from string format to numeric format
def convert_views(df):
    if 'K' in df['VIEWS']:
        views = float(df['VIEWS'].split('K')[0]) * 1000
        return views
    elif 'M' in df['VIEWS']:
        views = float(df['VIEWS'].split('M')[0]) * 1000000
        return views
    views = df['VIEWS'].split(' ')[0]
    return views

def create_df(master_list, df_name):
    # Create a pandas DataFrame from the collected video data
    youtube_df = pd.DataFrame(master_list)
    
    # Apply the 'convert_views' function to the 'VIEWS' column of the DataFrame and store the result in a new 'CLEAN VIEWS' column
    youtube_df['CLEAN VIEWS'] = youtube_df.apply(convert_views, axis=1).astype(int)
    youtube_df.to_csv(df_name, index=False)



if __name__ == '__main__':
    # Ask the user to input the link of the YouTube channel videos they want to scrape
    youtube_link = input("Enter the link to the channel videos you want to scrape (e.g.: https://www.youtube.com/@PewDiePie/videos): ")
    # Ask the user to input a name for the database file and save the DataFrame as a CSV file
    df_name = input("Enter a name for the database file (e.g.: pewdiepie.csv): ")
    # Ask the user to input the number of videos they want to scrape
    no_of_videos = int(input("Enter the number of videos you want to scrape: "))

    # Initializing the Firefox webdriver
    driver = webdriver.Firefox()
    driver.get(youtube_link)

    # Pass the cookies pop-up if it appears
    pass_cookies_page()

    # Scroll down the webpage to load more videos
    scroll_down(no_of_videos)

    # Get the page source and parse it with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Find all video elements on the page
    videos = soup.find_all('div', {'id': 'dismissible'})

    # Initialize an empty list to store the video data
    master_list = []

    # Loop through the video elements and extract the relevant information
    for video in videos:
        if no_of_videos != 0:
            video_data_dict = {}
            video_data_dict['TITLE'] = video.find('a', {'id': 'video-title-link'}).text
            video_data_dict['URL'] = 'https://www.youtube.com/' + video.find('a', {'id': 'video-title-link'})['href']
            meta = video.find_all('span', {'class': 'inline-metadata-item style-scope ytd-video-meta-block'})
            video_data_dict['VIEWS'] = meta[0].text
            video_data_dict['AGE'] = meta[1].text
            master_list.append(video_data_dict)
            no_of_videos -= 1
        else:
            break

    create_df(master_list, df_name)
    print('The database file has been created successfully!')
