# This is the iterative implementation of the web crawler using BFS

import urllib.request
from bs4 import BeautifulSoup as bs
import os.path
import time
from multiprocessing.dummy import Pool as ThreadPool,  Queue
pool = ThreadPool(8)


htmlSource = os.getcwd() + "/htmlSource/" #directory to store all the html source text files
maxDepth = 3
now = time.time()

class DLink:
    link = ''
    d = 0
    def __init__(self, link, d):
        self.link = link
        self.d = d

class Find:

    def findChildrenIterative(self,link):
        urls = Queue(-1)    #create a queue to store the urls
        urls.put(link)      # put the current link in queue
        crwled = []
        while not urls.empty():
            currLink = urls.pop(0)   # pop out the last element of queue
            crwled = currLink
            if link.d > maxDepth: #Do not expand this link if the current depth is greater than the maxDepth 
                continue

            print("Processing " + currLink.link)
            
            try:
                fileName = htmlSource + currLink.link.replace("/", "_").replace(":", "_")#replace / and : for the filename
                
                siteHtml = urllib.request.urlopen(currLink.link).read()#read the raw HTML into a string
                output = open(fileName + ".txt", "w") #create the file for the raw HTML
                output.write(siteHtml.decode("utf-8")) #write the HTML into a file
                output.flush()
                output.close()

                rawHTML = bs(siteHtml.decode("utf-8"), "html.parser")
                
                for childLink in rawHTML.find_all("a"): #iterate over all the 'a' tags
                    if(childLink not in crwled):
                        if(childLink.get("href") is not None):
                            if "http://" in childLink.get("href"): 
                                urls.put(DLink(childLink.get("href"), link.d + 1))
                            elif childLink.get("href")[0:2] == "//": #checks for a special case)
                                urls.put(DLink("http:" + childLink.get("href"), link.d + 1))
                            elif not "https://" in childLink.get("href"): #another special case
                                l = childLink.get("href")
                                if l[0] == '/':
                                    l = l[1:]
                                urls.put(DLink(currLink[:currLink.rfind('/') + 1] + l, link.d + 1))
            except:
                continue



    def findChildren(self, link, depth): #This will find all child URLS (in 'a' elements) from link
        depth += 1

        if depth > maxDepth: #Do not expand this link if the current depth is greater than the maxDepth 
            return False
        try:
            fileName = htmlSource + link.replace("/", "_").replace(":", "_")#replace / and : for the filename
            #Improvment to check for back edges and not re-expand sites
            if os.path.exists(fileName + ".txt"): 
                print("found file " + fileName + ".txt")
                return True

            print("Processing " + link.link)

            siteHtml = urllib.request.urlopen(link).read()#read the raw HTML into a string
            output = open(fileName + ".txt", "w") #create the file for the raw HTML
            output.write(siteHtml.decode("utf-8")) #write the HTML into a file
            output.flush()
            output.close()

            rawHTML = bs(siteHtml.decode("utf-8"), "html.parser")
            
            for childLink in rawHTML.find_all("a"): #iterate over all the 'a' tags
                if(childLink.get("href") is not None):
                    if "http://" in childLink.get("href"): 
                        self.findChildren(childLink.get("href"), depth)
                    elif childLink.get("href")[0:2] == "//": #checks for a special case
                        self.findChildren("http:" + childLink.get("href"), depth)
                    elif not "https://" in childLink.get("href"): #another special case
                        l = childLink.get("href")
                        if l[0] == '/':
                            l = l[1:]
                        self.findChildren(link[:link.rfind('/') + 1] + l, depth)
        except:
            return False       

    def makeVec(self, fileName): #makes the feature vector from the raw HTML files
        unigram = open(htmlSource + fileName.replace(".txt", ".vec"), 'w')
        counter = [0] * 95
        fileContents = open(htmlSource + fileName, "r").read()
        for char in fileContents:
            if ord(char) > 31 and ord(char) < 127:  #checks for a valid printable ASCII character
                counter[ord(char) - 32 ] += 1 #puts the count of each char in the array

        s = str(counter[0])
        for i in range (1, 94):
            s = s + "," + str(counter[i]) #dump the count into the textfile
        unigram.write(s)
        unigram.flush()
        unigram.close()


if os.path.exists(htmlSource) is False:
    os.makedirs(htmlSource)
f = Find()
f.findChildrenIterative(DLink("http://www.ask.com/", 0))
pool.map(f.makeVec, os.listdir(htmlSource))
pool.close()
pool.join()
print(time.time() - now)