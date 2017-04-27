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
import ssl
import socket
import httplib

class SectorBot:
    
    # Config
    SERVER="irc.freenode.net"
    PORT=6697
    CHANNEL="#sectorone"
    BOTNICK="S3c70rB0t"
    
    
    msg_stack=[]
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = ssl.wrap_socket(self.sock)
        random.seed()

    def connect(self):
        print "[*] Connecting to " + self.SERVER + " port " + str(self.PORT) + " chan " + self.CHANNEL + " using nick " + self.BOTNICK
        self.sock.connect((self.SERVER, self.PORT))
        self.sock.send("USER "+self.BOTNICK+" "+self.BOTNICK+" "+self.BOTNICK+" : H4cK7h3p14n37!\n")
        self.sock.send("NICK "+self.BOTNICK+"\n")
        self.sock.send("JOIN "+self.CHANNEL+"\n")
        self.sock.recv(2048) # Further checks can be done with this.
        # TODO: replace NICK if already taken
        #       or even register the bot then identifiy below.

    def disconnect(self):
        self.sock.close()

    def privmsg(self, target, msg):
        self.sock.send("PRIVMSG "+target+" :"+msg+"\r\n")



    def h4x17(self):
        while True:
            data = self.sock.recv(1024)
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
        content=""
        c_type=""
        c_length=""
        page=""
        ssl=False
        try:
            url=msg[msg.index('http'):]
            if url.find(' ') != -1:
                url=url[:url.index(' ')]

            base_url=url.split("/")[2]
            if len(url.split("/"))>2:
                for i in range(3, len(url.split("/"))):
                    page+="/"+url.split("/")[i]
        except:
            url=msg[msg.index('www.'):]
            if url.find(' ') != -1:
                url=url[:url.index(' ')]
            base_url=url.split("/")[0]

            if len(url.split("/"))>1:
                for i in range(2, len(url.split("/"))):
                    page+="/"+url.split("/")[i]

            if page == "":
                page = "/"

        try:
            print "ssl"
            c = httplib.HTTPSConnection(base_url)
            c.request("GET", page)
        except:
            print "plain"
            c = httplib.HTTPConnection(base_url)
            c.request("GET", page)
        try:
            r=c.getresponse()
            content=r.read()
            c_type=r.getheader('Content-Type')
            c_length=r.getheader('Content-Length')
        except:
            pass
        if content.find('<title>') != -1:
            title=content[content.index('<title>'):]
            title=title[:title.index('</title>')]
            title=title.replace('<title>','').replace("\n", " ").strip()
        if title is not "":
            self.privmsg(target, "["+str(author)+"] {" + str(title) + "} ("+str(c_type)+", "+str(c_length)+" Bytes)")
        else:
            self.privmsg(target, "["+str(author)+"] ("+str(c_type)+", "+str(c_length)+" Bytes)")

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
        if msg is "Hello " + self.BOTNICK:
            self.privmsg(target, "Hello " + author + "!")

        if mod is '!':
            cmd=msg[1:]
            if cmd.find(' ')!=-1:
                argv=cmd.split(' ')
            else:
                argv = [cmd]
            if argv[0] == "rand":
                if len(argv) == 1:
                    self.privmsg(target, str((random.getrandbits(0xFFFF) + 1) % 100))
                elif len(argv) == 2:
                    self.privmsg(target, str((random.getrandbits(0xFFFF) + 1) % int(argv[1])))
                else:
                    self.privmsg(target, str((random.getrandbits(0xFFFF) + int(argv[1]) % int(argv[2]))))

            if argv[0] == "roulette":
                if random.randint(1,6) == random.randint(1,6):
                    self.privmsg(target, "["+author+"] BOOM! You are dead.")
                    self.sock.send("KICK "+ target + " " + author + ": Here we kick kali users\r\n")
                    print self.sock.recv(128)
                else:
                    self.privmsg(target, "["+author+"] *click*")
            # n33d m04r ...

        # Because SectorBot has a heart! <3
        r=random.randint(0,100)
        if r > 95:
            self.privmsg(target, "lol")



irc=SectorBot()
irc.connect()
irc.h4x17()
irc.disconnect()
