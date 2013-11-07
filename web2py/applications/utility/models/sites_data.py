# coding: utf8
import os
""" For treatment we will later do analogous code as for the control where directory will be crawled
	and all the content read in. Disturbing images come from disturbingpictures.tumblr.com.
	I got as far as http://disturbingpictures.tumblr.com/page/22. Next time continue with
	page 23."""

list_files = os.listdir("/home/econ/loki/web2py/applications/utility/static/genova/control")
pics_control = []
for single_file in list_files:
  full_path = "/static/genova/control/" + single_file
  pics_control.append({"url" : full_path})

list_files = os.listdir("/home/econ/loki/web2py/applications/utility/static/genova/treatment")
pics_treatment = []
for single_file in list_files:
  full_path = "/static/genova/treatment/" + single_file
  pics_treatment.append({"url" : full_path})

#pics_treatment = pics_control
