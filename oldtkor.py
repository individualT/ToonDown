
import hashlib
   def gethash(self, filename):
        BLOCK_SIZE = 65536  # The size of each read from the file
        # Create the hash object, can use something other than `.sha256()` if you wish
        file_hash = hashlib.sha256()
        with open(filename, 'rb') as f:  # Open the file to read it's bytes
            # Read from the file. Take in the amount declared above
            fb = f.read(BLOCK_SIZE)
            while len(fb) > 0:  # While there is still data being read from the file
                file_hash.update(fb)  # Update the hash
                fb = f.read(BLOCK_SIZE)  # Read the next block from the file
        return file_hash.hexdigest()  # Get the hexadecimal digest of the hash

    def download(self, url, file_name):
        if not os.path.isfile(file_name):
            with open(file_name, "wb") as file:
                response = requests.get(url)
                self.log(file_name+' is being downloaded')
                file.write(response.content)
            if os.path.getsize(file_name) in addict.keys():
                if self.gethash(file_name) == addict[os.path.getsize(file_name)]:
                    os.remove(file_name)
                    return False
        else:
            self.log(file_name+' already exists')
        return True

    def log(self, message):
        global logging
        if not logging:
            return None
        try:
            with open('log.txt', 'r') as logfile:
                lines = logfile.readlines()
        except:
            lines = []
        lines.insert(0, str(datetime.datetime.now())+"\t"+message+'\n')
        with open('log.txt', 'w') as logfile:
            for line in lines:
                logfile.write(line)

    def tkors(self):
        toon_title_list = self.direc()
        global tkor_domain, logging
        html = True
        combine = False  # True
        start = 1
        end = 0
        logging = False
        lis = False
        down = True
        if len(sys.argv) > 1:
            if len(set(sys.argv[1:])&set(['-list', '-l'])) != 0:
                toon_title_list = pickle.load(open('waitlist.txt', 'rb'))
                lis = True
            if len(set(sys.argv[1:])&set(['-down', '-d'])) != 0:
                down = False
            if len(set(sys.argv[1:])&set(['-comb', '-c'])) != 0:
                combine = True
            if len(set(sys.argv[1:])&set(['-log', '-g'])) != 0:
                logging = True
            temptoon = []
            for i in sys.argv[1:]:
                if i[0] != '-':
                    temptoon.append(i)
            if temptoon != []:
                toon_title_list = temptoon
        while True:
            if toon_title_list == []:
                if lis:
                    while toon_title_list == []:
                        time.sleep(6)
                        toon_title_list = pickle.load(
                            open('waitlist.txt', 'rb'))
                else:
                    break
            print(toon_title_list)
            toon_title = toon_title_list[0]
            try:
                self.indexer()
            except Exception as Argument:
                self.log('while indexpage '+str(Argument))
                raise
            toon_title = toon_title.strip()
            self.log('%s download started combine=%s html=%s down=%s list=%s start=%d end=%d html=%s domain=%s'%(toon_title, combine, html, down,lis,start,end,html,tkor_domain))
            try:
                if toon_title == "update":
                    for i in self.direc():
                        self.tkor(tkor_domain, i, html, combine,start,end,down)
                else:
                    self.tkor(tkor_domain, toon_title, html,combine,start,end,down)
            except Exception as Argument:
                self.log('while tkormain '+str(Argument))
                raise
            self.log('%s download finished' % toon_title)
            if lis:
                toon_title_list = pickle.load(open('waitlist.txt', 'rb'))
            if toon_title in toon_title_list:
                toon_title_list.remove(toon_title)
            if lis:
                pickle.dump(toon_title_list, open('waitlist.txt', 'wb'))
global logging
app = tkordownloader()
