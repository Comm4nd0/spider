#!/usr/bin/env python3

try:
    import argparse
    import urllib.request
    import urllib.parse
    #import urllib.urlretrieve
    from bs4 import BeautifulSoup
    import validators
    import tldextract
    import os
    import re
except:
    print("Please make sure you install all libraries listed in requirements.txt")

class Colours:
    # set the values for the colours
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Spider:
    def __init__(self, url, mode, key):
        self.url = url
        self.key = key
        self.url_domain = ''
        self.url_suffix = ''
        self.current_domain = []
        self.checked = []
        self.urls_found = 0
        self.data = ''

        self.mode = getattr(self, mode)


    def get_url(self):
        # set the global domain and suffix
        extracted = tldextract.extract(self.url)
        self.url_domain = extracted.domain
        self.url_suffix = extracted.suffix

        if self.validate_url(self.url):
            self.get_html(self.url)
        else:
            print(Colours.FAIL + "Invalid URL - Example: http://reddit.com" + Colours.ENDC)
            quit()

    def validate_url(self, url):
        return validators.url(url, public=True)

    def get_html(self, url):
        self.stats(url)
        res = self.validate_url(url)
        if res == True:
            try:
                request = urllib.request.urlopen(url)
                soup = BeautifulSoup(request, "lxml")
                self.mode(url, soup)
                self.get_urls(soup)
            except (KeyboardInterrupt, SystemExit):
                quit()

        for item in self.current_domain:
            if item == url:
                try:
                    self.checked.append(url)
                    self.current_domain.remove(url)
                except (KeyboardInterrupt, SystemExit):
                    quit()

        self.loop_through_urls()

    def get_urls(self, soup):
        for link in soup.find_all('a', href=True):
            self.urls_found += 1
            extracted = tldextract.extract(link['href'])
            if self.validate_url(link['href']):
                if link['href'] not in self.current_domain and link['href'][-1:] != '#':
                    if extracted.domain == self.url_domain and extracted.suffix == self.url_suffix:
                        self.current_domain.append(link['href'])
                else:
                    # might have a hash on the end, i.e. dead link!
                    pass
            elif extracted.domain == '' and extracted.suffix == '' and link['href'][-1:] != '#':
                self.current_domain.append('http://' + self.url_domain + '.' + self.url_suffix + link['href'])

    def loop_through_urls(self):
        try:
            for url in self.current_domain:
                if url not in self.checked:
                    self.urls_found += 1
                    self.get_html(url)
                else:
                    self.current_domain.remove(url)
        except (KeyboardInterrupt, SystemExit):
            exit()

    def search(self, url, soup):
        if soup.find_all(string=re.compile(self.key)):
            self.data += url + '\n'

    def img(self,url, soup):
        if not os.path.isdir(os.getcwd() + '/images/'):
            os.makedirs(os.getcwd() + '/images/')
        link = soup.find_all('img')
        for item in link:
            try:
                if self.key in str(item['src']) and not os.path.isfile('images/' + os.path.basename(item['src'])):
                    urllib.request.urlretrieve(item['src'], 'images/' + os.path.basename(item['src']))
                    self.data += 'Downloaded: ' + str(os.path.basename(item['src'])) + '\n'

            except Exception as err:
                try:
                    urllib.request.urlretrieve('http:' + item['src'], 'images/' + os.path.basename(item['src']))
                except:
                    pass
                print(err)
        #self.data += link + '\n'


    def quit(self):
        exit()
    def stats(self, url):
        os.system('clear')
        print("""  
                   ;               ,           
                 ,;                 '.         
                ;:                   :;        
               ::                     ::       
               ::                     ::       
               ':                     :        
                :.                    :        
             ;' ::                   ::  '     
            .'  ';                   ;'  '.    
           ::    :;                 ;:    ::   
           ;      :;.             ,;:     ::   
           :;      :;:           ,;"      ::   
           ::.      ':;  ..,.;  ;:'     ,.;:   
            "'"...   '::,::::: ;:   .;.;""'    
                '"""""""....;\:::::;,;.;""""""         
            .:::.....'"':::::::'",...;::::;.   
           ;:' '""'"";.,;:::::;.'""""""        ':;   
          ::'         ;::;:::;::..         :;  
         ::         ,;:::::::::::;:..       :: 
         ;'     ,;;:;::::::::::::::;";..    ':.
        ::     ;:"  ::::::""""""   '::::::  ":     ::
         :.    ::   ::::::;  :::::::   :     ; 
          ;    ::   :::::::  :::::::   :    ;  
           '   ::   ::::::....:::::'  ,:   '   
            '  ::    :::::::::::::"   ::
               ::     ':::::::::"'    ::       
               ':       """""""'            ::       
                ::                   ;:        
                ':;                 ;:"        
                  ';              ,;'          
                    "'           '"            
                      '

        """)
        print(Colours.HEADER + "##### Welcome to the spider #####" + Colours.ENDC)
        print(Colours.OKGREEN + "+-------------------------------------------------+" + Colours.ENDC)
        print(Colours.OKBLUE + "Total URL's: " + Colours.ENDC + str(self.urls_found))
        print(Colours.OKBLUE + "Current URL: " + Colours.ENDC + url)
        print(Colours.OKBLUE + "Unique URL's scanned: " + Colours.ENDC + str(len(self.checked)))
        print(Colours.OKBLUE + "Search key: " + Colours.ENDC + self.key)
        print(Colours.OKBLUE + "Positive results: " + Colours.ENDC + str(len(self.data.split('\n'))-1))
        print(Colours.OKGREEN + "+-------------------------------------------------+" + Colours.ENDC)
        print(self.data)

def args():
    # handle the args
    parser = argparse.ArgumentParser(description='Search an entire domain for something!')
    parser.add_argument('--url')
    parser.add_argument('--search', help='Enter key word(s)')
    parser.add_argument('--img', help='Enter image name to download')
    args = parser.parse_args()

    if not args.url:
        print(Colours.FAIL + "Missing URL - Example: --url http://cia.com" + Colours.ENDC)
        exit()
    else:
        url = args.url

    if args.search:
        mode = 'search'
        key = args.search
    elif args.img:
        mode = 'img'
        key = args.img
    else:
        print('Check your syntax')

    return url, mode, key

if __name__ == "__main__":
    url, mode, key = args()
    web = Spider(url, mode, key).get_url()