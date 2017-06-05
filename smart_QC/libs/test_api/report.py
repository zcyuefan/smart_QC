#!/usr/bin/env python
# encoding=utf-8

# Author zhangchao@jinwantai.com
# date:2017/5/31
# topic: 
# update:

from __future__ import unicode_literals
import traceback
__version__ = "0.0.1"

import datetime
import StringIO
import sys
import time
import unittest
from xml.sax import saxutils
"""
A TestRunner for use with the Python unit testing framework. It generates a HTML report to show the result at a glance.

The simplest way to use this is to invoke its main method. E.g.

    import unittest
    import BSTestRunner

    ... define your tests ...

    if __name__ == '__main__':
        BSTestRunner.main()


For more customization options, instantiates a BSTestRunner object.
BSTestRunner is a counterpart to unittest's TextTestRunner. E.g.

    # output to a file
    fp = file('my_report.html', 'wb')
    runner = BSTestRunner.BSTestRunner(
                stream=fp,
                title='My unit test',
                description='This demonstrates the report output by BSTestRunner.'
                )

    # Use an external stylesheet.
    # See the Template_mixin class for more customizable options
    runner.STYLESHEET_TMPL = '<link rel="stylesheet" href="my_stylesheet.css" type="text/css">'

    # run the test
    runner.run(my_test_suite)


------------------------------------------------------------------------
Copyright (c) 2004-2007, Wai Yip Tung
Copyright (c) 2016, Eason Han
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.
* Neither the name Wai Yip Tung nor the names of its contributors may be
  used to endorse or promote products derived from this software without
  specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# ------------------------------------------------------------------------
# The redirectors below are used to capture output during testing. Output
# sent to sys.stdout and sys.stderr are automatically captured. However
# in some cases sys.stdout is already cached before BSTestRunner is
# invoked (e.g. calling logging.basicConfig). In order to capture those
# output, use the redirectors for the cached stream.
#
# e.g.
#   >>> logging.basicConfig(stream=BSTestRunner.stdout_redirector)
#   >>>

def to_unicode(s):
    try:
        return unicode(s)
    except UnicodeDecodeError:
        # s is non ascii byte string
        return s.decode('unicode_escape')

class OutputRedirector(object):
    """ Wrapper to redirect stdout or stderr """
    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(to_unicode(s))

    def writelines(self, lines):
        lines = map(to_unicode, lines)
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()

stdout_redirector = OutputRedirector(sys.stdout)
stderr_redirector = OutputRedirector(sys.stderr)



# ----------------------------------------------------------------------
# Template

class Template_mixin(object):
    """
    Define a HTML template for report customerization and generation.

    Overall structure of an HTML report

    HTML
    +------------------------+
    |<html>                  |
    |  <head>                |
    |                        |
    |   STYLESHEET           |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </head>               |
    |                        |
    |  <body>                |
    |                        |
    |   HEADING              |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   REPORT               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   ENDING               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </body>               |
    |</html>                 |
    +------------------------+
    """

    STATUS = {
    0: 'pass',
    1: 'fail',
    2: 'error',
    }

    DEFAULT_TITLE = 'Unit Test Report'
    DEFAULT_DESCRIPTION = ''

    # ------------------------------------------------------------------------
    # HTML Template

    HTML_TMPL = r"""<!DOCTYPE html>
<html lang="zh-cn">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <title>%(title)s</title>
    <meta name="generator" content="%(generator)s"/>
    <link rel="stylesheet" href="http://cdn.bootcss.com/bootstrap/3.3.0/css/bootstrap.min.css">
    %(stylesheet)s

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="http://cdn.bootcss.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="http://cdn.bootcss.com/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>
<body>
<script language="javascript" type="text/javascript"><!--
output_list = Array();

/* level - 0:Summary; 1:Failed; 2:All */
function showCase(level) {
    trs = document.getElementsByTagName("tr");
    for (var i = 0; i < trs.length; i++) {
        tr = trs[i];
        id = tr.id;
        if (id.substr(0,2) == 'ft') {
            if (level < 1) {
                tr.className = 'hiddenRow';
            }
            else {
                tr.className = '';
            }
        }
        if (id.substr(0,2) == 'pt') {
            if (level > 1) {
                tr.className = '';
            }
            else {
                tr.className = 'hiddenRow';
            }
        }
    }
}


