#!/usr/bin/env python

import sys
import csv
import time
import re
import datetime
import glob

translation_list = {}

class Transaction:
    def __init__(self, date, desc, eff_date = None):
        self.date = date
        self.desc = desc
        self.eff_date = eff_date
        self.accounts = [Account() for i in range(20)]

        while '  ' in self.desc:
            self.desc = self.desc.replace('  ', ' ').strip()

        self.desc, self.account = translate(self.desc)

        num = self.desc.rsplit(None, 1)[-1]
        if num.isdigit():
            self.desc = "(#%s) %s" % (num, self.desc[:-len(num)-1])

        if self.eff_date and self.date.tm_year == 1900:
            date_str = "-%s" % time.strftime("%m-%d", self.date)
            year = self.eff_date.tm_year
            if int(self.eff_date.tm_yday) < int(self.date.tm_yday):
                year -= 1
            self.date = time.strptime(str(year)+date_str, '%Y-%m-%d')

    def add_line(self, account, value):
        id = 0
        for i in range(0, 20):
            if not self.accounts[i].value:
                id = i
                break
        self.accounts[i].name = account
        self.accounts[i].value = value

    def __str__(self):
        output = "\n%s" % time.strftime("%Y-%m-%d", self.date)

        if self.eff_date and self.date != self.eff_date:
            output += "=%s" % time.strftime("%Y-%m-%d", self.eff_date)

        output +=" %s" % self.desc

        for i in range(0, 20):
            acc = self.accounts[i]
            if acc.value:
                output += "\n\t%-30s" % acc.name
                output += "%14.2f %s" % (acc.value, acc.currency)

        output += "\n\t%s" % self.account
        return output

class Account:
    def __init__(self, name = "Unidentified", value = 0, currency = "BRL"):
        self.name = name
        self.value = value
        self.currency = currency

    def __str__(self):
        return "%s     %d %s" % (self.name, self.value, self.currency)


def load_list_csv():
    f = open("list.csv", 'rt')
    try:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            translation_list[row[0]] = [ row[1], row[2] ]
    finally:
        f.close()

def translate(entry):
    inbox = "Unidentified"
    for item in translation_list:
        if item not in entry:
            continue
        if translation_list[item][0]:
            entry = entry.replace(item, translation_list[item][0]).strip()
        if translation_list[item][1]:
            inbox = translation_list[item][1].strip()
    return entry, inbox

def itau(f):
    for line in f:
        line_split = line.split(";")
        date = time.strptime(line_split[0], '%d/%m/%Y')
        desc = line_split[1].strip()
        value = float(line_split[2].strip().replace(",", "."))
        eff_date = None

        if desc[len(desc)-3] is '/' and desc[len(desc)-6] is '-':
            eff_date = date
            date = time.strptime(desc[len(desc)-5:], '%d/%m')
            desc = desc[:-6]

        new_entry = Transaction(date, desc, eff_date)
        new_entry.add_line("Assets:Checking", value)
        print new_entry

if len(sys.argv) < 3:
    print "Need arguments! %s <account> <filename>" % sys.argv[0]
else:
    load_list_csv()
    account = sys.argv[1]

    for i in range(len(sys.argv)-2):
        with open(sys.argv[i+2], 'r') as f:
            eval(account + "(f)")
            f.close()
