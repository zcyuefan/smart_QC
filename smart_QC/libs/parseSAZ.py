#!/usr/bin/env python
# encoding=utf-8

# Author zhangchao@jinwantai.com
# date:2017/2/9
# topic:
# update:

"""
This parses SAZ files outputted by Fiddler. It's a performance tool.

Steps:

0) Create a DSN on a windows machine to the local SQL Database. Edit the connection string in the script.

1) Save Fiddler output as SAZ file

2) Copy that file and rename the copy to WHATEVER.ZIP

3) Unzip that file into a folder called WHATEVER

4) Run the python script. This will process one record at a time into a SQL database (uncomment the SQLite3 part if you need to).
"""
import re
import os
import sqlite3
import pytz
from datetime import datetime
from bs4 import BeautifulSoup

# import pyodbc

server = 'localhost'
database = 'Performance'
connStr = (r'DSN=PerfDB')

# 09/13/2016, JJ.
'''Fiddler is a Telerik product that snoops localhost traffic. Its output is of file-type SAZ.
Rename a COPY to ZIP and extract it to a new folder in the current folder. This new folder
should be at the same level as the python script, so that the extracted contents are within
the new folder.'''

'''
create function stripWire(
	@URL VARCHAR(MAX)
) RETURNS VARCHAR(100)
AS
BEGIN
	return substring(@URL, 0, CHARINDEX('?', @URL))
END

CREATE TABLE [dbo].[browsing_history](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Result] [decimal](9, 2) NULL,
	[Protocol] [nvarchar](500) NULL,
	[Host] [nvarchar](500) NULL,
	[URL] [nvarchar](500) NULL,
	[Body] [int] NULL,
	[Caching] [nvarchar](500) NULL,
	[ContentType] [nvarchar](500) NULL,
	[Process] [nvarchar](500) NULL,
	[Comments] [nvarchar](500) NULL,
	[Custom] [nvarchar](500) NULL,
	[CID] [int] NULL,
	[SID] [int] NULL,
	[MID] [int] NULL
) ON [PRIMARY]
CREATE TABLE [dbo].[C](
	[CID] [int] NULL,
	[Method] [nvarchar](500) NULL,
	[URL] [nvarchar](max) NULL,
	[Version] [nvarchar](500) NULL,
	[Host] [nvarchar](500) NULL,
	[Connection] [nvarchar](500) NULL,
	[Content_Length] [nvarchar](500) NULL,
	[Accept] [nvarchar](500) NULL,
	[Origin] [nvarchar](500) NULL,
	[User_Agent] [nvarchar](500) NULL,
	[Content_Type] [nvarchar](500) NULL,
	[Referer] [nvarchar](500) NULL,
	[Accept_Encoding] [nvarchar](500) NULL,
	[Accept_Language] [nvarchar](500) NULL,
	[Cookie] [nvarchar](max) NULL,
	[JSONRequest] [nvarchar](max) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
CREATE TABLE [dbo].[M](
	[MID] [int] NULL,
	[ClientConnected] [datetime] NULL,
	[ClientBeginRequest] [datetime] NULL,
	[GotRequestHeaders] [datetime] NULL,
	[ClientDoneRequest] [datetime] NULL,
	[GatewayTime] [datetime] NULL,
	[DNSTime] [datetime] NULL,
	[TCPConnectTime] [datetime] NULL,
	[HTTPSHandshakeTime] [datetime] NULL,
	[ServerConnected] [datetime] NULL,
	[FiddlerBeginRequest] [datetime] NULL,
	[ServerGotRequest] [datetime] NULL,
	[ServerBeginResponse] [datetime] NULL,
	[GotResponseHeaders] [datetime] NULL,
	[ServerDoneResponse] [datetime] NULL,
	[ClientBeginResponse] [datetime] NULL,
	[ClientDoneResponse] [datetime] NULL,
	[x_egressport] [int] NULL,
	[x_responsebodytransferlength] [int] NULL,
	[x_clientport] [int] NULL,
	[x_clientip] [nvarchar](500) NULL,
	[x_serversocket] [nvarchar](500) NULL,
	[x_hostip] [nvarchar](500) NULL,
	[x_processinfo] [nvarchar](500) NULL
) ON [PRIMARY]
CREATE TABLE [dbo].[S](
	[SID] [int] NULL,
	[Cache_Control] [nvarchar](500) NULL,
	[Content_Type] [nvarchar](500) NULL,
	[Content_Length] [int] NULL,
	[Server] [nvarchar](500) NULL,
	[X_AspNetMvc_Version] [decimal](9, 2) NULL,
	[X_AspNet_Version] [decimal](9, 2) NULL,
	[X_SourceFiles] [nvarchar](500) NULL,
	[WWW_Authenticate] [nvarchar](500) NULL,
	[WWW_Authenticate2] [nvarchar](500) NULL,
	[X_Powered_By] [nvarchar](500) NULL,
	[Date] [smalldatetime] NULL,
	[Proxy_Support] [nvarchar](500) NULL,
	[Response] [nvarchar](500) NULL,
	[Version] [nvarchar](500) NULL,
	[StatusCode] [decimal](9, 2) NULL,
	[Status] [nvarchar](500) NULL,
	[JSONRequest] [nvarchar](max) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
'''