function showClassDetail(cid){
    var toHide = 1;
    var tr = document.evaluate("//tr[contains(@id,'"+'t' + cid.substr(1) + '.'+"')]", document.documentElement, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
    if (tr){
        if (tr.snapshotItem(0).className) {
            toHide = 0;
        }
        for (var i=0, len=tr.snapshotLength; i < len; i++) {
        tid=tr.snapshotItem(i).id;
        //alert(tid);
        if (toHide) {
            if(document.getElementById('div_'+tid)){
            document.getElementById('div_'+tid).style.display = 'none'
            }
            document.getElementById(tid).className = 'hiddenRow';
        }
        else {
            document.getElementById(tid).className = '';
        }
        }
    }
}


function showTestDetail(tid){
    var toHide = 1;
    var test_step = document.evaluate("//tr[starts-with(@id,'"+tid+".')]", document.documentElement, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
    if (test_step){
        if (test_step.snapshotItem(0).className) {
            toHide = 0;
        }
        for (var i=0, len=test_step.snapshotLength; i < len; i++) {
        sid=test_step.snapshotItem(i).id;
        if (toHide) {
            if(document.getElementById('div_'+tid)){
            document.getElementById('div_'+tid).style.display = 'none'
            }
            document.getElementById(sid).className = 'hiddenRow';
        }
        else {
            document.getElementById(sid).className = '';
        }
        }
    }
}


function showStepDetail(div_id){
    var details_div = document.getElementById(div_id);
    var displayState = details_div.style.display;
    // alert(displayState)
    if (displayState != 'block' ) {
        displayState = 'block';
        details_div.style.display = 'block';
    }
    else {
        details_div.style.display = 'none';
    }
}


function html_escape(s) {
    s = s.replace(/&/g,'&amp;');
    s = s.replace(/</g,'&lt;');
    s = s.replace(/>/g,'&gt;');
    return s;
}

/* obsoleted by detail in <div>
function showOutput(id, name) {
    var w = window.open("", //url
                    name,
                    "resizable,scrollbars,status,width=800,height=450");
    d = w.document;
    d.write("<pre>");
    d.write(html_escape(output_list[id]));
    d.write("\n");
    d.write("<a href='javascript:window.close()'>close</a>\n");
    d.write("</pre>\n");
    d.close();
}
*/
--></script>

<div class="container">
    %(heading)s
    %(report)s
    %(ending)s
</div>

</body>
</html>
"""
    # variables: (title, generator, stylesheet, heading, report, ending)


    # ------------------------------------------------------------------------
    # Stylesheet
    #
    # alternatively use a <link> for external style sheet, e.g.
    #   <link rel="stylesheet" href="$url" type="text/css">

    STYLESHEET_TMPL = """
<style type="text/css" media="screen">

/* -- css div popup ------------------------------------------------------------------------ */
.popup_window {
    display: none;
    position: relative;
    left: 0px;
    top: 0px;
    /*border: solid #627173 1px; */
    padding: 10px;
    background-color: #99CCFF;
    font-family: "Lucida Console", "Courier New", Courier, monospace;
    text-align: left;
    font-size: 10pt;
    width: 500px;
}

/* -- report ------------------------------------------------------------------------ */

#show_detail_line .label {
    font-size: 85%;
    cursor: pointer;
}

#show_detail_line {
    margin: 2em auto 1em auto;
}

#total_row  { font-weight: bold; }
.hiddenRow  { display: none; }
.testcase   { margin-left: 2em; }

</style>
"""



    # ------------------------------------------------------------------------
    # Heading
    #

    HEADING_TMPL = """<div class='heading'>
<h1>%(title)s</h1>
%(parameters)s
<p class='description'>%(description)s</p>
</div>

""" # variables: (title, parameters, description)

    HEADING_ATTRIBUTE_TMPL = """<p><strong>%(name)s:</strong> %(value)s</p>
""" # variables: (name, value)



    # ------------------------------------------------------------------------
    # Report
    #

    REPORT_TMPL = """
<p id='show_detail_line'>
<span class="label label-primary" onclick="showCase(0)">Summary</span>
<span class="label label-danger" onclick="showCase(1)">Failed</span>
<span class="label label-default" onclick="showCase(2)">All</span>
</p>
<table id='result_table' class="table">
    <thead>
        <tr id='header_row'>
            <th>Test Group/Test case/Test step</td>
            <th>Count</td>
            <th>Pass</td>
            <th>Fail</td>
            <th>Error</td>
            <th>View</td>
        </tr>
    </thead>
    <tbody>
        %(test_list)s
    </tbody>
    <tfoot>
        <tr id='total_row'>
            <td>Total</td>
            <td>%(count)s</td>
            <td class="text text-success">%(Pass)s</td>
            <td class="text text-danger">%(fail)s</td>
            <td class="text text-warning">%(error)s</td>
            <td>&nbsp;</td>
        </tr>
    </tfoot>
