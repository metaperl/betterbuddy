#!/usr/bin/python

# system
from collections import defaultdict
from functools import wraps
import pdb
import pprint
import re
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
    auctions = 'auctions'
)

def url_for_action(action):
    return "{0}/{1}".format(base_url,action_path[action])

def try_method(fn):
    @wraps(fn)
    def wrapper(self):
        try:
            return fn(self)
        except:
            print traceback.format_exc()
            self.visit_auction()

    return wrapper


class Entry(object):

    def __init__(self, user, browser, url):
        self.user=user
        self.browser=browser
        self.url=url

    @try_method
    def find_bid_button(self):
        self.bid_button = self.browser.find_by_xpath('//a[@class="bid-button-link button-small"]')

    def item_price(self):
        price = self.browser.find_by_xpath('//*[@class="bid-price"]')
        return float(price.value[1::])


    @try_method
    def click_bid_button(self):
        self.bid_button.click()
        print "\tClicked."
        time.sleep(1)

    def login(self):
        print "Logging in..."
        self.browser.visit(url_for_action('login'))
        self.browser.fill('data[User][username]', self.user['username'])
        self.browser.fill('data[User][password]', self.user['password'])
        button = self.browser.find_by_id('log_submit')
        button.click()


    @try_method
    def execute_click(self):
        self.find_bid_button()
        self.click_bid_button()
        self.report_results()

    def report_results(self):
        self.bids_at_finish = self.bids_left()
        diff = self.bids_at_start - self.bids_at_finish
        bid_cost = diff * 0.50
        total_cost = bid_cost + self.item_price()
        print "\tBids used: {0}. Bid Cost at .50/bid = {1}. Total cost = {2}".format(diff, bid_cost, total_cost)

    def check_for_click(self):
        #self.countdown() <= 2 would be a neat test, but the DOM is
        # too freaky around this time to be playing games and you
        # have to get a click in at all costs.

        # it would be nice to not waste a click if someone else clicks
        # in the same few milliseconds but that is not possible
        # given the speed of DOM lookups, etc
        return True

    def chosen_auction(self):
        u = self.browser.url
        print "\tCurrent browser url=", u
        if re.search('\d+$', u):
            print "Chosen auction", u
            return u
        else:
            time.sleep(5)
            print "\t\tStill waiting for auction to be chosen"
            return self.chosen_auction()

    def wait_for_auction_choice(self):
        self.browser.visit(url_for_action('auctions'))
        return self.chosen_auction()



    def visit_auction(self):

        if not self.url:
            print "Must wait for user to choose auction."
            self.url = self.wait_for_auction_choice()

        print "Visiting", self.url
        self.browser.visit(self.url)


        self.bids_at_start = self.bids_left()

        print "--------------------------------------------------------"
        print "Begin auction with {0} bids".format(self.bids_at_start)


        while True:
            c = self.countdown()
            print "Seconds remaining = {0}".format(c)
            if c is None:
                self.report_results()
                break
            elif c == 1 or c == 2:
                if self.check_for_click():
                    self.execute_click()
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
            return 0.1
        else:
            return s - 4

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

    @try_method
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

    if len(sys.argv) == 2:
        bid_url = sys.argv[1]
    else:
        bid_url = None
    main(bid_url)