def file_get_contents(filename):
    with open(filename) as f:
        return f.read()


def log(text):
    file = open('SQLStatements.txt', 'a')
    file.write(text + "\n")
    file.close()


def checkDB(db_name):
    conn = sqlite3.connect(db_name)

    cur = conn.cursor()
    tables = cur.execute("SELECT name FROM sqlite_master;")
    all_tables = [x[0] for x in tables.fetchall()]

    # check that the table at least has the 4 main tables.
    if (set(all_tables) & set(['C', 'S', 'M', 'browsing_history']) != set(['C', 'S', 'M', 'browsing_history'])):
        # check the db for these table(s):
        str_make_table_browsing_history = "CREATE TABLE 'browsing_history' (	'ID'	INTEGER,	'Result'	NUMERIC,	'Protocol'	TEXT,	'Host'	TEXT,	'URL'	TEXT,	" \
                                          "'Body'	INTEGER,	'Caching'	TEXT,	'ContentType'	TEXT,	'Process'	TEXT,	'Comments'	TEXT, " \
                                          "'Custom'	TEXT, 'CID'	INTEGER, 'SID'	INTEGER, 'MID'	INTEGER, PRIMARY KEY(ID) );"

        str_make_table_c = "CREATE TABLE 'C' (	'CID'	INTEGER,	'Method'	TEXT,  'URL' TEXT, 'Version' TEXT,	'Host'	TEXT,	'Connection'	TEXT,	'Content_Length'	INTEGER,	'Accept'	TEXT, " \
                           "'Origin'	TEXT, 	'User_Agent'	TEXT,	'Content_Type'	TEXT,	'Referer'	TEXT,	'Accept_Encoding'	TEXT,	'Accept_Language'	TEXT,	'Cookie'	TEXT, " \
                           "'JSONRequest'	TEXT, 	PRIMARY KEY(CID));"

        str_make_table_s = "CREATE TABLE 'S' (	'SID'	INTEGER,	'Cache_Control'	TEXT,	'Content_Type'	TEXT,	'Content_Length' INTEGER, 'Server'	TEXT,	'X_AspNetMvc_Version'	NUMERIC,	" \
                           "'X_AspNet_Version'	NUMERIC,	'X_SourceFiles'	TEXT,	'WWW_Authenticate'	TEXT,	'WWW_Authenticate2'	TEXT,	'X_Powered_By'	TEXT,	'Date'	TEXT, " \
                           "'Proxy_Support'	TEXT,	'Response'	TEXT, 'Version' TEXT, 'StatusCode' TEXT, 'Status' TEXT, 'JSONRequest' TEXT,  PRIMARY KEY(SID));"

        str_make_table_m = "CREATE TABLE 'M' (	'MID'	INTEGER,	'ClientConnected'	TEXT,	'ClientBeginRequest'	TEXT,	'GotRequestHeaders'	TEXT, " \
                           "'ClientDoneRequest'	TEXT,	'GatewayTime'	TEXT,	'DNSTime'	TEXT,	'TCPConnectTime'	TEXT,	'HTTPSHandshakeTime'	TEXT,	'ServerConnected'	TEXT, " \
                           "'FiddlerBeginRequest'	TEXT,	'ServerGotRequest'	TEXT,	'ServerBeginResponse'	TEXT,	'GotResponseHeaders'	TEXT,	'ServerDoneResponse'	TEXT, " \
                           "'ClientBeginResponse'	TEXT,	'ClientDoneResponse'	TEXT,	'x_egressport'	INTEGER,	'x_responsebodytransferlength'	INTEGER,	'x_clientport'	INTEGER, " \
                           "'x_clientip'	TEXT,	'x_serversocket'	TEXT,	'x_hostip'	TEXT,	'x_processinfo'	TEXT, 	PRIMARY KEY(MID));"

        try:
            conn.execute(str_make_table_browsing_history)
        except sqlite3.OperationalError as e:
            print(e)
            pass

        try:
            conn.execute(str_make_table_c)
        except sqlite3.OperationalError as e:
            print(e)
            pass

        try:
            conn.execute(str_make_table_s)
        except sqlite3.OperationalError as e:
            print(e)
            pass

        try:
            conn.execute(str_make_table_m)
        except sqlite3.OperationalError as e:
            print(e)
            pass

        conn.commit()
        conn.close()
        return True

    # re-evaluate: are there at least these 4 tables?
    return set(all_tables) & set(['C', 'S', 'M', 'browsing_history']) == set(['C', 'S', 'M', 'browsing_history'])


