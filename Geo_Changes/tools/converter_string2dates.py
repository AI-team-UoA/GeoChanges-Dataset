import random
import time
import datetime
from datetime import timedelta
import random
from datetime import datetime
import threading,time


# date_str="Fri Apr 01 00:00:00 1960" #Fri Apr 01 00:00:00 EET 1960

# ./resources/rdf_dump/events_updated_uris_county_n.nt

with open("./resources/older_files/events_updated_uris_county_n.nt", 'r', encoding='UTF-8') as file:
    while (line := file.readline().rstrip()):
    # line = file.readline().rstrip()
        triple = line.split(" ")
        if triple[1] == "<http://semanticweb.cs.vu.nl/2009/11/sem/hasBeginTimeStamp>" or triple[1] == "<http://semanticweb.cs.vu.nl/2009/11/sem/hasEndTimeStamp>":
            date_str=line.split("\"")[1]
            new_date_str = date_str.replace("EET", "")
            new_date_str = new_date_str.replace("EEST", "")
            d = datetime.strptime(new_date_str, '%a %b %d %H:%M:%S %Y')
            new_line = line.replace(date_str, str(d.date()))
            new_line = new_line.replace("http://www.w3.org/2001/XMLSchema#string", "http://www.w3.org/2001/XMLSchema#date")
        else:
            new_line = line
        #print(new_line)
        with open('./resources/rdf_dump/events_updated_uris_county_n2.nt', 'a', encoding='UTF-8') as the_file:
            the_file.write(new_line+"\n")
