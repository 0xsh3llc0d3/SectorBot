#######################################################################
# SectorBot - 2017                                                    #
#                                                                     #
# Because every IRC channels need a good slave.                       #
#                                                                     #
# Copyleft # SectorOne Team                                           #
# https://sectorone.cr                                                #
# developed by sh3llc0de (http://0xsh3llc0.de)                        #
#######################################################################
#        .__    ________ .__  .__         _______       .___________  
#   _____|  |__ \_____  \|  | |  |   ____ \   _  \    __| _/\_____  \ 
#  /  ___/  |  \  _(__  <|  | |  | _/ ___\/  /_\  \  / __ |   _(__  < 
#  \___ \|   Y  \/       \  |_|  |_\  \___\  \_/   \/ /_/ |  /       \
# /____  >___|  /______  /____/____/\___  >\_____  /\____ | /______  /
#      \/     \/       \/               \/       \/      \/        \/ 

import sys
import re
import random
import socket
import urllib2 # useful to get content of links posted on the channel

# Config
SERVER="irc.freenode.net"
PORT=6667
CHANNEL="#sectorone"
BOTNICK="s3ct0rB0t"

class SectorBot:
    msg_stack=[]
    lol=-1
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        random.seed()

    def connect(self):
        global SERVER,PORT,CHANNEL,BOTNICK
        print "[*] Connecting to " + SERVER + " port " + str(PORT) + " chan " + CHANNEL + " using nick " + BOTNICK
        self.sock.connect((SERVER, PORT))
        self.sock.send("USER "+BOTNICK+" "+BOTNICK+" "+BOTNICK+" : H4cK7h3p14n37!\n")
        self.sock.send("NICK "+BOTNICK+"\n")
        self.sock.send("JOIN "+CHANNEL+"\n")
        self.sock.recv(1024) # Further checks can be done with this.
        # TODO: replace NICK if already taken
        #       or even register the bot then identifiy below.

    def disconnect(self):
        self.sock.close()

    def privmsg(self, target, msg):
        self.sock.send("PRIVMSG "+target+" :"+msg+"\r\n")

    def h4x17(self):
        global CHANNEL,BOTNICK
        while True:
            data = self.sock.recv(4096)
            if not data:
                pass
            elif data.find('PING') != -1: # PING?
                self.sock.send("PONG " + data.split()[1]+'\r\n') # PONG!
                print "[*] Got a ping. " + str(data.split()[1])
            else:
                data=data.split(' :')
                if len(data)<2:
                    pass
                else:
                    msg=data[1][:-2]
                    # We have the message, let's get the author.
                    data=data[0].split('PRIVMSG ')
                    if len(data)<2:
                        pass
                    else:
                        author_mask,target = data
                        data=author_mask.split('!~') # data is something like :username!~username@hostname 
                        author=data[0][1:]
                        self.msg_stack.insert(0,"["+author+"] "+msg) # Add the current message to the message pile.
                        if len(msg) > 1:
                            if msg.find('http://') != -1 or msg.find('https://') != -1 or msg.find("www.") != -1: # Some sort of URL?
                                self.handle_url(author, target, msg)
                            else: # Finish here. Let's check if msg is a command.
                                self.handle_cmd(author, target, msg)
        
    def handle_url(self, author, target, msg):
        title=""
        try:
            url=msg[msg.index('http'):]
        except:
            url=msg[msg.index('www.'):]
        if url.find(' ') != -1:
            url=url[:url.index(' ')]
        try:
            response=urllib2.urlopen(url)
            content=response.read()
            c_type=response.info().getheader('Content-Type')
            c_length=response.info().getheader('Content-Length')
        except:
            pass
        if content.find('<title>') != -1:
            title=content[content.index('<title>'):]
            title=title[:title.index('</title>')]
            title=title.replace('<title>','')
        if title is not "":
            self.privmsg(CHANNEL, "["+str(author)+"] {" + str(title) + "} ("+str(c_type)+", "+str(c_length)+" Bytes)")
        else:
            self.privmsg(CHANNEL, "["+str(author)+"] ("+str(c_type)+", "+str(c_length)+" Bytes)")

    def handle_cmd(self, author, target, msg):
        mod=msg[0]
        
        if mod is 's':
            if msg[1] is '/':
                payload=msg[2:]
                txt_regex=payload[:payload.index('/')]
                txt_replace=payload[payload.index('/')+1:]

                self.msg_stack=self.msg_stack[1:]

                for past_msg in self.msg_stack:
                    if re.search(txt_regex, past_msg) is not None:
                        past_msg=re.sub(txt_regex,txt_replace, past_msg)
                        self.privmsg(target, past_msg)
                        return
                return

        if mod is '!':
            self.privmsg(target, "["+str(author)+"] No commands yet.. except `s/<search>/<replace>` Share your ideas for commands!")
            # TODO: commands.
            # rand, roulette, ...

        # Because SectorBot has a heart! <3
        r=random.randint(0,100)
        if r > 85:
            self.privmsg(target, "lol")


irc=SectorBot()
irc.connect()
irc.h4x17()
irc.disconnect()