class browsing_history:
    ID = ""
    Result = ""
    Protocol = ""
    Host = ""
    URL = ""
    Body = ""
    Caching = ""
    ContentType = ""
    Process = ""
    Comments = ""
    Custom = ""
    CID = ""
    SID = ""
    MID = ""

    def save(self):
        self.Body = self.Body.replace(",", "").strip()
        vals = (
        self.Result, self.Protocol, self.Host, self.URL, self.Body, self.Caching, self.ContentType, self.Process,
        self.Comments, self.Custom, self.CID, self.SID, self.MID)
        new_record = "INSERT INTO browsing_history (Result, Protocol, Host, URL, Body, Caching, ContentType, Process, Comments, Custom, CID, SID, MID) " \
                     "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', {10}, {11}, {12})".format(
            *vals)

        new_record = new_record.replace("'NULL'", "NULL")
        log('\n' + new_record)

        try:
            ### self.conn.execute(new_record)
            ### self.conn.commit()
            dbCursor = self.conn.cursor()
            dbCursor.execute(new_record)
            dbCursor.commit()
        except pyodbc.DataError as e:
            log("--" + e.args[1])


class C:
    CID = ""
    Method = ""
    URL = ""
    Version = ""
    Host = ""
    Connection = ""
    Accept = ""
    Origin = ""
    User_Agent = ""
    Content_Length = ""
    Content_Type = ""
    Referer = ""
    Accept_Encoding = ""
    Accept_Language = ""
    Cookie = ""
    JSONRequest = ""

    def parse(self, file_name):
        nLineNumber = 0
        # we have to read these C, S, M files line by line
        with open(file_name) as f:
            for line in f:
                if (line == "\n"):
                    continue
                if (nLineNumber == 0):
                    sline = line.split(" ")
                    self.Method = sline[0].strip()
                    self.URL = sline[1].strip()
                    self.Version = sline[2].strip()
                else:
                    if (self.Cookie != ""):
                        # cookie's been set, the next thing is the request
                        self.JSONRequest = self.JSONRequest + line
                    else:
                        # note the space, to keep port numbers, etc
                        sline = line.split(": ")
                        inboundKey = sline[0].strip().upper()
                        inboundVal = sline[1].strip()

                        if (inboundKey == "HOST"):
                            self.Host = inboundVal
                        elif (inboundKey == "CONNECTION"):
                            self.Connection = inboundVal
                        elif (inboundKey == "CONTENT-LENGTH"):
                            self.Content_Length = inboundVal
                        elif (inboundKey == "ACCEPT"):
                            self.Accept = inboundVal
                        elif (inboundKey == "ORIGIN"):
                            self.Origin = inboundVal
                        elif (inboundKey == "USER-AGENT"):
                            self.User_Agent = inboundVal
                        elif (inboundKey == "CONTENT-TYPE"):
                            self.Content_Type = inboundVal
                        elif (inboundKey == "REFERER"):
                            self.Referer = inboundVal
                        elif (inboundKey == "ACCEPT-ENCODING"):
                            self.Accept_Encoding = inboundVal
                        elif (inboundKey == "ACCEPT-LANGUAGE"):
                            self.Accept_Language = inboundVal
                        elif (inboundKey == "COOKIE"):
                            self.Cookie = inboundVal

                nLineNumber = nLineNumber + 1

        self.save()

    def save(self):
        vals = (self.CID, self.Method, self.URL, self.Version, self.Host, self.Connection, self.Accept, self.Origin,
                self.User_Agent, self.Content_Length, self.Content_Type, self.Referer, \
                self.Accept_Encoding, self.Accept_Language, self.Cookie, self.JSONRequest)
        new_record = "INSERT INTO C (CID, Method, URL, Version, Host, Connection, Accept, Origin, User_Agent, Content_Length, Content_Type, Referer, " \
                     "Accept_Encoding, Accept_Language, Cookie, JSONRequest) VALUES ({0}, '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}', '{14}', '{15}')".format(
            *vals)

        new_record = new_record.replace("'NULL'", "")

        log('\n' + new_record)

        try:
            ### self.conn.execute(new_record)
            ### self.conn.commit()
            dbCursor = self.conn.cursor()
            dbCursor.execute(new_record)
            dbCursor.commit()
        except pyodbc.DataError as e:
            log("--" + e.args[1])


