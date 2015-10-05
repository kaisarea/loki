line = '172.16.0.3 - - [25/Sep/2002:14:04:19 +0200] "GET / HTTP/1.1" 401 - "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.1) Gecko/20020827"'


line = '76.104.182.172 - - [20/Apr/2014:06:36:52 +0000] "GET /static/debug_tasks?_=1397975811306 HTTP/1.1" 200 2939'
regex = '([(\d\.)]+) - - \[(.*?)\] "(.*?)" (.*?) (.*?)'

import re, collections, sys

f = open(sys.argv[1])
lines = [re.match(regex, line).groups() for line in f]
codes = [line[-2] for line in lines]
counts = collections.Counter(codes)
for k,v in counts.items():
    print ('code %s occurs %2d%%'
           % (k, int(100 * float(v) / float(len(lines)))))

