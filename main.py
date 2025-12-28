from bs4 import BeautifulSoup
import requests
import os
import sys

# Function to download files
# stolen from https://www.geeksforgeeks.org/python/how-to-download-an-image-from-a-url-in-python/
def download_file(file_url, directory):
     try:
         response = requests.get(file_url)
         response.raise_for_status()  # Check for request errors
         file_name = os.path.basename(file_url)
         file_path = os.path.join(directory, file_name)
         with open(file_path, 'wb') as file:
             file.write(response.content)
         print(f"Downloaded: {file_url}")
     except requests.RequestException as e:
         print(f"Error downloading {file_url}: {e}")

def getUserInfo (usernumber):
    url = "https://dad.gallery/users/" + str(usernumber) + "/submissions"
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    #retrieve username
    try:
        imgurl = soup.find('img', {"class": "submissionThumbnail"})['src']
    except:
        print("User not found. Exiting.")
        exit(0)
    ind = str(imgurl).find("submissions/")
    ind2 = str(imgurl).find("/drawing")
    username = str(imgurl)[ind+12:ind2]

    #retrieve pagecount
    pagenav = soup.find('a', {"class": "next_page"})
    if (pagenav == None):
        pagecount = 1
    else:
        pagecount = int(str(pagenav.previous_sibling.previous_sibling.contents)[2:-2])

    return (username, pagecount)

def downloadPage (usernumber, username, pagenumber):
    url = "https://dad.gallery/users/" + str(usernumber) + "/submissions?page="
    response = requests.get(url+str(pagenumber))
    html_content = response.text

    # Save page listing, unnecessary
    with open('archive/' + username + '/files/page' + str(pagenumber) + '.html', 'w', encoding='utf-8') as file:
        file.write(html_content)
        file.close()

    soup = BeautifulSoup(html_content, 'html.parser')

    # cannot manipulate thumbnail links due to content filter thumbnails
    for img in soup.find_all('img', {"class": "submissionThumbnail"}):
        suburl = "https://dad.gallery" + img['data-details']
        response = requests.get(suburl)
        html_content = response.text
        with open('archive/' + username + '/files/sub' + str(img['data-details'][13:]) + '.html', 'w', encoding='utf-8') as subfile:
            subfile.write(html_content)

        subSoup = BeautifulSoup(html_content, 'html.parser')

        subNumber = img['data-details'][13:]

        userCard = subSoup.find(attrs={'class':'col-lg-2'}).find(attrs={'class':'card-body'})
        ind = str(userCard.contents).find("Content Level: ")
        rating = str(userCard.contents)[ind+15]

        subImg = subSoup.find(id="submissionImage").get('src')
        ind = str(subImg).find(subNumber)
        filename = str(subImg)[ind+len(subNumber)+1:]
        #print("Downloading submission: " + subNumber + '_' + filename)

        saveLocationFolder = 'archive/' + username + '/img/'
        if (rating[0] == 'E'):
            saveLocationFolder = saveLocationFolder + 'explicit/'
        saveLocation = saveLocationFolder + subNumber + '_' + filename

        print("File: " + subNumber + '_' + filename)

        # This script runs newest submission to oldest.
        # I'm going to assume that if you hit a repeat file,
        # you have them all and we're not going to waste our time with the rest.
        if (os.path.exists(saveLocation)):
            print("Repeat submission " + subNumber + ". Exiting.")
            exit()

        imgData = requests.get(subImg).content
        imageFile = open(saveLocation, 'wb')
        imageFile.write(imgData)
        imageFile.close()

def main():
    try: 
        usernumber = int(sys.argv[1])
    except:
        usernumber = 13688
    print(usernumber)
    
    username, pagecount = getUserInfo(usernumber)
    print("Downloading " + str(pagecount) + " pages of submissions from user " + username)

    os.makedirs('archive', exist_ok=True)
    os.makedirs('archive/' + username, exist_ok=True)
    os.makedirs('archive/' + username + '/files', exist_ok=True)
    os.makedirs('archive/' + username + '/img', exist_ok=True)
    os.makedirs('archive/' + username + '/img/explicit', exist_ok=True)

    for i in range(1,pagecount+1):
        print("Downloading page " + str(i) + " of " + str(pagecount))
        downloadPage(usernumber, username, i)

if __name__ == "__main__":
    main()