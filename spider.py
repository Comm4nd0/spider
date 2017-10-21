#!/usr/bin/env python3

import argparse
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import validators
import tldextract
import os
import re

class colours():
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class spider():
    def __init__(self):
        self.URL_DOMAIN = ''
        self.URL_SUFFIX = ''
        self.CURRENT_DOMAIN = []
        self.CHECKED = []
        self.URLS_FOUND = 0
        self.DATA = ''

        self.get_url()

    def get_url(self):
        parser = argparse.ArgumentParser(description='Search an entire domain for something!')
        parser.add_argument('--url')
        parser.add_argument('--search', help='Enter key word(s)')
        args = parser.parse_args()
        url = args.url
        self.KEY = args.search

        extracted = tldextract.extract(url)
        self.URL_DOMAIN = extracted.domain
        self.URL_SUFFIX = extracted.suffix

        res = self.validate_url(url)
        if res:
            self.get_html(url)
        else:
            print(colours.FAIL + "Invalid URL - Example: http://reddit.com" + colours.ENDC)
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

        for item in self.CURRENT_DOMAIN:
            if item == url:
                try:
                    self.CHECKED.append(url)
                    self.CURRENT_DOMAIN.remove(url)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception as error:
                    print(error)

        self.loop_through_urls()

    def get_urls(self, soup):
        for link in soup.find_all('a', href=True):
            self.URLS_FOUND += 1
            res = self.validate_url(link['href'])
            extracted = tldextract.extract(link['href'])
            if res == True:
                if link['href'] not in self.CURRENT_DOMAIN and link['href'][-1:] != '#':
                    if extracted.domain == self.URL_DOMAIN and extracted.suffix == self.URL_SUFFIX:
                        self.CURRENT_DOMAIN.append(link['href'])
                else:
                    # might have a hash on the end, i.e. dead link!
                    pass
            elif extracted.domain == '' and extracted.suffix == '' and link['href'][-1:] != '#':
                self.CURRENT_DOMAIN.append('http://' + self.URL_DOMAIN + '.' + self.URL_SUFFIX + link['href'])

    def loop_through_urls(self):
        for url in self.CURRENT_DOMAIN:
            if url not in self.CHECKED:
                self.URLS_FOUND += 1
                self.get_html(url)
            else:
                self.CURRENT_DOMAIN.remove(url)

    def search(self, url, soup):
        if soup.find_all(string=re.compile(self.KEY)):
            self.DATA += url + '\n'

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
        -hrr-     ';              ,;'          
                    "'           '"            
                      '


        """)
        print(colours.HEADER + "##### Welcome to the spider #####" + colours.ENDC)
        print(colours.OKGREEN + "+-------------------------------------------------+" + colours.ENDC)
        print(colours.OKBLUE + "Total URL's: " + colours.ENDC + str(self.URLS_FOUND))
        print(colours.OKBLUE + "Current URL: " + colours.ENDC + url)
        print(colours.OKBLUE + "Unique URL's scanned: " + colours.ENDC + str(len(self.CHECKED)))
        print(colours.OKBLUE + "Search key: " + colours.ENDC + self.KEY)
        print(colours.OKBLUE + "Positive results: " + colours.ENDC + str(len(self.DATA.split('\n'))-1))
        print(colours.OKGREEN + "+-------------------------------------------------+" + colours.ENDC)
        print(self.DATA)

if __name__ == "__main__":
    spider()