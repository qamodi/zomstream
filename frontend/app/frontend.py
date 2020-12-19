#!/usr/bin/env python

# imports
import flask
import pathlib
import yaml
import sys
import xml.etree.ElementTree as etree
import urllib
import logging

logging.basicConfig(level=logging.DEBUG)

# load configuration from config.yml file
if pathlib.Path("config.yml").is_file():
    stream = open('config.yml', 'r')
    configuration = yaml.load(stream)
    stream.close()
else:
    print('missing configuration.')
    sys.exit(1)

def getStreamNames(url):
    streamnames = []
    # get data from the streaming server
    response = urllib.request.urlopen(url)
    content = response.read().decode('utf-8')
    # parse the xml / walk the tree
    tree = etree.fromstring(content)
    server = tree.find('server')
    applications = server.findall('application')
    for application in applications:
        appname = application.find('name')
        if appname.text == "live" or appname.text == "rec":
            streams = application.find('live').findall('stream')
            for stream in streams:
                name = stream.find('name')
                rate = stream.find('bw_video')
                if rate.text != "0":
                    streamnames.append( [appname.text, name.text] )

    return streamnames

streamList = []
frontend = flask.Flask(__name__)

@frontend.route("/")
def start():
    mainTemplate = '%s/main.html.j2' % configuration['template_folder']
    streamList = getStreamNames(configuration['stat_url'])
    page = flask.render_template(
        mainTemplate,
        items=streamList,
        configuration=configuration
    )
    return page

@frontend.route("/player/<appname>/<streamname>")
def show_player(appname, streamname):
    playerTemplate = '%s/player.html.j2' % configuration['template_folder']
    page = flask.render_template(
        playerTemplate, 
        streamname=streamname,
        appname=appname,
        hls_url='%s://%s/video/hls/%s.m3u8' % (
            configuration['web_proto'], 
            configuration['base_url'], 
            streamname),
        configuration=configuration
        )
    return page