class S:
    SID = ""
    Cache_Control = ""
    Content_Type = ""
    Content_Length = ""
    Server = ""
    X_AspNetMvc_Version = ""
    X_AspNet_Version = ""
    X_SourceFiles = ""
    WWW_Authenticate = ""
    WWW_Authenticate2 = ""
    X_Powered_By = ""
    Date = ""
    Proxy_Support = ""
    Response = ""
    Version = ""
    StatusCode = ""
    Status = ""
    JSONRequest = ""

    def parse(self, file_name):
        nLineNumber = 0
        # we have to read these C, S, M files line by line
        with open(file_name) as f:
            for line in f:
                if (line == "\n"):
                    continue
                if (nLineNumber == 0):
                    sline = line.split(" ")
                    self.Version = sline[0].strip()
                    self.StatusCode = sline[1].strip()
                    self.Status = sline[2].strip()
                else:
                    if (self.Content_Length != ""):
                        # cookie's been set, the next thing is the request
                        self.JSONRequest = self.JSONRequest + line
                    else:
                        # note the space, to keep port numbers, etc
                        sline = line.split(": ")
                        inboundKey = sline[0].strip().upper()
                        inboundVal = sline[1].strip()

                        if (inboundKey == "Cache-Control".upper()):
                            self.Cache_Control = inboundVal
                        elif (inboundKey == "Content_Type".upper()):
                            self.Content_Type = inboundVal
                        elif (inboundKey == "CONTENT-LENGTH"):
                            self.Content_Length = inboundVal
                        elif (inboundKey == "Server".upper()):
                            self.Server = inboundVal
                        elif (inboundKey == "X_AspNetMvc_Version".upper()):
                            self.X_AspNetMvc_Version = inboundVal
                        elif (inboundKey == "X_AspNet_Version".upper()):
                            self.X_AspNet_Version = inboundVal
                        elif (inboundKey == "X_SourceFiles".upper()):
                            self.X_SourceFiles = inboundVal
                        elif (inboundKey == "WWW_Authenticate".upper()):
                            self.WWW_Authenticate = inboundVal
                        elif (inboundKey == "WWW_Authenticate2".upper()):
                            self.WWW_Authenticate2 = inboundVal
                        elif (inboundKey == "X_Powered_By".upper()):
                            self.X_Powered_By = inboundVal
                        elif (inboundKey == "Date".upper()):
                            self.Date = inboundVal
                        elif (inboundKey == "Proxy_Support".upper()):
                            self.Proxy_Support = inboundVal
                        elif (inboundKey == "Response".upper()):
                            self.Response = inboundVal
                        elif (inboundKey == "Version".upper()):
                            self.Version = inboundVal
                        elif (inboundKey == "StatusCode".upper()):
                            self.StatusCode = inboundVal
                        elif (inboundKey == "Status".upper()):
                            self.Status = inboundVal

                nLineNumber = nLineNumber + 1

        self.save()

    def save(self):
        def nullify(empty):
            if empty == "":
                return "NULL"
            else:
                return empty

        self.JSONRequest = self.JSONRequest.replace("\n", "")
        (self.X_AspNetMvc_Version, self.X_AspNet_Version, self.StatusCode) = (
        nullify(self.X_AspNet_Version), nullify(self.X_AspNet_Version), nullify(self.StatusCode))

        # self.date is of the format
        # Tue, 13 Sep 2016 20:12:47 GMT
        gmt = pytz.timezone('GMT')
        eastern = pytz.timezone('US/Eastern')
        date = datetime.strptime(self.Date, '%a, %d %b %Y %H:%M:%S GMT')
        dategmt = gmt.localize(date)
        dateeastern = dategmt.astimezone(eastern)
        self.Date = datetime.strftime(dateeastern, '%Y-%m-%d %H:%M:%S')

        vals = (
        self.SID, self.Cache_Control, self.Content_Type, self.Content_Length, self.Server, self.X_AspNetMvc_Version,
        self.X_AspNet_Version, \
        self.X_SourceFiles, self.WWW_Authenticate, self.WWW_Authenticate2, self.X_Powered_By, self.Date,
        self.Proxy_Support, self.Response, self.Version, self.StatusCode, self.Status, self.JSONRequest)
        new_record = "INSERT INTO S (SID, Cache_Control, Content_Type, Content_Length, Server, X_AspNetMvc_Version, X_AspNet_Version, \
                      X_SourceFiles, WWW_Authenticate, WWW_Authenticate2, X_Powered_By, Date, Proxy_Support, Response, Version, StatusCode, Status, JSONRequest) \
                      VALUES ({0}, '{1}', '{2}', '{3}', '{4}', {5}, {6}, '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}', '{14}', '{15}', '{16}', '{17}')".format(
            *vals)

        new_record = new_record.replace("'NULL'", "NULL")

        log('\n' + new_record)

        try:
            ### self.conn.execute(new_record)
            ### self.conn.commit()
            dbCursor = self.conn.cursor()
            dbCursor.execute(new_record)
            dbCursor.commit()
        except pyodbc.DataError as e:
            log("--" + e.args[1])


