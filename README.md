# python-debianbts

Python-debianbts is a Python library that allows for querying Debian's [Bug
Tracking System](https://bugs.debian.org). Since 2011, python-debianbts is used
by Debian's `reportbug` to query the Bug Tracking System and has currently
(2017-11) roughly [190.000 installations](https://qa.debian.org/popcon.php?package=python-debianbts).


## Installing

```bash
pip install python-debianbts
```


## Quickstart

```python
>>> import debianbts as bts

>>> bts.get_bugs(package='python-debianbts')
[803900, 787723, 824111, 639458, 726878, 722226, 789047]

>>> bts.get_status([803900, 787723])
[<debianbts.debianbts.Bugreport at 0x7f47080d8c10>,
 <debianbts.debianbts.Bugreport at 0x7f47080d80d0>]

>>> for b in bts.get_status([803900, 787723]):
...     print(b)
...
originator: Antonio Terceiro <terceiro@debian.org>
date: 2015-06-04 13:09:02
subject: reportbug: crashes when querying Debian BTS for reports on wnpp
msgid: <20150604130538.GA16742@debian.org>
package: python-debianbts
tags: ['fixed-upstream', 'patch', 'jessie']
done: True
forwarded: https://github.com/venthur/python-debianbts/pull/5
mergedwith: [722226, 726878, 789047]
severity: important
owner: 
found_versions: []
fixed_versions: ['python-debianbts/1.13']
blocks: []
blockedby: []
unarchived: True
summary: 
affects: []
log_modified: 2019-07-08 07:27:36
location: archive
archived: True
bug_num: 787723
source: python-debianbts
pending: done
done_by: Bastian Venthur <venthur@debian.org>

originator: Wookey <wookey@debian.org>
date: 2015-11-03 01:39:01
subject: reportbug errors out with SOAP error
msgid: <20151103013542.11170.31413.reportbug@cheddar.halon.org.uk>
package: python-debianbts
tags: []
done: False
forwarded: 
mergedwith: []
severity: normal
owner: 
found_versions: []
fixed_versions: ['python-debianbts/2.0']
blocks: []
blockedby: []
unarchived: False
summary: 
affects: []
log_modified: 2015-11-03 08:36:04
location: db-h
archived: False
bug_num: 803900
source: python-debianbts
pending: pending
done_by: None
```
