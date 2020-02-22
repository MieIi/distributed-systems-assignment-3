"""
Antti Vilkman
0521281
CT30A3401 Distributed Systems
Wikipedia Shortest Path


forked from https://github.com/ian-henderson/Wikipedia-Game
"""

import os
import sys
import wikipedia
import threading
import time
import requests


lock = threading.Lock()

def print_path(data):
    if data['parent']:
        print_path(data['parent'])
        print(' => ', end='')
    print(data['title'], end='')


def get_page(selection):
    page = None
    while not page:
        try:
            entry = input('%s page title: ' % selection)
            page = wikipedia.page(entry)
        except wikipedia.exceptions.DisambiguationError as e:
            print('\nDisambiguation Selection (Choose one of these or use another term)')
            for option in e.options:
                print('\t' + option)
            print()
        except wikipedia.exceptions.PageError as e:
            print('Page error, try again.')
        except KeyboardInterrupt:
            print('Exiting')
            sys.exit()
    return page



def crawl_page(current, Q, G, target_page):
    try:
        locs = threading.local()
        # Get current page, check if target is among the links in the page
        locs.current_page = wikipedia.page(current['title'])
        for link in locs.current_page.links:
            lock.acquire()
            if link not in G:
                G[link] = {
                    'title': link,
                    'distance': current['distance'] + 1,
                    'parent': current
                }
                print('\t%s %d' % (G[link]['title'], G[link]['distance']))
                if link == target_page.title:
                    print('\n%s found!' % link)
                    print('Path: ', end='')
                    print_path(G[link])
                    print()
                    #input("aff: ")
                    os._exit(1)
                    lock.release()
                Q.append(G[link])
            lock.release()
    except wikipedia.exceptions.DisambiguationError as e:
        G[e.title] = {
            'title': e.title,
            'distance': current['distance'] + 1,
            'parent': current
        }
        # In case of disambiguation page, add every link to queue
        for option in e.options:
            if option not in G:
                G[option] = {
                    'title': option,
                    'distance': current['distance'] + 2,
                    'parent': G[e.title]
                }
                if option == target_page.title:
                    print('\n%s found!' % option)
                    print('Path: ', end='')
                    print_path(G[option])
                    print()
                    os._exit(1)
                    lock.release()
                Q.append(G[option])
    except wikipedia.exceptions.PageError as e:
        # Skips over the item in the queue if it results in a page error.
        print('\tSkipping %s...\n\t\t%s' % (current['title'], e))
    except KeyboardInterrupt:
        print('Exiting')
        sys.exit()
    except requests.exceptions.ConnectionError:
        time.sleep(1)



# Clears up the screen
os.system('cls' if os.name == 'nt' else 'clear')
# Get the initial page and target
root_page = get_page('Start')
target_page = get_page('Target')

# List of crawled pages
G = {}
G[root_page.title] = {
    'title': root_page.title,
    'distance': 0,
    'parent': None
}
# Queue of pages to crawl
Q = []
Q.append(G[root_page.title])
while Q:
    workers = []
    for current in Q:
        workers.append(threading.Thread(target=crawl_page, args=(current, Q, G, target_page)))
    for w in workers:
        w.start()
        w.join()
        
    for obj in Q:
        if G[obj['title']]:
            #print(obj['title'] + "already searched!")
            Q.remove(obj)




