# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2005  Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Base URL handler.
"""

import sys
import os
import urlparse
import urllib2
import urllib
import time
import traceback
import socket
import select
import codecs

import linkcheck
import linkcheck.linkparse
import linkcheck.strformat
import linkcheck.containers
import linkcheck.log
import linkcheck.httplib2
import linkcheck.HtmlParser.htmlsax


stderr = codecs.getwriter("iso8859-1")(sys.stderr, errors="ignore")

def internal_error ():
    """
    Print internal error message to stderr.
    """
    print >> stderr, os.linesep
    print >> stderr, _("""********** Oops, I did it again. *************

You have found an internal error in LinkChecker. Please write a bug report
at http://sourceforge.net/tracker/?func=add&group_id=1913&atid=101913
or send mail to %s and include the following information:
- the URL or file you are testing
- your commandline arguments and/or configuration.
- the output of a debug run with option "-Dall" of the executed command
- the system information below.

Disclosing some of the information above due to privacy reasons is ok.
I will try to help you nonetheless, but you have to give me something
I can work with ;) .
""") % linkcheck.configuration.Email
    etype, value = sys.exc_info()[:2]
    print >> stderr, etype, value
    traceback.print_exc()
    print_app_info()
    print >> stderr, os.linesep, \
            _("******** LinkChecker internal error, over and out ********")
    sys.exit(1)


def print_app_info ():
    """
    Print system and application info to stderr.
    """
    print >> stderr, _("System info:")
    print >> stderr, linkcheck.configuration.App
    print >> stderr, _("Python %s on %s") % (sys.version, sys.platform)
    for key in ("LC_ALL", "LC_MESSAGES",  "http_proxy", "ftp_proxy"):
        value = os.getenv(key)
        if value is not None:
            print >> stderr, key, "=", repr(value)


def urljoin (parent, url, scheme):
    """
    If url is relative, join parent and url. Else leave url as-is.

    @return join url
    """
    if url.startswith(scheme+":"):
        return url
    return urlparse.urljoin(parent, url)


class UrlBase (object):
    """
    An URL with additional information like validity etc.
    """

    def __init__ (self, base_url, recursion_level, consumer,
                  parent_url = None, base_ref = None,
                  line = -1, column = -1, name = u""):
        """
        Initialize check data, and store given variables.

        @param base_url: unquoted and possibly unnormed url
        @param recursion_level: on what check level lies the base url
        @param consumer: consumer instance
        @param parent_url: quoted and normed url of parent or None
        @param base_ref: quoted and normed url of <base href=""> or None
        @param line: line number of url in parent content
        @param column: column number of url in parent content
        @param name: name of url or empty
        """
        self.base_ref = base_ref
        # note that self.base_url must not be modified
        self.base_url = base_url
        self.parent_url = parent_url
        self.recursion_level = recursion_level
        self.consumer = consumer
        self.line = line
        self.column = column
        self.name = name
        if self.base_ref:
            assert not linkcheck.url.url_needs_quoting(self.base_ref), \
                   "unquoted %r" % self.base_ref
        if self.parent_url:
            assert not linkcheck.url.url_needs_quoting(self.parent_url), \
                   "unquoted %r" % self.parent_url
        url = linkcheck.checker.absolute_url(base_url, base_ref, parent_url)
        # assume file link if no scheme is found
        self.scheme = url.split(":", 1)[0] or "file"

        # self.url is constructed by self.build_url() out of base_url
        # and (base_ref or parent) as absolute and normed url.
        # This the real url we use when checking so it also referred to
        # as 'real url'
        self.url = None
        # a splitted version of url for convenience
        self.urlparts = None
        # the anchor part of url
        self.anchor = None
        # the result message string
        self.result = u""
        # cached or not
        self.cached = False
        # valid or not
        self.valid = True
        # list of warnings (without duplicates)
        self.warning = linkcheck.containers.SetList()
        # list of infos (without duplicates)
        self.info = linkcheck.containers.SetList()
        # download time
        self.dltime = -1
        # download size
        self.dlsize = -1
        # check time
        self.checktime = 0
        # connection object
        self.url_connection = None
        self.extern = (1, 0)
        # data of url content
        self.data = None
        # if data is filled
        self.has_content = False
        # cache keys, are set by build_url() calling set_cache_keys()
        self.cache_url_key = None
        self.cache_content_key = None
        # Store a list of aliases since the same resource can be known
        # under several URLs. This is used for example on HTTP 30[12]
        # redirections.
        # Note that aliases are saved as-is, not through the cache-key-
        # generating method set_cache_keys().
        self.aliases = []

    def set_result (self, msg, valid=True):
        """
        Set result string and validity.
        """
        self.result = msg
        self.valid = valid

    def is_parseable (self):
        """
        Return True iff content of this url is parseable.
        """
        return False

    def is_html (self):
        """
        Return True iff content of this url is HTML formatted.
        """
        return False

    def is_http (self):
        """
        Return True for http:// URLs.
        """
        return False

    def is_file (self):
        """
        Return True for file:// URLs.
        """
        return False

    def add_warning (self, s):
        """
        Add a warning string.
        """
        self.warning.append(s)

    def add_info (self, s):
        """
        Add an info string.
        """
        self.info.append(s)

    def copy_from_cache (self, cache_data):
        """
        Fill attributes from cache data.
        """
        self.result = cache_data["result"]
        self.warning.extend(cache_data["warning"])
        self.info.extend(cache_data["info"])
        self.valid = cache_data["valid"]
        self.dltime = cache_data["dltime"]
        self.dlsize = cache_data["dlsize"]
        self.cached = True

    def get_cache_data (self):
        """
        Return all data values that should be put in the cache.
        """
        return {"result": self.result,
                "warning": self.warning,
                "info": self.info,
                "valid": self.valid,
                "dltime": self.dltime,
                "dlsize": self.dlsize,
               }

    def set_cache_keys (self):
        """
        Set keys for URL checking and content recursion.
        """
        # remove anchor from content cache key since we assume
        # URLs with different anchors to have the same content
        self.cache_content_key = urlparse.urlunsplit(self.urlparts[:4]+[u''])
        assert isinstance(self.cache_content_key, unicode), self
        linkcheck.log.debug(linkcheck.LOG_CACHE, "Content cache key %r",
                            self.cache_content_key)
        # construct cache key
        if self.consumer.config["anchorcaching"] and \
           self.consumer.config["anchors"]:
            # do not ignore anchor
            parts = self.urlparts[:]
            parts[4] = self.anchor
            if self.userinfo:
                parts[1] = self.userinfo+u"@"+parts[1]
            self.cache_url_key = urlparse.urlunsplit(parts)
        else:
            # no anchor caching
            self.cache_url_key = self.cache_content_key
        assert isinstance(self.cache_url_key, unicode), self
        linkcheck.log.debug(linkcheck.LOG_CACHE, "URL cache key %r",
                            self.cache_url_key)

    def check_syntax (self):
        """
        Called before self.check(), this function inspects the
        url syntax. Success enables further checking, failure
        immediately logs this url. Syntax checks must not
        use any network resources.
        """
        linkcheck.log.debug(linkcheck.LOG_CHECK, "checking syntax")
        if not self.base_url:
            self.set_result(_("URL is empty"), valid=False)
            return False
        try:
            self.build_url()
            # check url warnings
            effectiveurl = urlparse.urlunsplit(self.urlparts)
            if self.url != effectiveurl:
                self.add_warning(_("Effective URL %s.") % effectiveurl)
                self.url = effectiveurl
        except linkcheck.LinkCheckerError, msg:
            self.set_result(linkcheck.strformat.unicode_safe(msg),
                            valid=False)
            return False
        self.set_cache_keys()
        self.extern = self._get_extern(self.url)
        return True

    def build_url (self):
        """
        Construct self.url and self.urlparts out of the given base
        url information self.base_url, self.parent_url and self.base_ref.
        """
        # norm base url
        base_url, is_idn = linkcheck.url.url_norm(self.base_url)
        if is_idn:
            self.add_warning(_("""URL %s has a unicode domain name which
                          is not yet widely supported. You should use
                          the URL %s instead.""") % (self.base_url, base_url))
        elif self.base_url != base_url:
            self.add_warning(
              _("Base URL is not properly normed. Normed url is %(url)s.") % \
               {'url': base_url})
        # make url absolute
        if self.base_ref:
            # use base reference as parent url
            if ":" not in self.base_ref:
                # some websites have a relative base reference
                self.base_ref = urljoin(self.parent_url, self.base_ref,
                                        self.scheme)
            self.url = urljoin(self.base_ref, base_url, self.scheme)
        elif self.parent_url:
            self.url = urljoin(self.parent_url, base_url, self.scheme)
        else:
            self.url = base_url
        # split into (modifiable) list
        self.urlparts = linkcheck.strformat.url_unicode_split(self.url)
        # and unsplit again
        self.url = urlparse.urlunsplit(self.urlparts)
        # check userinfo@host:port syntax
        self.userinfo, host = urllib.splituser(self.urlparts[1])
        # set host lowercase and without userinfo
        self.urlparts[1] = host.lower()
        # safe anchor for later checking
        self.anchor = self.urlparts[4]
        self.host, self.port = urllib.splitport(host)
        if self.port is not None:
            if not linkcheck.url.is_numeric_port(self.port):
                raise linkcheck.LinkCheckerError, \
                         _("URL has invalid port %r") % str(self.port)
            self.port = int(self.port)

    def check (self):
        """
        Main check function for checking this URL.
        """
        try:
            self.local_check()
            self.consumer.checked(self)
        except (socket.error, select.error):
            self.consumer.interrupted(self)
            # on Unix, ctrl-c can raise
            # error: (4, 'Interrupted system call')
            etype, value = sys.exc_info()[:2]
            if etype == 4:
                raise KeyboardInterrupt, value
            else:
                raise
        except KeyboardInterrupt:
            self.consumer.interrupted(self)
            raise
        except:
            self.consumer.interrupted(self)
            internal_error()

    def add_country_info (self):
        """
        Try to ask GeoIP database for country info.
        """
        country = self.consumer.get_country_name(self.host)
        if country is not None:
            self.add_info(_("URL is located in %s.") % _(country))

    def local_check (self):
        """
        Local check function can be overridden in subclasses.
        """
        linkcheck.log.debug(linkcheck.LOG_CHECK, "Checking %s", self)
        if self.recursion_level and self.consumer.config['wait']:
            linkcheck.log.debug(linkcheck.LOG_CHECK,
                                "sleeping for %d seconds",
                                self.consumer.config['wait'])
            time.sleep(self.consumer.config['wait'])
        t = time.time()
        if self.is_extern():
            self.add_info(_("Outside of domain filter, checked only syntax."))
            return

        # check connection
        linkcheck.log.debug(linkcheck.LOG_CHECK, "checking connection")
        try:
            self.check_connection()
            self.add_country_info()
            if self.consumer.config["anchors"]:
                self.check_anchors()
        except tuple(linkcheck.checker.ExcList):
            etype, evalue, etb = sys.exc_info()
            linkcheck.log.debug(linkcheck.LOG_CHECK, "exception %s",
                                traceback.format_tb(etb))
            # make nicer error msg for unknown hosts
            if isinstance(evalue, socket.error) and evalue[0] == -2:
                evalue = _('Hostname not found')
            # make nicer error msg for bad status line
            if isinstance(evalue, linkcheck.httplib2.BadStatusLine):
                evalue = _('Bad HTTP response %r') % str(evalue)
            self.set_result(linkcheck.strformat.unicode_safe(evalue),
                            valid=False)

        # check content
        warningregex = self.consumer.config["warningregex"]
        if warningregex and self.valid:
            linkcheck.log.debug(linkcheck.LOG_CHECK, "checking content")
            try:
                self.check_content(warningregex)
            except tuple(linkcheck.checker.ExcList):
                value, tb = sys.exc_info()[1:]
                linkcheck.log.debug(linkcheck.LOG_CHECK, "exception %s",
                                    traceback.format_tb(tb))
                self.set_result(linkcheck.strformat.unicode_safe(value),
                                valid=False)

        self.checktime = time.time() - t
        # check recursion
        linkcheck.log.debug(linkcheck.LOG_CHECK, "checking recursion...")
        try:
            if self.allows_recursion():
                self.parse_url()
            else:
                linkcheck.log.debug(linkcheck.LOG_CHECK, "...no recursion")
            # check content size
            self.check_size()
        except tuple(linkcheck.checker.ExcList):
            value, tb = sys.exc_info()[1:]
            linkcheck.log.debug(linkcheck.LOG_CHECK, "exception %s",
                                traceback.format_tb(tb))
            self.set_result(_("could not parse content: %r") % str(value),
                            valid=False)
        # close
        self.close_connection()

    def close_connection (self):
        """
        Close an opened url connection.
        """
        if self.url_connection is None:
            # no connection is open
            return
        try:
            self.url_connection.close()
        except:
            # ignore close errors
            pass
        self.url_connection = None

    def check_connection (self):
        """
        The basic connection check uses urllib2.urlopen to initialize
        a connection object.
        """
        self.url_connection = urllib2.urlopen(self.url)

    def allows_recursion (self):
        """
        Return True iff we can recurse into the url's content.
        """
        #linkcheck.log.debug(linkcheck.LOG_CHECK, "valid=%s, parseable=%s, "\
        #                    "content=%s, extern=%s, robots=%s",
        #                    self.valid, self.is_parseable(),
        #                    self.can_get_content(),
        #                    self.extern[0],
        #                    self.content_allows_robots())
        # note: test self.valid before self.is_parseable()
        return self.valid and \
            self.is_parseable() and \
            self.can_get_content() and \
            (self.consumer.config["recursionlevel"] < 0 or
            self.recursion_level < self.consumer.config["recursionlevel"]) and \
            not self.extern[0] and self.content_allows_robots()

    def content_allows_robots (self):
        """
        Return True if the content of this URL forbids robots to
        search for recursive links.
        """
        if not self.is_html():
            return True
        if not (self.is_http() or self.is_file()):
            return True
        h = linkcheck.linkparse.MetaRobotsFinder(self.get_content())
        p = linkcheck.HtmlParser.htmlsax.parser(h)
        h.parser = p
        p.feed(self.get_content())
        p.flush()
        h.parser = None
        p.handler = None
        return h.follow

    def check_anchors (self):
        """
        If URL was valid and a HTML resource, check the anchors and
        log a warning when an anchor was not found.
        """
        if not (self.valid and self.anchor and self.is_html() and \
                self.can_get_content()):
            # do not bother
            return
        linkcheck.log.debug(linkcheck.LOG_CHECK, "checking anchor %r",
                            self.anchor)
        h = linkcheck.linkparse.LinkFinder(self.get_content(),
                                   tags={'a': [u'name'], None: [u'id']})
        p = linkcheck.HtmlParser.htmlsax.parser(h)
        h.parser = p
        p.feed(self.get_content())
        p.flush()
        h.parser = None
        p.handler = None
        for cur_anchor, line, column, name, base in h.urls:
            if cur_anchor == self.anchor:
                return
        self.add_warning(_("Anchor #%s not found.") % self.anchor)

    def is_extern (self):
        """
        Determine if this URL is extern or not.

        @return: True if URL is extern, else False
        @rtype: bool
        """
        linkcheck.log.debug(linkcheck.LOG_CHECK, "extern=%s", self.extern)
        return self.extern[0] and \
           (self.consumer.config["externstrictall"] or self.extern[1])

    def _get_extern (self, url):
        """
        Match URL against intern and extern link patterns, according
        to the configured denyallow order.

        @return: a tuple (is_extern, is_strict)
        @rtype: tuple (bool, bool)
        """
        if not (self.consumer.config["externlinks"] or \
           self.consumer.config["internlinks"]):
            return (0, 0)
        # deny and allow external checking
        linkcheck.log.debug(linkcheck.LOG_CHECK, "Url %r", url)
        if self.consumer.config["denyallow"]:
            for entry in self.consumer.config["externlinks"]:
                linkcheck.log.debug(linkcheck.LOG_CHECK, "Extern entry %r",
                                    entry)
                match = entry['pattern'].search(url)
                if (entry['negate'] and not match) or \
                   (match and not entry['negate']):
                    return (1, entry['strict'])
            for entry in self.consumer.config["internlinks"]:
                linkcheck.log.debug(linkcheck.LOG_CHECK, "Intern entry %r",
                                    entry)
                match = entry['pattern'].search(url)
                if (entry['negate'] and not match) or \
                   (match and not entry['negate']):
                    return (0, 0)
            return (0, 0)
        else:
            for entry in self.consumer.config["internlinks"]:
                linkcheck.log.debug(linkcheck.LOG_CHECK, "Intern entry %r",
                                    entry)
                match = entry['pattern'].search(url)
                if (entry['negate'] and not match) or \
                   (match and not entry['negate']):
                    return (0, 0)
            for entry in self.consumer.config["externlinks"]:
                linkcheck.log.debug(linkcheck.LOG_CHECK, "Extern entry %r",
                                    entry)
                match = entry['pattern'].search(url)
                if (entry['negate'] and not match) or \
                   (match and not entry['negate']):
                    return (1, entry['strict'])
            return (1, 0)

    def can_get_content (self):
        """
        Indicate wether url get_content() can be called.
        """
        return True

    def get_content (self):
        """
        Precondition: url_connection is an opened URL.
        """
        if not self.has_content:
            t = time.time()
            self.data = self.url_connection.read()
            self.dltime = time.time() - t
            self.dlsize = len(self.data)
            self.has_content = True
        return self.data

    def check_content (self, warningregex):
        """
        If a warning expression was given, call this function to check it
        against the content of this url.
        """
        if not self.can_get_content():
            return
        match = warningregex.search(self.get_content())
        if match:
            self.add_warning(_("Found %r in link contents.") % match.group())

    def check_size (self):
        """
        If a maximum size was given, call this function to check it
        against the content size of this url.
        """
        maxbytes = self.consumer.config["warnsizebytes"]
        if maxbytes is not None and self.dlsize >= maxbytes:
            self.add_warning(_("Content size %s is larger than %s.") % \
                         (linkcheck.strformat.strsize(self.dlsize),
                          linkcheck.strformat.strsize(maxbytes)))

    def parse_url (self):
        """
        Parse url content and search for recursive links.
        Default parse type is html.
        """
        linkcheck.log.debug(linkcheck.LOG_CHECK,
                            "Parsing recursively into %s", self)
        self.parse_html()

    def get_user_password (self):
        """
        Get tuple (user, password) from configured authentication.
        Both user and password can be None if not specified.
        """
        for auth in self.consumer.config["authentication"]:
            if auth['pattern'].match(self.url):
                return auth['user'], auth['password']
        return None, None

    def parse_html (self):
        """
        Parse into HTML content and search for URLs to check.
        Found URLs are added to the URL queue.
        """
        h = linkcheck.linkparse.LinkFinder(self.get_content())
        p = linkcheck.HtmlParser.htmlsax.parser(h)
        h.parser = p
        p.feed(self.get_content())
        p.flush()
        h.parser = None
        p.handler = None
        for s in h.parse_info:
            # the parser had warnings/errors
            self.add_warning(s)
        for url, line, column, name, codebase in h.urls:
            if codebase:
                base_ref = codebase
            else:
                base_ref = h.base_ref
            url_data = linkcheck.checker.get_url_from(url,
                  self.recursion_level+1, self.consumer, parent_url=self.url,
                  base_ref=base_ref, line=line, column=column, name=name)
            self.consumer.append_url(url_data)

    def parse_opera (self):
        """
        Parse an opera bookmark file.
        """
        name = ""
        lineno = 0
        lines = self.get_content().splitlines()
        for line in lines:
            lineno += 1
            line = line.strip()
            if line.startswith("NAME="):
                name = line[5:]
            elif line.startswith("URL="):
                url = line[4:]
                if url:
                    url_data = linkcheck.checker.get_url_from(url,
                              self.recursion_level+1, self.consumer,
                              parent_url=self.url, line=lineno, name=name)
                    self.consumer.append_url(url_data)
                name = ""

    def parse_text (self):
        """
        Parse a text file with on url per line; comment and blank
        lines are ignored.
        """
        lineno = 0
        for line in self.get_content().splitlines():
            lineno += 1
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            url_data = linkcheck.checker.get_url_from(line,
                              self.recursion_level+1, self.consumer,
                              parent_url=self.url, line=lineno)
            self.consumer.append_url(url_data)

    def parse_css (self):
        """
        Parse a CSS file for url() patterns.
        """
        lineno = 0
        for line in self.get_content().splitlines():
            lineno += 1
            for mo in linkcheck.linkparse.css_url_re.finditer(line):
                column = mo.start("url")
                url = linkcheck.strformat.unquote(mo.group("url").strip())
                url_data = linkcheck.checker.get_url_from(url,
                             self.recursion_level+1, self.consumer,
                             parent_url=self.url, line=lineno, column=column)
                self.consumer.append_url(url_data)

    def serialized (self):
        """
        Return serialized url check data as unicode string.
        """
        sep = linkcheck.strformat.unicode_safe(os.linesep)
        assert isinstance(self.base_url, unicode), self
        if self.parent_url is not None:
            assert isinstance(self.parent_url, unicode), self
        if self.base_ref is not None:
            assert isinstance(self.base_ref, unicode), self
        assert isinstance(self.name, unicode), self
        return sep.join([
            u"%s link" % self.scheme,
            u"base_url=%r" % self.base_url,
            u"parent_url=%r" % self.parent_url,
            u"base_ref=%r" % self.base_ref,
            u"recursion_level=%s" % self.recursion_level,
            u"url_connection=%s" % self.url_connection,
            u"line=%d" % self.line,
            u"column=%d" % self.column,
            u"name=%r" % self.name,
           ])

    def __str__ (self):
        """
        Get URL info.

        @return: URL info, encoded with the output logger encoding
        @rtype: string
        """
        s = self.serialized()
        return self.consumer.config['logger'].encode(s)

    def __repr__ (self):
        """
        Get URL info.

        @return: URL info
        @rtype: unicode
        """
        return u"<%s >" % self.serialized()
