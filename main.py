#coding=utf8
import webapp2
import dns.message
import dns.query
import jinja2
import os
import json


tpl_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))) #..;


class MainHandler(webapp2.RequestHandler):
    def get(self):
        domain = self.request.get('domain')

        tpl = tpl_env.get_template('index.jinja2.html')

        self.response.write(tpl.render({
            'domain': domain,
        }))


class LookupHandler(webapp2.RequestHandler):

    @staticmethod
    def pick_a_record(answers):
        for answer in answers:
            if answer.rdtype == dns.rdatatype.A:
                return answer

    def get(self):
        domain = self.request.get('domain')
        ip = self.request.get('ip')

        query = dns.message.make_query(domain, dns.rdatatype.A)
        received = dns.query.tcp(query, ip, 3000, 53)

        a_record = self.pick_a_record(received.answer) # TODO : 없는경우 대비

        data = a_record.to_rdataset()
        addresses = [x.address for x in data]

        values  = ', '.join(addresses)
        resp_body = json.dumps({
            'domain': domain,
            'A': values,
        })

        self.response.content_type = 'application/json'
        self.response.write(resp_body)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/api/lookup', LookupHandler)
], debug=False)
