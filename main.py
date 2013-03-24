#!/usr/bin/python

# system
from collections import defaultdict
import pdb
import pprint
import sys
import time
import traceback

# pypi
from splinter import Browser

# local
import user as userdata


pp = pprint.PrettyPrinter(indent=4)

base_url = 'http://www.btgpennyauctions.com'
action_path = dict(
    login = "",
    buy_shares = 'index.php?p=buy_shares'
)

def url_for_action(action):
    return "{0}/{1}".format(base_url,action_path[action])

pay_via = dict(
    stp='1',
    pm='5',
    lr='6',
    egopay='10'
)

class Entry(object):

    def __init__(self, user, browser, url):
        self.user=user
        self.browser=browser
        self.url=url

    def find_bid_button(self):
        self.bid_button = self.browser.find_by_xpath('//a[@class="bid-button-link button-small"]')

    def click_bid_button(self):
        try:
            self.bid_button.click()
        except:
            print traceback.format_exc()
        print "\t\t\tClicked."
        time.sleep(5)

    def login(self):
        self.browser.visit(url_for_action('login'))
        self.browser.fill('data[User][username]', self.user['username'])
        self.browser.fill('data[User][password]', self.user['password'])
        button = self.browser.find_by_id('log_submit')
        button.click()

    def visit_auction(self):
        self.browser.visit(self.url)
        self.at1 = 0
        self.find_bid_button()
        while True:
            c = self.countdown()
            print c, "Seconds left in auction"
            if c == 2:
                self.click_bid_button()
                self.find_bid_button()

            sleep_time = self.sleep_time(c)
            print "\tSleeping for", sleep_time, "seconds"
            time.sleep(sleep_time)


    def sleep_time(self, s):
        if s <= 1:
            return 0.01
        elif s == 2:
            return 0.01
        else:
            return s - 2


    def countdown_div_value(self):
        countdown_div = self.browser.find_by_xpath(
            '//div[@class="timer countdown"]'
        )
        v = countdown_div.value.split(':')
        if "--" in v: # timer has not printed to screen
            return self.countdown_div_value()
        elif "Ended" in v:
            print "Auction ended."
            time.sleep(600)
        else:
            return v

    def countdown(self):
        (h,m,s) = [int(v) for v in self.countdown_div_value()]
        return h*60*60 + m*60 + s


def main(bid_url=None):
    with Browser() as browser:

        for user in userdata.users:
            e = Entry(user, browser, bid_url)
            e.login()
            e.visit_auction()
            time.sleep(600)

if __name__ == '__main__':
    main(sys.argv[1])
