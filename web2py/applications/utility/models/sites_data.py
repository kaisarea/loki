# coding: utf8
import os
pics_treatment = [
    {"url" : "http://manteresting.com/nail/316572"},
	{"url" : "http://25.media.tumblr.com/a473ae5b8a3f7bac080a1cc8d8860e24/tumblr_mm9601pDiR1qzerzpo1_500.jpg"},
    {"url" : "http://25.media.tumblr.com/01c37118fb5e8427a4f4ad3c226ad4b8/tumblr_mm6wdph1kF1qzerzpo1_500.jpg"},
	{"url" : "http://disturbingpictures.tumblr.com/"},
    {"url" : "http://25.media.tumblr.com/ede25d58bc410822506df0c8d44a3fcb/tumblr_mm4mblvwaG1r9bh4io1_500.png"},
    {"url" : "http://www.fullpunch.com/wp-content/uploads/2013/01/disturbing-pictures-over-the-web-1.png"},
    {"url" : "http://www.fullpunch.com/wp-content/uploads/2013/01/disturbing-pictures-over-the-web-3.jpg"},
    {"url" : "http://www.fullpunch.com/wp-content/uploads/2013/01/disturbing-pictures-over-the-web-4.png"},
    {"url" : "http://www.fullpunch.com/wp-content/uploads/2013/01/disturbing-pictures-over-the-web-5.jpg"},
    {"url" : "http://www.fullpunch.com/wp-content/uploads/2013/01/disturbing-pictures-over-the-web-6.jpg"},
    {"url" : "http://www.fullpunch.com/wp-content/uploads/2013/01/disturbing-pictures-over-the-web-7.jpg"},
    {"url" : "http://www.fullpunch.com/wp-content/uploads/2013/01/disturbing-pictures-over-the-web-8.jpg"},
    {"url" : "http://www.fullpunch.com/wp-content/uploads/2013/01/disturbing-pictures-over-the-web-9.jpg"}
        
        ]

list_files = os.listdir("/home/econ/loki/web2py/applications/utility/static/genova/control")
pics_control = []
for single_file in list_files:
  full_path = "/static/genova/control/" + single_file
  pics_control.append({"url" : full_path})
#pics_control = [
#    {"url" : "/static/genova/iowa-state-capitol.jpg"},
#    {"url" : "/static/genova/sao-paulo.jpg"},
#    {"url" : "/static/genova/beverly-hills.jpg"},
#    {"url" : "/static/genova/granite.jpg"},
#    {"url" : "/static/genova/watermelon.jpg"},
#    {"url" : "/static/genova/jesus.jpg"},
#    {"url" : "/static/genova/figs.jpg"},
#    {"url" : "/static/genova/bike.jpg"}
#        ]