</table>
""" # variables: (test_list, count, Pass, fail, error)

    REPORT_CLASS_TMPL = r"""
<tr class='%(style)s'>
    <td>%(desc)s</td>
    <td>%(count)s</td>
    <td>%(Pass)s</td>
    <td>%(fail)s</td>
    <td>%(error)s</td>
    <td><a class="btn btn-xs btn-primary"href="javascript:showClassDetail('%(cid)s',%(count)s)">Detail</a></td>
</tr>
""" # variables: (style, desc, count, Pass, fail, error, cid)


    REPORT_TEST_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s' onclick="javascript:showTestDetail('%(tid)s')" style="cursor:pointer;"><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'>

    <!--css div popup start-->
    <a class="btn btn-xs %(btn_class)s" >
        %(status)s</a>
    <!--css div popup end-->

    </td>
</tr>
""" # variables: (tid, Class, btn_class, style, desc, status)

    REPORT_STEP_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s' onclick="javascript:showStepDetail('div_%(tid)s')" style="cursor:pointer;"><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'>

    <!--css div popup start-->
    <a class="btn btn-xs %(btn_class)s" >
        %(status)s</a>

    <div id='div_%(tid)s' class="popup_window">
        <div style='text-align: right;cursor:pointer'>
        </div>
        <pre>
        %(script)s
        </pre>
    </div>
    <!--css div popup end-->

    </td>
</tr>
""" # variables: (tid, Class, btn_class, style, desc, status)

#     REPORT_TEST_NO_OUTPUT_TMPL = r"""
# <tr id='%(tid)s' class='%(Class)s'>
#     <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
#     <td colspan='5' align='center'>%(status)s</td>
# </tr>
# """ # variables: (tid, Class, style, desc, status)


    REPORT_TEST_OUTPUT_TMPL = r"""
%(id)s: %(output)s
""" # variables: (id, output)



    # ------------------------------------------------------------------------
    # ENDING
    #

    ENDING_TMPL = """<div id='ending'>&nbsp;</div>"""

# -------------------- The end of the Template class -------------------

STDOUT_LINE = '\nStdout:\n%s'
STDERR_LINE = '\nStderr:\n%s'


class TestResult(object):

    def __init__(self):
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.current_case = CaseResult()

        # result is a list of result in 2 tuple
        # (
        #   result code (0: success; 1: fail; 2: error),
        #   CaseResult object,
        # )
        self.result = []

    def add_result(self):
        if self.current_case.status == 0:
            self.success_count += 1
            self.result.append((0, self.current_case))
        elif self.current_case.status == 1:
            self.failure_count += 1
            self.result.append((1, self.current_case))
        elif self.current_case.status == 1:
            self.error_count += 1
            self.result.append((2, self.current_case))
        else:
            pass


class CaseResult(object):
    def __init__(self, verbosity=1):
        self.outputBuffer = StringIO.StringIO()
        self.stdout0 = None
        self.stderr0 = None
        self.verbosity = verbosity
        self.buffer = False
        self.errors = []
        self.failures = []
        self.status = 4  # not run

        # result is a list of result in 4 tuple
        # (
        #   result code (0: success; 1: fail; 2: error),
        #   Step object,
        #   Test output (byte string),
        #   stack trace,
        # )
        self.result = []

    def start_step(self):
        # just one buffer for both stdout and stderr
        stdout_redirector.fp = self.outputBuffer
        stderr_redirector.fp = self.outputBuffer
        self.stdout0 = sys.stdout
        self.stderr0 = sys.stderr
        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector

    def complete_output(self):
        """
        Disconnect output redirection and return buffer.
        Safe to call multiple times.
        """
        if self.stdout0:
            sys.stdout = self.stdout0
            sys.stderr = self.stderr0
            self.stdout0 = None
            self.stderr0 = None
        return self.outputBuffer.getvalue()

    def stop_step(self):
        self.complete_output()

    def add_success(self, step, output):
        output += self.complete_output()
        self.result.append((0, step, output, ''))
        if self.status == 4:
            self.status = 0
        if self.verbosity > 1:
            sys.stderr.write('ok ')
            sys.stderr.write(str(step))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('.')

    def add_error(self, step, err):
        self.errors.append((step, self._exc_info_to_string(err, step)))
        _, _exc_str = self.errors[-1]
        output = self.complete_output()
        self.result.append((2, step, output, _exc_str))
        self.status = 2
        if self.verbosity > 1:
            sys.stderr.write('E  ')
            sys.stderr.write(str(step))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('E')

    def add_failure(self, step, err):
        self.failures.append((step, self._exc_info_to_string(err, step)))
        _, _exc_str = self.failures[-1]
        output = self.complete_output()
        self.result.append((1, step, output, _exc_str))
        if self.status in (0, 4):
            self.status = 1
        if self.verbosity > 1:
            sys.stderr.write('F  ')
            sys.stderr.write(str(step))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('F')

    def _exc_info_to_string(self, err, step):
        """Converts a sys.exc_info()-style tuple of values into a string."""
        exctype, value, tb = err
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next

        if exctype is step.failureException:
            # Skip assert*() traceback levels
            length = self._count_relevant_tb_levels(tb)
            msgLines = traceback.format_exception(exctype, value, tb, length)
        else:
            msgLines = traceback.format_exception(exctype, value, tb)

        if self.buffer:
            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
            if output:
                if not output.endswith('\n'):
                    output += '\n'
                msgLines.append(STDOUT_LINE % output)
            if error:
                if not error.endswith('\n'):
                    error += '\n'
                msgLines.append(STDERR_LINE % error)
        return ''.join(msgLines)

    def _is_relevant_tb_level(self, tb):
        return '__unittest' in tb.tb_frame.f_globals

    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        return length


