import btree

class DataThree:
    database = None
    file = None
    actualKey = None

    def __init__(self):
        pass

    def openDatabase(self, readMode):
        if not readMode:
            self.file = open("../config", "w+b")
        else:
            try:
                self.file = open("../config", "r+b")
            except OSError:
                self.file = open("../config", "w+b")
        self.database = btree.open(self.file)
        return True if self.database != None else False

    def begin(self, key, readMode=True):
        self.actualKey = key
        return self.openDatabase(readMode)

    def put(self, key, data):
        if (self.database != None):
            if (type(data) is str):
                data_to_write = data
            else:
                data_to_write = str(data)
       #     print(f"key: {key} data: {data_to_write}")
            self.database[(self.actualKey + key).encode("utf-8")] =  data_to_write.encode("utf-8")
        else:
            print('Databaza sa nenasla!')

    def getString(self, key):
        try:
            if (self.database != None):
            #    print(f"key: {self.actualKey} k {key}  db {self.database.keys()}")
             #   for key1 in self.database.keys():
            #        print(key1)
                #if (self.database[(self.actualKey + key).encode("utf-8")] in self.database):
                if (self.actualKey + key).encode("utf-8") in self.database.keys():
                    return self.database[(self.actualKey + key)].decode("utf-8")
            else:
                print('Databaza sa nenasla!')
        except KeyError:
            print("Key not found")
            return None

    def getInt(self, key, defaultValue=None):
        data = self.getString(key)
        if (data != None):
            return int(self.getString(key))
        else:
            print("returned default value")
            return defaultValue

    def getBool(self, key, defaultValue=None):
        data = self.getString(key)
        if (data != None):
            return data.lower() in ("true", "yes", "t", "1")
        else:
            return defaultValue

    def end(self):
        self.database.flush()
        self.database.close()
        self.file.close()


"""
if(pref.begin(definition.TYPE_DAY_NIGHT.lower(), False)):
     pref.put("hour_on", self.hourOpk)
     pref.put("min_on", self.minOpk)
     pref.put("hour_off", self.hourCyk)
     pref.put("min_off", self.minCyk)
     pref.end()
"""
