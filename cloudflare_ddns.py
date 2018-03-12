#!/usr/bin/env python3
# Made by Neavend [nsimon.fr] - Unlicensed

import requests as r

class CloudflareDDNS():
    api_key = "PUT_YOUR_KEY_HERE"
    email = "nsimon@protonmail.com"
    recordsToChange = ['test.example.com'] # List of records or None to skip


    def __init__(self, api_key=None):
        self.api_key = api_key or self.api_key
        self.headers = {
            "X-Auth-Key": self.api_key,
            "X-Auth-Email": self.email,
        }
        self.ip = r.get("http://ifconfig.io/ip").text.strip()
        print("Your IP is:", self.ip)

        self.zone_ids = self.get_zone_ids() #TODO
        for zone_id in self.zone_ids:
            for A_record in self.get_A_records(zone_id):
                if not self.recordsToChange or A_record['name'] in self.recordsToChange:
                    if A_record['content'] != self.ip:
                        self.update_record(zone_id, A_record)
                    else:
                        print("IP matches, no need to update {} record for zone {}".format(A_record['type'], zone_id))
        print("Done.")

    def get_zone_ids(self):
        zones = r.get("https://api.cloudflare.com/client/v4/zones",
            headers=self.headers).json()['result']
        if not zones:
            raise Exception("Unable to get zones, check credentials and/or cloudflare configuration")
        for z in zones:
            print('Found DNS Record:', z['name'])
            yield z['id']


    def get_A_records(self, zone_id):
        dns_records = r.get("https://api.cloudflare.com/client/v4/zones/{}/dns_records".format(zone_id),
            headers=self.headers).json()['result']
        if not dns_records:
            raise Exception("Unable to get dns_records, check credentials and/or cloudflare configuration")
        for dns_record in dns_records:
            _type = dns_record['type']
            if _type == 'A' or _type == 'A':
                yield dns_record


    def update_record(self, zone_id, A_record):
        resp = r.put("https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}".format(zone_id, A_record['id']),
            headers=self.headers, json={
                "type": A_record['type'],
                "name": A_record['name'],
                "content": self.ip
            }).json()
        if not resp['success']:
            raise Exception("Unable to update this record, check credentials and/or cloudflare configuration")



if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        CloudflareDDNS(sys.argv[1])
    else:
        CloudflareDDNS()
