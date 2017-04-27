from twisted.internet import defer, endpoints, protocol, reactor, task, ssl
from twisted.words.protocols import irc
import random
import requests

class IRCBotProtocol(irc.IRCClient):
    nickname = 'S3ct0rsl4ve'
    optkey = "!"
    lol=0

    def signedOn(self):
        for channel in self.factory.channels:
            self.join(channel)
    # Called when a PRIVMSG is received.
    def privmsg(self, user, channel, message):
        nick, _, host = user.partition('!')
        message = message.strip()
        if message[0:2] == "why" or message[0:2] == "Why":
            self.msg(channel, "because.")
        if message[0] == self.optkey:
            self.handle_cmd(nick, channel, message)

        if message.find("http://")!=-1 or message.find("https://")!=-1 or message.find("www.")!=-1:
            self.handle_url(nick, channel, message)
        return

    def handle_cmd(self, user, channel, message):
        cmd=message[1:]
        if cmd.find(' ')!=-1:
            argv=cmd.split(' ')
        else:
            argv = [cmd]
        if argv[0] == "rand":
            self.msg(channel, "["+user+"] " + self.dorand(argv))
        elif argv[0] == "roulette":
            if self.doroulette(argv):
                self.msg(channel, "["+user+"] BOOM! You're dead.")
            else:
                self.msg(channel, "["+user+"] *click*")
        # n33d m04r ...
        # Because SectorBot has a heart! <3
        r=random.randint(0,100)
        if self.lol > 0:
            self.lol -= self.lol

        if r > 95 and self.lol == 0:
            self.privmsg(target, "lol")
            self.lol=20

    def handle_url(self, user, channel, message):
        try:
            url=message[message.index('http'):]
            if url.find(' ') != -1:
                url=url[:url.index(' ')]
        except:
            url=message[message.index('www.'):]
            if url.find(' ') != -1:
                url=url[:url.index(' ')]


        r = requests.get(url.strip())
        if r.status_code != 200:
            return

        c_type=""
        try:
            c_type=r.headers["content-type"]
        except:
            pass
        c_length=""
        try:
            c_length=r.headers["content-length"]
        except:
            pass
         

        title=r.content[r.content.find("<title>"):]
        title=title[:title.find("</title>")]
        title=title.replace("<title>","")
        
        title = self.sectxt(title)
        c_length=self.sectxt(c_length)
        c_type=self.sectxt(c_type)
        self.msg(channel, "["+user+"] \x039{"+title+"} \x037("+c_type+":"+c_length+" Bytes)")

    
    def sectxt(self,txt):
        while txt.find('\n')!=-1:
            txt=txt.replace("\n", "")
        while txt.find("\r")!=-1:
            txt=txt.replace("\r","")
        return txt

    def dorand(self, argv):
        if len(argv) == 1:
            return str((random.getrandbits(0xFFFF) + 1) % 100)
        elif len(argv) == 2:
            return str((random.getrandbits(0xFFFF) + 1) % long(argv[1]))

    def doroulette(self, argv):
         return (random.randint(1,6) == random.randint(1,6))

class IRCBotFactory(protocol.ReconnectingClientFactory):
    protocol = IRCBotProtocol
    channels = ['#sectorone']


if __name__ == '__main__':
    hostname = "irc.freenode.net"
    port = 6697 #port

    factory = IRCBotFactory()
    reactor.connectSSL(hostname, port, factory, ssl.ClientContextFactory())
    reactor.run()
