from bs4 import BeautifulSoup
from getmeetings import GetBookingsTable
from prettytable import PrettyTable

# ____________ FUNCTIONS _______________
def text2num(string):
    """transforms strings like 12PM to 12.00. or 5:30PM to 17.50"""
    splitstr = string.split(":")
    num1 = int(splitstr[0]) * 60
    
    if 'PM' in splitstr[1]:
        num1 += 720
    
    num2 = int(splitstr[1][:2])
    
    return num1+num2
    
# _______________ DATA _______________________________________
roomdict = {
    # maps the rooms to the proper buildings
            "Student Union Uconn" : {},
            'Arjona Uconn': {"ARJ 105", "ARJ 143"}, 
           "uconn Philip E. Austin" : {"AUST 105", "AUST 108", "AUST 110", "AUST 163", "AUST 344", "AUST 434", "AUST 445"}, 
           'UConn School of Business' : {"BUSN 106", "BUSN 127", "BUSN 211"}, 
           'Castleman Uconn' : {"CAST 212"}, 
           'UConn Chemistry Building' : {"CHEM 248"},
           "Family Studies Building Uconn" : {"FSB 103", "FSB 202", "FSB 220"},
           'Gentry Uconn': {"GENT 131"},
           'ITE UConn' : {"ITE 336", "ITE C80"},
           'Lawrence D. McHugh Hall': {"MCHU 101", "MCHU 102", "MCHU 201", "MCHU 202", "MCHU 205", "MCHU 206", "MCHU 301", "MCHU 302", "MCHU 305", "MCHU 306"},
           'Henry Ruthven Monteith Building' : {"MONT 104"},
           'Susan V. Herbst Hall' : {"SHH 101", "SHH 112", "SHH 117"},
           "schenker lecture hall uconn" : {"SCHN 151"},
           'Torrey life science Uconn': {"TLS 154"},
           "wilfred young building uconn" : {"YNG 100", "YNG 327"},
           "Lester E. Shippee Residence Hall Uconn" : {"SPRH"}
           }

roomset = set()
for rooms in list(roomdict.values()):
    roomset.update(rooms)

# __________ TABLE CREATION ____________________________
def GetDict(offline=False, moredata=False, st=17, printTable=True):
    """ scrapes and print the table from the HTML string """
    
    source_code = GetBookingsTable(test=offline)

    soup = BeautifulSoup(source_code, 'html.parser')

    meetingsSoup = soup.find_all('table')[1]
    meetingsTable = {'timeWindow':[], 'stStr':[], 'etStr':[], 'room':[], 'building':[]}

    # add the starting times to the dictionary
    allStimes = meetingsSoup.find_all(class_ = "showResStartTime")
    allEtimes = meetingsSoup.find_all(class_ = "showResEndTime")
    allRooms= meetingsSoup.find_all(class_ = "roomDesc")


    for i in range(len(allStimes)):
        
        Stime = (allStimes[i].text.strip()[allStimes[i].text.strip().index('M')+1:])
        Etime = (allEtimes[i].text.strip()[allEtimes[i].text.strip().index('M')+1:])
        stInt = text2num(Stime)
        room = allRooms[i].text.strip()
        
        if (room in roomset) and (stInt >=(st*60)):
            
            meetingsTable['stStr'].append(Stime)
            meetingsTable['etStr'].append(Etime)
            meetingsTable["room"].append(room)
            
            st1 = int(text2num(Stime))-1050
            st2 = int(text2num(Etime))-1050
            if(st1 <0):
                st1 = 0
            meetingsTable["timeWindow"].append ( ( st1 , st2  ) ) 
            
            for building, broomset in roomdict.items():
                if room in broomset:
                    meetingsTable["building"].append(building)
        
    if printTable:        
        table = PrettyTable(["Srt Time", "End Time", "Room"])
        table.title = "Today's Bookings"
        for i in range(len(meetingsTable["stStr"])):
            if moredata:
                table.add_row((meetingsTable['stStr'][i], meetingsTable['etStr'][i], meetingsTable['room'][i],  meetingsTable["timeWindow"][i], meetingsTable["building"][i]))
            else:
                table.add_row((meetingsTable['stStr'][i], meetingsTable['etStr'][i], meetingsTable['room'][i]))
        print(table)
        
    # the format of the dictionary: { "starting times" = [list of srt times as string], "end times" = [list of end times as string] , "room" = [list of rooms in order], "timeWindow" = [ list of tuples: (start time as float, end time as float) ], "building": [list of buildings in order based on the room with the same index]}
    return meetingsTable

if __name__ == "__main__":
    GetDict(offline=True, moredata=False, st=17, printTable=True)
    
    while True:
        print("press q and enter to quit")
        if input() == 'q':
            break