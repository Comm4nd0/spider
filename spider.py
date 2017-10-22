#!/usr/bin/env python3

import argparse
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import validators
import tldextract
import os
import re

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
    def __init__(self, url, key):
        self.url = url
        self.key = key
        self.url_domain = ''
        self.url_suffix = ''
        self.current_domain = []
        self.checked = []
        self.urls_found = 0
        self.data = ''

    def get_url(self):
        # set the global domain and suffix
        extracted = tldextract.extract(self.url)
        self.url_domain = extracted.domain
        self.url_suffix = extracted.suffix

        if self.validate_url(self.url):
            self.get_html(self.url)
        else:
            print(Colours.FAIL + "Invalid URL - Example: http://reddit.com" + Colours.ENDC)
            exit()

    def validate_url(self, url):
        return validators.url(url, public=True)

    def get_html(self, url):
        self.stats(url)
        res = self.validate_url(url)
        if res == True:
            try:
                request = urllib.request.urlopen(url)
                soup = BeautifulSoup(request, "lxml")
                self.search(url, soup)
                self.get_urls(soup)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as error:
                print(error)

        for item in self.current_domain:
            if item == url:
                try:
                    self.checked.append(url)
                    self.current_domain.remove(url)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception as error:
                    print(error)

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
        for url in self.current_domain:
            if url not in self.checked:
                self.urls_found += 1
                self.get_html(url)
            else:
                self.current_domain.remove(url)

    def search(self, url, soup):
        if soup.find_all(string=re.compile(self.key)):
            self.data += url + '\n'

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
    args = parser.parse_args()

    if not args.url:
        print(Colours.FAIL + "Missing URL - Example: --url http://cia.com" + Colours.ENDC)
        exit()
    else:
        url = args.url

    if not args.search:
        print(Colours.FAIL + "Missing search string - Example: --search \"aliens exist!\"" + Colours.ENDC)
        exit()
    else:
        key = args.search

    return url, key

if __name__ == "__main__":
    url, key = args()
    web = Spider(url, key).get_url()