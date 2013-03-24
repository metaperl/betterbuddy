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


class Entry(object):

    def __init__(self, user, browser, url):
        self.user=user
        self.browser=browser
        self.url=url

    def find_bid_button(self):
        self.bid_button = self.browser.find_by_xpath('//a[@class="bid-button-link button-small"]')

    def item_price(self):
        price = self.browser.find_by_xpath('//*[@class="bid-price"]')
        return float(price.value[1::])


    def click_bid_button(self):
        try:
            self.bid_button.click()
        except:
            print traceback.format_exc()
        print "\tClicked."

    def login(self):
        self.browser.visit(url_for_action('login'))
        self.browser.fill('data[User][username]', self.user['username'])
        self.browser.fill('data[User][password]', self.user['password'])
        button = self.browser.find_by_id('log_submit')
        button.click()

    def report_results(self):
        self.bids_at_finish = self.bids_left()
        diff = self.bids_at_start - self.bids_at_finish
        bid_cost = diff * 0.50
        total_cost = bid_cost + self.item_price()
        print "\tBids used: {0}. Bid Cost at .50/bid = {1}. Total cost = {2}".format(diff, bid_cost, total_cost)


    def visit_auction(self):
        self.bids_at_start = self.bids_left()
        print "--------------------------------------------------------"
        print "Begin auction with {0} bids".format(self.bids_at_start)
        self.browser.visit(self.url)
        #pdb.set_trace()

        self.at1 = 0
        self.find_bid_button()
        while True:
            c = self.countdown()
            print "{0} seconds left in auction".format(c)
            if c is None:
                self.report_results()
                break
            elif c <= 2:
                self.click_bid_button()
                self.find_bid_button()
                self.report_results()
                time.sleep(1)
                continue


            sleep_time = self.sleep_time(c)
            print "\tSleeping for", sleep_time, "seconds"
            time.sleep(sleep_time)


    def sleep_time(self, s):
        if s <= 1:
            return 0
        elif s == 2:
            return 0
        elif s == 3 or s == 4:
            return 1
        else:
            return s - 3

    def bids_left(self):
        div = self.browser.find_by_xpath('//*[@class="bid-balance"]')
        #pdb.set_trace()
        return int(div.value)


    def countdown_div_value(self):
        countdown_div = self.browser.find_by_xpath(
            '//div[@class="timer countdown"]'
        )
        v = countdown_div.value.split(':')
        if "--" in v: # timer has not printed to screen
            return self.countdown_div_value()
        elif "Ended" in v:
            print "Auction ended."
            return None
        else:
            return v

    def countdown(self):
        c = self.countdown_div_value()
        if c is None:
            return None

        (h,m,s) = [int(v) for v in c]
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
