# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from .items import metaItem,techItem,techinfoItem
import logging
import datetime
import os
import pandas as pd

class QuotesSpiderPipeline(object):

    def open_spider(self , spider):
        self.websites = set()
        self.metadic = {}
        self.techs = []
        self.techdic = {}

    def process_item(self, item, spider):
        if isinstance(item , metaItem):
            self.websites.add(item['site'])
            self.metadic[item['site']] = item['spent']

        if isinstance(item , techItem):
            self.websites.add(item['site'])
            self.techs.append(item)
        if isinstance(item , techinfoItem):
            desc = item['desc']
            site = item['site']
            if not desc:
                desc = "unknown"
            if not site:
                site = "unknown"
            self.techdic[item['tech']] = (site , desc)



    def close_spider(self , spider):

        mylogger = logging.getLogger("mainspider_logger")

        websites = [x['site'] for x in self.techs]
        domains = [x['domain'] for x in self.techs]
        techs = [x['tech'] for x in self.techs]

        spent = []
        for x in self.techs:
            site = x['site']
            try:
                v = self.metadic[site]
                spent.append(v)
            except KeyError:
                spent.append("unknown")

        urls , descs = [] , []
        for x in self.techs:
            tech = x['tech']
            try:
                tup = self.techdic[tech]
                urls.append(tup[0])
                descs.append(tup[1])
            except KeyError:
                urls.append("unknown")
                descs.append("unknown")
        #mylogger.warning("{} {} {} {} {} {}".format(len(techs) , len(websites) , len(spent) , len(domains) , len(descs) , len(urls)))
        final_dic = {
            'website': websites,
            'spend': spent,
            'technology': techs,
            'domain': domains,
            'link': urls,
            'description': descs
        }
        df = pd.DataFrame.from_dict(final_dic)
        df = df[final_dic.keys()]

        resdir = "./results/" + datetime.datetime.now().strftime("%m%d%Y-%H%M%S") + "/"
        try:
            os.makedirs(resdir, exist_ok=True)

        except:
            pass

        df.to_csv(os.path.join(resdir, 'master.csv'), sep=',')

        """websites = list(self.websites)
        metadic = {}
        for site in websites:
            try:
                metadic[site] = self.metadic[site]
            except KeyError:
                metadic[site] = "unknown"
        """
        for site_name in set(websites):
            mini_df = df[df.website == site_name]
            mini_df = mini_df.drop('website', axis='columns')
            mini_df.to_csv(os.path.join(resdir, site_name + ".csv"), sep=',')

