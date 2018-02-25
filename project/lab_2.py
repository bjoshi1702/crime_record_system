from spyne.decorator import srpc
from spyne.protocol.http import HttpRpc
from spyne.service import ServiceBase
import requests, json
from spyne.model.complex import Iterable
from spyne.model.primitive import Integer
from spyne.model.primitive import Float
from spyne.model.primitive import String, Unicode
from spyne.server.wsgi import WsgiApplication
from spyne import Application
from spyne.protocol.json import JsonDocument
import datetime
import re
import operator
from operator import itemgetter


class CrimeService(ServiceBase):
    @srpc(Float, Float, Float, _returns=Unicode(String))
    def checkcrime(lat,lon, radius):
        url = "https://api.spotcrime.com/crimes.json?lat={}&lon={}&radius={}&key=.".format(lat,lon,radius)
        data = requests.get(url).json()
        
        totalCrime=0
        
        EventTimeCountDict = {'c1': 0, 'c2': 0, 'c3': 0, 'c4': 0, 'c5': 0, 'c6': 0, 'c7': 0, 'c8': 0}
        CrimeListDict = {}
        StreetListDict = {}
        totalCrime=len(data["crimes"])
        
        for i in range(len(data["crimes"])):
            crime_type= data["crimes"][i]["type"]
            crime_datetime= data["crimes"][i]["date"]
            crime_time = CrimeService.find_time(crime_datetime)
            CrimeService.CountForEventTime(crime_time,i, EventTimeCountDict=EventTimeCountDict)
            crime_address= data["crimes"][i]["address"]
            CrimeService.findStreet(crime_address, StreetListDict)
            
            if not crime_type in CrimeListDict:
                CrimeListDict[crime_type]=1
            else:
                CrimeListDict[crime_type]+=1
        
        SortedStreetDict = dict(sorted(StreetListDict.items(), reverse=True, key= operator.itemgetter(1))[:3])
                
        DangerousStreetDict = []    
                
        for key in SortedStreetDict:
            DangerousStreetDict.append(key)
        
        
        c1 = EventTimeCountDict['c1'];
        c2 = EventTimeCountDict['c2'];
        c3 = EventTimeCountDict['c3'];
        c4 = EventTimeCountDict['c4'];
        c5 = EventTimeCountDict['c5'];
        c6 = EventTimeCountDict['c6'];
        c7 = EventTimeCountDict['c7'];
        c8 = EventTimeCountDict['c8'];
        
        
                
        TimeCounterDict = {'12:01am-3am': c1, '3:01am-6am': c2, '6:01am-9am': c3, '9:01am-12noon': c4, '12:01pm-3pm': c5, '3:01pm-6pm': c6, '6:01pm-9pm': c7, '9:01pm-12midnight': c8}
    
        data_print={"total_crime" : totalCrime, "the_most_dangerous_streets" : DangerousStreetDict, "crime_type_count" : CrimeListDict, "event_type_count": TimeCounterDict}
        return data_print
        
    @staticmethod
    def  find_time(crimedt):
        date = datetime.datetime.strptime(crimedt, "%m/%d/%y %I:%M %p")
        dt1 = date.time()
        return date
        
    @staticmethod
    def CountForEventTime(crime_time,crime, EventTimeCountDict):
        year = crime_time.year
        month = crime_time.month
        day = crime_time.day

        dt1 = datetime.datetime(year, month, day, 00, 01, 00)
        dt2 = datetime.datetime(year, month, day, 03, 00, 00)

        if dt1 <= crime_time <= dt2:
            EventTimeCountDict['c1'] = EventTimeCountDict['c1'] + 1
            return EventTimeCountDict

        dt1 = datetime.datetime(year, month, day, 03, 01, 00)
        dt2 = datetime.datetime(year, month, day, 06, 00, 00)

        if dt1 <= crime_time <= dt2:
            EventTimeCountDict['c2'] = EventTimeCountDict['c2'] + 1
            return EventTimeCountDict

        dt1 = datetime.datetime(year, month, day, 06, 01, 00)
        dt2 = datetime.datetime(year, month, day, 9, 1, 00)

        if dt1 <= crime_time <= dt2:
            EventTimeCountDict['c3'] = EventTimeCountDict['c3'] + 1
            return EventTimeCountDict

        dt1 = datetime.datetime(year, month, day, 9, 01, 00)
        dt2 = datetime.datetime(year, month, day, 12, 1, 00)

        if dt1 <= crime_time <= dt2:
            EventTimeCountDict['c4'] = EventTimeCountDict['c4'] + 1
            return EventTimeCountDict

        dt1 = datetime.datetime(year, month, day, 12, 01, 00)
        dt2 = datetime.datetime(year, month, day, 15, 00, 00)

        if dt1 <= crime_time <= dt2:
            EventTimeCountDict['c5'] = EventTimeCountDict['c5'] + 1
            return EventTimeCountDict

        dt1 = datetime.datetime(year, month, day, 15, 01, 00)
        dt2 = datetime.datetime(year, month, day, 18, 00, 00)

        if dt1 <= crime_time <= dt2:
            EventTimeCountDict['c6'] = EventTimeCountDict['c6'] + 1
            return EventTimeCountDict

        dt1 = datetime.datetime(year, month, day, 18, 01, 00)
        dt2 = datetime.datetime(year, month, day, 21, 00, 00)

        if dt1 <= crime_time <= dt2:
            EventTimeCountDict['c7'] = EventTimeCountDict['c7'] + 1
            return EventTimeCountDict
    
        EventTimeCountDict['c8'] = EventTimeCountDict['c8'] + 1
        return EventTimeCountDict
    
    @staticmethod
    def findStreet(address, StreetListDict):
        
        matching1 = re.search(r'[\d\w\s]+OF ([\w\s\d]+ BL)', address)
        if matching1:
            street = matching1.group(1)
            if not street in StreetListDict:
                StreetListDict[street] = 1
            else:
                StreetListDict[street] = StreetListDict[street] + 1
            return StreetListDict

        matching2 = re.search(r'([\d\w\s]+ST) & ([\w\s\d]+ST)', address)
        if matching2:
            street1 = matching2.group(1)
            street2 = matching2.group(2)
            if not street1 in StreetListDict:
                StreetListDict[street1] = 1
            else:
                StreetListDict[street1] = StreetListDict[street1] + 1

            if not street2 in StreetListDict:
                StreetListDict[street2] = 1
            else:
                StreetListDict[street2] = StreetListDict[street2] + 1
            return StreetListDict
            
        matching3 = re.search(r'[\d\w\s]+OF ([\w\s\d]+ ST)', address)
        if matching3:
            street = matching3.group(1)
            
            if not street in StreetListDict:
                StreetListDict[street] = 1
            else:
                StreetListDict[street] = StreetListDict[street] + 1
            return StreetListDict

        

        matching4 = re.search(r'[\d\w\s]+OF ([\w\s\d]+ AV)', address)
        if matching4:
            street = matching4.group(1)
            if not street in StreetListDict:
                StreetListDict[street] = 1
            else:
                StreetListDict[street] = StreetListDict[street] + 1
            return StreetListDict
        
        matching5 = re.search(r'[\d\w\s]+OF ([\w\s\d]+ DR)', address)
        if matching5:
            street = matching5.group(1)
            if not street in StreetListDict:
                StreetListDict[street] = 1
            else:
                StreetListDict[street] = StreetListDict[street] + 1
            return StreetListDict
                        
if __name__=='__main__':
    from wsgiref.simple_server import make_server
    


application=Application([CrimeService], 'spyne.examples.app.http', in_protocol=HttpRpc(validator='soft'), out_protocol=JsonDocument(ignore_wrappers=True))

wsgi_application=WsgiApplication(application)

server=make_server('127.0.0.1',8000,wsgi_application)

   
    

    
server.serve_forever()