class TestReport(Template_mixin):
    """
    """

    def __init__(self, stream=sys.stdout, verbosity=1, title=None, description=None):
        self.stream = stream
        self.verbosity = verbosity
        if title is None:
            self.title = self.DEFAULT_TITLE
        else:
            self.title = title
        if description is None:
            self.description = self.DEFAULT_DESCRIPTION
        else:
            self.description = description

        self.startTime = datetime.datetime.now()

    def run(self):
        pass

    # def run(self, test):
    #     "Run the given test case or test suite."
    #     result = TestResult(self.verbosity)
    #     test(result)
    #     self.stopTime = datetime.datetime.now()
    #     self.generateReport(result)
    #     print >> sys.stderr, '\nTime Elapsed: %s' % (self.stopTime - self.startTime)
    #     return result

    # def sortResult(self, result_list):
    #     # unittest does not seems to run in any particular order.
    #     # Here at least we want to group them together by class.
    #     rmap = {}
    #     classes = []
    #     for n, t, o, e in result_list:
    #         cls = t.__class__
    #         if not rmap.has_key(cls):
    #             rmap[cls] = []
    #             classes.append(cls)
    #         rmap[cls].append((n, t, o, e))
    #     r = [(cls, rmap[cls]) for cls in classes]
    #     return r

    def getReportAttributes(self, result):
        """
        Return report attributes as a list of (name, value).
        Override this to add custom attributes.
        """
        startTime = str(self.startTime)[:19]
        duration = str(self.stopTime - self.startTime)
        status = []
        if result.success_count: status.append(
            '<span class="text text-success">Pass <strong>%s</strong></span>' % result.success_count)
        if result.failure_count: status.append(
            '<span class="text text-danger">Failure <strong>%s</strong></span>' % result.failure_count)
        if result.error_count:   status.append(
            '<span class="text text-warning">Error <strong>%s</strong></span>' % result.error_count)
        if status:
            status = ' '.join(status)
        else:
            status = 'none'
        return [
            ('Start Time', startTime),
            ('Duration', duration),
            ('Status', status),
        ]

    def generateReport(self, result):
        self.stopTime = datetime.datetime.now()
        report_attrs = self.getReportAttributes(result)
        generator = 'Smart_QC %s' % __version__
        stylesheet = self._generate_stylesheet()
        heading = self._generate_heading(report_attrs)
        report = self._generate_report(result)
        ending = self._generate_ending()
        output = self.HTML_TMPL % dict(
            title=saxutils.escape(self.title),
            generator=generator,
            stylesheet=stylesheet,
            heading=heading,
            report=report,
            ending=ending,
        )
        self.stream.write(output.encode('utf8'))

    def _generate_stylesheet(self):
        return self.STYLESHEET_TMPL

    def _generate_heading(self, report_attrs):
        a_lines = []
        for name, value in report_attrs:
            line = self.HEADING_ATTRIBUTE_TMPL % dict(
                # name = saxutils.escape(name),
                # value = saxutils.escape(value),
                name=name,
                value=value,
            )
            a_lines.append(line)
        heading = self.HEADING_TMPL % dict(
            title=saxutils.escape(self.title),
            parameters=''.join(a_lines),
            description=saxutils.escape(self.description),
        )
        return heading

    def _generate_report(self, result):
        rows = []
        # sortedResult = self.sortResult(result.result)
        # for cid, (cls, cls_results) in enumerate(sortedResult):
        for cid, (cls, cls_results) in enumerate(result.result):
            # subtotal for a class
            np = nf = ne = 0
            for n, t, o, e in cls_results:
                if n == 0:
                    np += 1
                elif n == 1:
                    nf += 1
                else:
                    ne += 1

            # format class description
            if cls.__module__ == "__main__":
                name = cls.__name__
            else:
                name = "%s.%s" % (cls.__module__, cls.__name__)
            doc = cls.__doc__ and cls.__doc__.split("\n")[0] or ""
            desc = doc and '%s: %s' % (name, doc) or name

            row = self.REPORT_CLASS_TMPL % dict(
                style=ne > 0 and 'text text-warning' or nf > 0 and 'text text-danger' or 'text text-success',
                desc=desc,
                count=np + nf + ne,
                Pass=np,
                fail=nf,
                error=ne,
                cid='c%s' % (cid + 1),
            )
            rows.append(row)

            for tid, (n, t, o, e) in enumerate(cls_results):
                self._generate_report_test(rows, cid, tid, n, t, o, e)

        report = self.REPORT_TMPL % dict(
            test_list=''.join(rows),
            count=str(result.success_count + result.failure_count + result.error_count),
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
        )
        return report

    def _generate_report_test(self, rows, cid, tid, n, t, o, e):
        # e.g. 'pt1.1', 'ft1.1', etc
        tid = (n == 0 and 'p' or 'f') + 't%s.%s' % (cid + 1, tid + 1)
        name = t.id().split('.')[-1]
        doc = t.shortDescription() or ""
        desc = doc and ('%s: %s' % (name, doc)) or name

        # o and e should be byte string because they are collected from stdout and stderr?
        if isinstance(o, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # uo = unicode(o.encode('string_escape'))
            uo = o.decode('latin-1')
        else:
            uo = o
        if isinstance(e, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # ue = unicode(e.encode('string_escape'))
            ue = e.decode('latin-1')
        else:
            ue = e

        script = self.REPORT_TEST_OUTPUT_TMPL % dict(
            id=tid,
            output=saxutils.escape(uo + ue),
        )

        row = self.REPORT_TEST_TMPL % dict(
            tid=tid,
            # Class = (n == 0 and 'hiddenRow' or 'none'),
            Class=(n == 0 and 'hiddenRow' or 'text text-success'),
            btn_class=n == 2 and 'btn-danger' or (n == 1 and 'btn-warning' or 'btn-success'),
            # style = n == 2 and 'errorCase' or (n == 1 and 'failCase' or 'none'),
            style=n == 2 and 'text text-warning' or (n == 1 and 'text text-danger' or 'text text-success'),
            desc=desc,
            script=script,
            status=self.STATUS[n],
        )
        rows.append(row)
        for sid, (n, t, o, e) in enumerate(step_results):
            self._generate_report_step(rows, cid, tid, sid, n, t, o, e)

    def _generate_report_step(self, rows, cid, tid, n, t, o, e):
        # e.g. 'pt1.1', 'ft1.1', etc
        has_output = bool(o or e)
        tid = (n == 0 and 'p' or 'f') + 't%s.%s' % (cid + 1, tid + 1)
        name = t.id().split('.')[-1]
        doc = t.shortDescription() or ""
        desc = doc and ('%s: %s' % (name, doc)) or name
        tmpl = has_output and self.REPORT_TEST_WITH_OUTPUT_TMPL or self.REPORT_TEST_NO_OUTPUT_TMPL

        # o and e should be byte string because they are collected from stdout and stderr?
        if isinstance(o, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # uo = unicode(o.encode('string_escape'))
            uo = o.decode('latin-1')
        else:
            uo = o
        if isinstance(e, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # ue = unicode(e.encode('string_escape'))
            ue = e.decode('latin-1')
        else:
            ue = e

        script = self.REPORT_TEST_OUTPUT_TMPL % dict(
            id=tid,
            output=saxutils.escape(uo + ue),
        )

        row = tmpl % dict(
            tid=tid,
            # Class = (n == 0 and 'hiddenRow' or 'none'),
            Class=(n == 0 and 'hiddenRow' or 'text text-success'),
            btn_class=n == 2 and 'btn-danger' or (n == 1 and 'btn-warning' or 'btn-success'),
            # style = n == 2 and 'errorCase' or (n == 1 and 'failCase' or 'none'),
            style=n == 2 and 'text text-warning' or (n == 1 and 'text text-danger' or 'text text-success'),
            desc=desc,
            script=script,
            status=self.STATUS[n],
        )
        rows.append(row)
        if not has_output:
            return

    def _generate_ending(self):
        return self.ENDING_TMPL
