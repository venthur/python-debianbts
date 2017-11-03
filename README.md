# python-debianbts

Python-debianbts is a Python library that allows for querying Debian's [Bug
Tracking System](https://bugs.debian.org). Since 2011, python-debianbts is used
by Debian's `reportbug` to query the Bug Tracking System and has currently
(2017-11) roughly [190.000 installations](https://qa.debian.org/popcon.php?package=python-debianbts).

Python-debianbts is Python2 and Python3 compatible.


## Installing

```bash
pip install python-debianbts
```


## Quickstart

```python
>>> import debianbts as bts

>>> bts.get_bugs('package', 'python-debianbts')
[803900, 787723, 824111, 639458, 726878, 722226, 789047]

>>> bts.get_tatus(803900, 787723)
[<debianbts.debianbts.Bugreport at 0x7f47080d8c10>,
 <debianbts.debianbts.Bugreport at 0x7f47080d80d0>]

>>> for b in bts.get_status(803900, 787723):
        print(b)
fixed_versions: [u'python-debianbts/1.13']
blockedby: []
done: True
unarchived: True
owner:
subject: reportbug: crashes when querying Debian BTS for reports on wnpp
archived: False
forwarded: https://github.com/venthur/python-debianbts/pull/5
bug_num: 787723
msgid: <20150604130538.GA16742@debian.org>
source: python-debianbts
location: db-h
pending: done
originator: Antonio Terceiro <terceiro@debian.org>
blocks: []
tags: [u'fixed-upstream', u'patch', u'jessie']
date: 2015-06-04 13:09:02
mergedwith: [722226, 726878, 789047]
severity: important
package: python-debianbts
summary:
log_modified: 2016-12-07 01:36:36
found_versions: []
affects: []

fixed_versions: [u'python-debianbts/2.0']
blockedby: []
done: False
unarchived: False
owner:
subject: reportbug errors out with SOAP error
archived: False
forwarded:
bug_num: 803900
msgid: <20151103013542.11170.31413.reportbug@cheddar.halon.org.uk>
source: python-debianbts
location: db-h
pending: pending
originator: Wookey <wookey@debian.org>
blocks: []
tags: []
date: 2015-11-03 01:39:01
mergedwith: []
severity: normal
package: python-debianbts
summary:
log_modified: 2015-11-03 08:36:04
found_versions: []
affects: []
```
