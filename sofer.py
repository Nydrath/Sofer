import pydle
import json

with open("password", "r") as f:
    WHOIS_PW = f.read().strip()

def update_ipnames(hostname, nick):
    with open("ipnames.json", "r") as f:
        data = json.load(f)
    if hostname in data:
        if nick not in data[hostname]:
            data[hostname].append(nick)
            with open("ipnames.json", "w") as f:
                json.dump(data, f, indent=4)
    else:
        data[hostname] = [nick]
        with open("ipnames.json", "w") as f:
            json.dump(data, f, indent=4)

def nickname(fullname):
    return fullname[:fullname.index("!")].strip("@").strip("%").strip("+")

def hostname(fullname):
    name = fullname[fullname.index("!"):]
    return name[name.index("@")+1:]

def listjoin(l):
    s = ", ".join(l)
    if len(l) > 1:
        idx = s.rfind(", ")+1
        s = s[:idx] + " and" + s[idx:]
    return s

class Sofer(pydle.Client):
    def on_connect(self):
         self.join('#/div/ination')

    def on_raw(self, message):
        super(Sofer, self).on_raw(message)
        if message.command == 353:
            people = message.params[3].split()
            for person in people:
                update_ipnames(hostname(person), nickname(person))
        elif message.command == "JOIN":
            update_ipnames(hostname(message.source), nickname(message.source))
        elif message.command == "NICK":
            update_ipnames(hostname(message.source), message.params[0])

    def on_private_message(self, nick, message):
        if WHOIS_PW in message:
            hostname = message.split()[1]
            with open("ipnames.json", "r") as f:
                data = json.load(f)
            if hostname in data:
                self.message(nick, "{0} has appeared under the names {1}".format(hostname, listjoin(data[hostname])))
            else:
                self.message(nick, "{0} is not in the database".format(hostname))
            for potentialhost in data.keys():
                crop = potentialhost[potentialhost.index(".")+1:]
                if crop in message and potentialhost != hostname:
                    self.message(nick, "{0} has a similar ip, using the names {1}".format(potentialhost, listjoin(data[potentialhost])))


client = Sofer("Sofer", realname="Sofer")
client.connect('irc.us.sorcery.net', 6667)
client.handle_forever()
