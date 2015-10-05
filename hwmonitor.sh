#!/bin/bash

while true; 
do
        ps -eo pmem,pcpu,pid,user,args | sort -k 1 -r | head -10 >> logfile.txt;
        echo "\n" >> logfile.txt;
        sleep 1;
done

#we need to grep this for mention of postgres, apache2 etc
#basically parse every line and aggregate before writing
#into a file

#%MEM %CPU   PID USER     COMMAND
# 2.0  0.3 25091 econ     /usr/sbin/apache2 -k start
# 0.8  0.0 25219 postgres postgres: nail nail_utility_sandbox 127.0.0.1(39809) idle                                                                   
# 0.7  0.0  2730 postgres postgres: writer process                                                                                                    
# 0.5  0.0  2558 www-data /usr/local/bin/uwsgi --ini web2py.ini
# 0.4  0.3 12049 www-data /usr/sbin/apache2 -k start
# 0.3  0.0  2728 www-data /usr/local/bin/uwsgi --ini web2py.ini
# 0.3  0.0  2727 www-data /usr/local/bin/uwsgi --ini web2py.ini
# 0.3  0.0  2726 www-data /usr/local/bin/uwsgi --ini web2py.ini
# 0.3  0.0  2725 www-data /usr/local/bin/uwsgi --ini web2py.ini
