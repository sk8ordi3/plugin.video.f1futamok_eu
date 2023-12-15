# -*- coding: utf-8 -*-

'''
    F1futamok.eu Addon
    Copyright (C) 2023 heg, vargalex

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os, sys, re, xbmc, xbmcgui, xbmcplugin, xbmcaddon, locale, base64
from bs4 import BeautifulSoup
import requests
import urllib.parse
import resolveurl as urlresolver
from resources.lib.modules.utils import py2_decode, py2_encode
import html
import random

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

version = xbmcaddon.Addon().getAddonInfo('version')
kodi_version = xbmc.getInfoLabel('System.BuildVersion')
base_log_info = f'F1futamok.eu | v{version} | Kodi: {kodi_version[:5]}'

xbmc.log(f'{base_log_info}', xbmc.LOGINFO)

base_url = 'https://f1futamok.eu'

BR_VERS = [
    ['%s.0' % i for i in range(18, 43)],
    ['61.0.3163.79', '61.0.3163.100', '62.0.3202.89', '62.0.3202.94', '63.0.3239.83', '63.0.3239.84', '64.0.3282.186', '65.0.3325.162', '65.0.3325.181', '66.0.3359.117', '66.0.3359.139',
     '67.0.3396.99', '68.0.3440.84', '68.0.3440.106', '68.0.3440.1805', '69.0.3497.100', '70.0.3538.67', '70.0.3538.77', '70.0.3538.110', '70.0.3538.102', '71.0.3578.80', '71.0.3578.98',
     '72.0.3626.109', '72.0.3626.121', '73.0.3683.103', '74.0.3729.131'],
    ['11.0']]
WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1']
FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
            'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
            'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko']

ind_ex = random.randrange(len(RAND_UAS))
r_u_a = RAND_UAS[ind_ex].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES), br_ver=random.choice(BR_VERS[ind_ex]))

headers = {
    'authority': 'f1futamok.eu',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': r_u_a,
}

if sys.version_info[0] == 3:
    from xbmcvfs import translatePath
    from urllib.parse import urlparse, quote_plus
else:
    from xbmc import translatePath
    from urlparse import urlparse
    from urllib import quote_plus

class navigator:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
        except:
            try:
                locale.setlocale(locale.LC_ALL, "")
            except:
                pass
        self.base_path = py2_decode(translatePath(xbmcaddon.Addon().getAddonInfo('profile')))      

    def root(self):
        self.addDirectoryItem("Kategóriák", f"categories&url={base_url}", '', 'DefaultFolder.png')
        self.addDirectoryItem("Keresés", "newsearch", '', 'DefaultFolder.png')
        self.endDirectory()
        
    def getCategorys(self, url):
        import requests
        
        html_source = requests.get(url, headers=headers)
        soup = BeautifulSoup(html_source.text, 'html.parser')
        
        menu_links = soup.select('.sp-megamenu-parent a')
        
        items_dict = {}
        
        for menu_link in menu_links:
            title = menu_link.text.strip()
            href = menu_link['href']
        
            if not title:
                continue
        
            if title in ('Boxutca', 'Egyebek', '1992'):
                items_dict[title] = {'title': title, 'href': f"https://f1futamok.eu{href}"}
            elif '-' in title:
                try:
                    start, end = map(int, title.split(' - '))
                    for year in range(end, start - 1, -1):
                        items_dict[str(year)] = {'title': str(year), 'href': f"https://f1futamok.eu/{year}"}
                    items_dict[title] = {'title': title, 'href': f"https://f1futamok.eu{href}"}
                except ValueError:
                    items_dict[title] = {'title': title, 'href': f"https://f1futamok.eu{href}"}
            else:
                items_dict[title] = {'title': title, 'href': f"https://f1futamok.eu{href}"}
        
        sorted_items = sorted(items_dict.values(), key=lambda x: (int(x['title']) if x['title'].isdigit() else 0, x['title']), reverse=True)
        
        for stuffs in sorted_items:
            cat_title = stuffs['title']
            href = stuffs['href']
            
            self.addDirectoryItem(f'[B]{cat_title}[/B]', f'ext_categs&url={href}', '', 'DefaultMovies.png', isFolder=True, meta={'title': cat_title})

        self.endDirectory()

    def extCatergorys(self, url, image_url, title):
        import requests
        
        html_source = requests.get(url, headers=headers)
        soup = BeautifulSoup(html_source.text, 'html.parser')

        item_containers = soup.find_all('div', class_='catItemView')

        for container in item_containers:
            title = container.find('h3', class_='catItemTitle').text.strip()

            try:
                image = container.find('img')['src']
                image_url = f'{base_url}{image}'
            except (TypeError, KeyError):
                image_url = ''

            link = container.find('a', class_='k2ReadMore')['href']
            href_link = f'{base_url}{link}'

            self.addDirectoryItem(f'[B]{title}[/B]', f'ext_video&url={href_link}&image_url={image_url}&title={title}', image_url, 'DefaultMovies.png', isFolder=True, meta={'title': title})     

        pagination_list = soup.find('ul', class_='pagination')

        if pagination_list:
            next_page_element = pagination_list.find('a', {'title': 'Tovább'})
        
            if next_page_element:
                next_page = next_page_element['href']
                next_page_link = f'https://f1futamok.eu{next_page}'
                self.addDirectoryItem('[I]Következő oldal[/I]', f'ext_categs&url={quote_plus(next_page_link)}', '', 'DefaultFolder.png')
        
        self.endDirectory()


    def extVideo(self, url, image_url, title):
        import requests
        from urllib.parse import urlparse, urlunparse
        import re
        
        html_source = requests.get(url, headers=headers)
        soup = BeautifulSoup(html_source.text, 'html.parser')
        
        try:
            iframe_tag = soup.find('iframe')
            src_attribute = iframe_tag['src']
            
            if src_attribute.startswith('//'):
                iframe_link = 'https:' + src_attribute
                
            self.addDirectoryItem(f'[B]{title}[/B]', f'play_movie&url={quote_plus(iframe_link)}&image_url={image_url}&title={title}', image_url, 'DefaultMovies.png', isFolder=False, meta={'title': title})
        except:        
            try:
                redcat_link = re.findall(r'\"(https.*redcat.hu/.*php.*?)\"', str(soup))[0].strip()  
                
                import requests
                
                headers_x = {
                    'authority': 'redcat.hu',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'referer': 'https://srzt.eu/',
                    'user-agent': r_u_a,
                }
                
                resp = requests.get(redcat_link, headers=headers_x).text
                
                def normalize_url(url_x):
                    parsed_url = urlparse(url_x)
                    if not parsed_url.scheme or parsed_url.scheme == "//":
                        scheme = "https"
                    else:
                        scheme = parsed_url.scheme
                    normalized_url = urlunparse((scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment))
                    return normalized_url
                
                iframe_link = re.findall(r'iframe.*?"(.*?)"', resp, flags=re.IGNORECASE)[0].strip()
                iframe_link = normalize_url(iframe_link)
                
                self.addDirectoryItem(f'[B]{title}[/B]', f'play_movie&url={quote_plus(iframe_link)}&image_url={image_url}&title={title}', image_url, 'DefaultMovies.png', isFolder=False, meta={'title': title})
            except:
                xbmc.log(f'{base_log_info}| playMovie | name: No video sources found', xbmc.LOGINFO)
                notification = xbmcgui.Dialog()
                notification.notification("F1futamok.eu", "Törölt tartalom", time=5000)
        
        self.endDirectory()

    def playMovie(self, url):
        try:
            direct_url = urlresolver.resolve(url)
            xbmc.log(f'{base_log_info}| playMovie | direct_url: {direct_url}', xbmc.LOGINFO)
            play_item = xbmcgui.ListItem(path=direct_url)
            if 'm3u8' in direct_url:
                from inputstreamhelper import Helper
                is_helper = Helper('hls')
                if is_helper.check_inputstream():
                    play_item.setProperty('inputstream', 'inputstream.adaptive')  # compatible with recent builds Kodi 19 API
                    play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)
        except:
            xbmc.log(f'{base_log_info}| playMovie | name: No video sources found', xbmc.LOGINFO)
            notification = xbmcgui.Dialog()
            notification.notification("F1futamok.eu", "Törölt tartalom", time=5000)

    def doSearch(self, url):
        search_text = self.getSearchText()
        
        from bs4 import BeautifulSoup
        import requests
        
        params = {
            'searchword': search_text,
            'ordering': 'newest',
            'searchphrase': 'exact',
        }
        
        html_source = requests.get('https://f1futamok.eu/component/search/', params=params, headers=headers)
        soup = BeautifulSoup(html_source.text, 'html.parser')
        
        entries = soup.find_all('dt', class_='result-title')
        
        for entry in entries:
            title_tag = entry.find('a')
            href = title_tag.get('href')
            href_link = f'https://f1futamok.eu{href}'
            
            title = ' '.join(title_tag.stripped_strings)

            self.addDirectoryItem(title, f'ext_video&url={href_link}&title={title}', '', 'DefaultFolder.png')
        
        self.endDirectory()

    def getSearchText(self):
        search_text = ''
        keyb = xbmc.Keyboard('', u'Add meg a keresend\xF5 film c\xEDm\xE9t')
        keyb.doModal()
        if keyb.isConfirmed():
            search_text = keyb.getText()
        return search_text

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None, banner=None):
        url = f'{sysaddon}?action={query}' if isAction else query
        if thumb == '':
            thumb = icon
        cm = []
        if queue:
            cm.append((queueMenu, f'RunPlugin({sysaddon}?action=queueItem)'))
        if not context is None:
            cm.append((context[0].encode('utf-8'), f'RunPlugin({sysaddon}?action={context[1]})'))
        item = xbmcgui.ListItem(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'banner': banner})
        if Fanart is None:
            Fanart = addonFanart
        item.setProperty('Fanart_Image', Fanart)
        if not isFolder:
            item.setProperty('IsPlayable', 'true')
        if not meta is None:
            item.setInfo(type='Video', infoLabels=meta)
        xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def endDirectory(self, type='addons'):
        xbmcplugin.setContent(syshandle, type)
        xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)  