class M:
    MID = ""
    ClientConnected = ""
    ClientBeginRequest = ""
    GotRequestHeaders = ""
    ClientDoneRequest = ""
    GatewayTime = ""
    DNSTime = ""
    TCPConnectTime = ""
    HTTPSHandshakeTime = ""
    ServerConnected = ""
    FiddlerBeginRequest = ""
    ServerGotRequest = ""
    ServerBeginResponse = ""
    GotResponseHeaders = ""
    ServerDoneResponse = ""
    ClientBeginResponse = ""
    ClientDoneResponse = ""
    x_egressport = ""
    x_responsebodytransferlength = ""
    x_clientport = ""
    x_clientip = ""
    x_serversocket = ""
    x_hostip = ""
    x_processinfo = ""

    def parse(self, file_name):
        def safe_wrapper(array, tag):
            try:
                return_value = array.attrs[tag.lower()]
                return return_value
            except Exception:
                return ''

        file_contents = file_get_contents(file_name)
        soup = BeautifulSoup(file_contents, "html.parser")

        # there's only one sesion timer
        sessionTimer = soup.find("sessiontimers")
        self.ClientConnected = safe_wrapper(sessionTimer, 'ClientConnected')
        self.ClientBeginRequest = safe_wrapper(sessionTimer, 'ClientBeginRequest')
        self.GotRequestHeaders = safe_wrapper(sessionTimer, 'GotRequestHeaders')
        self.ClientDoneRequest = safe_wrapper(sessionTimer, 'ClientDoneRequest')
        self.GatewayTime = safe_wrapper(sessionTimer, 'GatewayTime')
        self.DNSTime = safe_wrapper(sessionTimer, 'DNSTime')
        self.TCPConnectTime = safe_wrapper(sessionTimer, 'TCPConnectTime')
        self.HTTPSHandshakeTime = safe_wrapper(sessionTimer, 'HTTPSHandshakeTime')
        self.ServerConnected = safe_wrapper(sessionTimer, 'ServerConnected')
        self.FiddlerBeginRequest = safe_wrapper(sessionTimer, 'FiddlerBeginRequest')
        self.ServerGotRequest = safe_wrapper(sessionTimer, 'ServerGotRequest')
        self.ServerBeginResponse = safe_wrapper(sessionTimer, 'ServerBeginResponse')
        self.GotResponseHeaders = safe_wrapper(sessionTimer, 'GotResponseHeaders')
        self.ServerDoneResponse = safe_wrapper(sessionTimer, 'ServerDoneResponse')
        self.ClientBeginResponse = safe_wrapper(sessionTimer, 'ClientBeginResponse')
        self.ClientDoneResponse = safe_wrapper(sessionTimer, 'ClientDoneResponse')

        sessionFlags = soup.find("sessionflags")
        for sessionFlag in sessionFlags.findAll("sessionflag"):
            if (sessionFlag["n"] == 'x-egressport'):
                self.x_egressport = sessionFlag["v"]
            if (sessionFlag["n"] == 'x-responsebodytransferlength'):
                self.x_responsebodytransferlength = sessionFlag["v"]
            if (sessionFlag["n"] == 'x-clientport'):
                self.x_clientport = sessionFlag["v"]
            if (sessionFlag["n"] == 'x-clientip'):
                self.x_clientip = sessionFlag["v"]
            if (sessionFlag["n"] == 'x-serversocket'):
                self.x_serversocket = sessionFlag["v"]
            if (sessionFlag["n"] == 'x-hostip'):
                self.x_hostip = sessionFlag["v"]
            if (sessionFlag["n"] == 'x-processinfo'):
                self.x_processinfo = sessionFlag["v"]
        self.save()

    def save(self):
        def convertToDateTime(fiddlerDate):
            try:
                test_date_copy = fiddlerDate.replace("0", "")

                if (fiddlerDate == "" or test_date_copy == ""):
                    return 'NULL'

                if (fiddlerDate == '0001-01-01T00:00:00'):
                    return 'NULL'

                fiddlerDate_part1 = fiddlerDate.split(".")
                # fiddler uses 7 digits accuracy, SQL server likes 3:
                fiddlerDate_part1b = fiddlerDate_part1[1].split("-")[0][0:-4]
                fiddlerDate = ".".join([fiddlerDate_part1[0], fiddlerDate_part1b])
                fiddlerDate = " ".join(fiddlerDate.split("T"))  # replace the T with ''
                return fiddlerDate
            except Exception:
                return 'NULL'

        self.ClientConnected = convertToDateTime(self.ClientConnected)
        self.ClientBeginRequest = convertToDateTime(self.ClientBeginRequest)
        self.GotRequestHeaders = convertToDateTime(self.GotRequestHeaders)
        self.ClientDoneRequest = convertToDateTime(self.ClientDoneRequest)
        self.GatewayTime = convertToDateTime(self.GatewayTime)
        self.DNSTime = convertToDateTime(self.DNSTime)
        self.TCPConnectTime = convertToDateTime(self.TCPConnectTime)
        self.HTTPSHandshakeTime = convertToDateTime(self.HTTPSHandshakeTime)
        self.ServerConnected = convertToDateTime(self.ServerConnected)
        self.FiddlerBeginRequest = convertToDateTime(self.FiddlerBeginRequest)
        self.ServerGotRequest = convertToDateTime(self.ServerGotRequest)
        self.ServerBeginResponse = convertToDateTime(self.ServerBeginResponse)
        self.GotResponseHeaders = convertToDateTime(self.GotResponseHeaders)
        self.ServerDoneResponse = convertToDateTime(self.ServerDoneResponse)
        self.ClientBeginResponse = convertToDateTime(self.ClientBeginResponse)
        self.ClientDoneResponse = convertToDateTime(self.ClientDoneResponse)
        self.x_responsebodytransferlength = self.x_responsebodytransferlength.replace(",", "").strip()

        vals = (self.MID, self.ClientConnected, self.ClientBeginRequest, self.GotRequestHeaders, self.ClientDoneRequest,
                self.GatewayTime, self.DNSTime, self.TCPConnectTime, \
                self.HTTPSHandshakeTime, self.ServerConnected, self.FiddlerBeginRequest, self.ServerGotRequest,
                self.ServerBeginResponse, self.GotResponseHeaders, \
                self.ServerDoneResponse, self.ClientBeginResponse, self.ClientDoneResponse, self.x_egressport,
                self.x_responsebodytransferlength, self.x_clientport, \
                self.x_clientip, self.x_serversocket, self.x_hostip, self.x_processinfo)
        new_record = "INSERT INTO M (MID, ClientConnected, ClientBeginRequest, GotRequestHeaders, ClientDoneRequest, GatewayTime, DNSTime, TCPConnectTime, \
                        HTTPSHandshakeTime, ServerConnected, FiddlerBeginRequest, ServerGotRequest, ServerBeginResponse, GotResponseHeaders, \
                        ServerDoneResponse, ClientBeginResponse, ClientDoneResponse, x_egressport, x_responsebodytransferlength, x_clientport, \
                        x_clientip, x_serversocket, x_hostip, x_processinfo) \
                      VALUES ({0}, '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}', '{14}', '{15}', '{16}', \
                      '{17}', '{18}', '{19}', '{20}', '{21}', '{22}', '{23}')".format(*vals)

        new_record = new_record.replace("'NULL'", "NULL")
        log('\n' + new_record)

        try:
            ### self.conn.execute(new_record)
            ### self.conn.commit()
            dbCursor = self.conn.cursor()
            dbCursor.execute(new_record)
            dbCursor.commit()
        except pyodbc.DataError as e:
            log("--" + e.args[1])


