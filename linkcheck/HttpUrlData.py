import httplib,urlparse,sys,base64,time
from UrlData import UrlData
from RobotsTxt import RobotsTxt
import Config,StringUtil

class HttpUrlData(UrlData):
    "Url link with http scheme"

    def checkConnection(self, config):
        """
        Check a URL with HTTP protocol.
        Here is an excerpt from RFC 1945 with common response codes:
        The first digit of the Status-Code defines the class of response. The
        last two digits do not have any categorization role. There are 5
        values for the first digit:
        o 1xx: Informational - Not used, but reserved for future use
        o 2xx: Success - The action was successfully received,
          understood, and accepted.
        o 3xx: Redirection - Further action must be taken in order to
          complete the request
        o 4xx: Client Error - The request contains bad syntax or cannot
          be fulfilled
        o 5xx: Server Error - The server failed to fulfill an apparently
        valid request
        The individual values of the numeric status codes defined for
        HTTP/1.0, and an example set of corresponding Reason-Phrase's, are
        presented below. The reason phrases listed here are only recommended
        -- they may be replaced by local equivalents without affecting the
        protocol. These codes are fully defined in Section 9.
        Status-Code    = "200"   ; OK
        | "201"   ; Created
        | "202"   ; Accepted
        | "204"   ; No Content
        | "301"   ; Moved Permanently
        | "302"   ; Moved Temporarily
        | "304"   ; Not Modified
        | "400"   ; Bad Request
        | "401"   ; Unauthorized
        | "403"   ; Forbidden
        | "404"   ; Not Found
        | "500"   ; Internal Server Error
        | "501"   ; Not Implemented
        | "502"   ; Bad Gateway
        | "503"   ; Service Unavailable
        | extension-code
        """
        
        self.mime = None
        self.auth = None
        self.proxy = config["proxy"]
        self.proxyport = config["proxyport"]
        if config["robotstxt"] and not self.robotsTxtAllowsUrl(config):
            self.setWarning("Access denied by robots.txt, checked only syntax")
            return
            
        status, statusText, self.mime = self.getHttpRequest()
        Config.debug(str(self.mime))
        if status == 401:
            self.auth = base64.encodestring(LinkChecker.User+":"+LinkChecker.Password)
            status, statusText, self.mime = self.getHttpRequest()
        if status >= 400:
            self.setError(`status`+" "+statusText)
            return

        # follow redirections and set self.url to the effective url
        tries = 0
        redirected = self.urlName
        while status in [301,302] and self.mime and tries < 5:
            redirected = urlparse.urljoin(redirected, self.mime.getheader("Location"))
            self.urlTuple = urlparse.urlparse(redirected)
            status, statusText, self.mime = self.getHttpRequest()
            Config.debug("\nRedirected\n"+str(self.mime))
            tries = tries + 1
    
        effectiveurl = urlparse.urlunparse(self.urlTuple)
        if self.url != effectiveurl:
            self.setWarning("Effective URL "+effectiveurl)
            self.url = effectiveurl
        
        # check final result
        if status == 204:
            self.setWarning(statusText)
        if status >= 400:
            self.setError(`status`+" "+statusText)
        else:
            self.setValid(`status`+" "+statusText)

        
    def getHttpRequest(self, method="HEAD"):
        "Put request and return (status code, status text, mime object)"
        if self.proxy:
            host = self.proxy+":"+`self.proxyport`
        else:
            host = self.urlTuple[1]
        if self.urlConnection:
            self.closeConnection()
        self.urlConnection = httplib.HTTP(host)
        if self.proxy:
            path = urlparse.urlunparse(self.urlTuple)
        else:
            path = self.urlTuple[2]
            if self.urlTuple[3] != "":
                path = path + ";" + self.urlTuple[3]
            if self.urlTuple[4] != "":
                path = path + "?" + self.urlTuple[4]
        self.urlConnection.putrequest(method, path)
        if self.auth:
            self.urlConnection.putheader("Authorization", "Basic "+self.auth)
        self.urlConnection.putheader("User-agent", Config.UserAgent)
        self.urlConnection.endheaders()
        return self.urlConnection.getreply()

    def getContent(self):
        self.closeConnection()
        t = time.time()
        self.getHttpRequest("GET")
        self.urlConnection = self.urlConnection.getfile()
        data = StringUtil.stripHtmlComments(self.urlConnection.read())
        self.time = time.time() - t
        return data
        
    def isHtml(self):
        if self.mime:
            return self.valid and self.mime.gettype()=="text/html"
        return 0

    def robotsTxtAllowsUrl(self, config):
        try:
            if config.robotsTxtCache_has_key(self.urlTuple[1]):
                robotsTxt = config.robotsTxtCache_get(self.urlTuple[1])
            else:
                robotsTxt = RobotsTxt(self.urlTuple[1], Config.UserAgent)
                Config.debug("DEBUG: "+str(robotsTxt)+"\n")
                config.robotsTxtCache_set(self.urlTuple[1], robotsTxt)
        except:
            type, value = sys.exc_info()[:2]
            Config.debug("Heieiei: "+str(value)+"\n")
            return 1
        return robotsTxt.allowance(Config.UserAgent, self.urlTuple[2])


    def __str__(self):
        return "HTTP link\n"+UrlData.__str__(self)

    def closeConnection(self):
        if self.mime:
            try: self.mime.close()
            except: pass
            self.mime = None
        UrlData.closeConnection(self)
