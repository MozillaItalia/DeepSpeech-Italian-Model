import requests
import urllib2
import time
from bs4 import BeautifulSoup

urls = open( './books_list.txt', 'r' ).read().splitlines()
text = ''

for url in urls:
    response = requests.get( url )
    soup = BeautifulSoup( response.text.encode( 'utf-8' ), 'html.parser' )
    p_list = soup.findAll( 'p' )

    for p in p_list:
        line = p.get_text()
        if '*** END OF THIS PROJECT GUTENBERG EBOOK' in line:
            break
        elif '***' not in line and 'Project Gutenberg' not in line and \
             'http://www.pgdp.net' not in line and 'EBook' not in line:
            text += line

result = open( 'result.txt', 'w' )
result.write( text.encode( 'utf-8' ) )
result.close()