def parseSaz(folder_name, file_name):
    # this folder should contain an HTML file
    # the database is named after the folder
    ### three pounds / hashes for SQLite3
    ### database = folder_name + ".db"
    ### bDBOK = checkDB(database)
    bDBOK = True
    colIdx = 0
    current_record = browsing_history()
    ### current_record.conn = sqlite3.connect(database)
    current_record.conn = pyodbc.connect(connStr)

    if (bDBOK):
        # in the file_name folder there is an _index.html
        _indexHTML = file_get_contents(folder_name + "/" + file_name)
        soup = BeautifulSoup(_indexHTML, 'html.parser')
        for col in soup.find_all('td'):
            hrefs = col.find_all('a')
            if (len(hrefs) > 0):
                # these files are found in the ./raw folder
                c = hrefs[0].attrs['href']
                s = hrefs[1].attrs['href']
                m = hrefs[2].attrs['href']
                current_record.CID = int("".join(re.findall(r'\d', c)))
                current_record.SID = int("".join(re.findall(r'\d', s)))
                current_record.MID = int("".join(re.findall(r'\d', m)))

                try:
                    # parse the 'C' file
                    c_rec = C()
                    c_rec.CID = current_record.CID
                    c_rec.conn = current_record.conn
                    C.parse(c_rec, file_name=folder_name + "\\" + c)
                except:
                    log("-- A 'c' record was passed: " + c)
                    pass

                try:
                    # parse the 'S' file
                    s_rec = S()
                    s_rec.SID = current_record.SID
                    s_rec.conn = current_record.conn
                    S.parse(s_rec, file_name=folder_name + "\\" + s)
                except:
                    log("-- An 's' record was passed: " + s)
                    pass

                try:
                    # parse the 'M' file
                    m_rec = M()
                    m_rec.MID = current_record.MID
                    m_rec.conn = current_record.conn
                    M.parse(m_rec, file_name=folder_name + "\\" + m)
                except:
                    log("-- An 'm' record was passed: " + m)
                    pass

                # this is the 0th col
                colIdx = 0
            else:
                #   #	Result	Protocol	Host	URL	Body	Caching	Content-Type	Process	Comments	Custom
                if (colIdx == 1):
                    current_record.ID = col.text
                elif (colIdx == 2):
                    current_record.Result = col.text
                elif (colIdx == 3):
                    current_record.Protocol = col.text
                elif (colIdx == 4):
                    current_record.Host = col.text
                elif (colIdx == 5):
                    current_record.URL = col.text
                elif (colIdx == 6):
                    current_record.Body = col.text
                elif (colIdx == 7):
                    current_record.Caching = col.text
                elif (colIdx == 8):
                    current_record.ContentType = col.text
                elif (colIdx == 9):
                    current_record.Process = col.text
                elif (colIdx == 10):
                    current_record.Comments = col.text
                elif (colIdx == 11):
                    current_record.Custom = col.text

            # parse next
            colIdx = colIdx + 1

            if (colIdx % 12 == 0):
                # flush this row to the db
                current_record.save()

        # now close the db
        current_record.conn.close()


if __name__ == '__main__':
    try:
        # default usage is at the same level as unzipped SAZ file
        saz_file = [i for i in os.listdir() if i[-3:] == 'saz'][0]
        test_folder = saz_file.lower().replace(".saz", "")

        # unzipped folder has to be top-level
        if (os.path.exists(test_folder)):
            parseSaz(folder_name=test_folder, file_name="_index.htm")
    except IndexError:
        print("No SAZ file was found.")
