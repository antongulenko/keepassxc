#!/usr/bin/python3

#
# Copyright (C) 2013 Felix Geyer <debfx@fobos.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 or (at your option)
# version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#
# Parses keysymdef.h to construct a unicode symbol -> keysym mapping table.
#
# The lines that are parsed look like this:
# #define XK_Aogonek 0x01a1  /* U+0104 LATIN CAPITAL LETTER A WITH OGONEK */
#
# This would create a 0x0104 -> 0x01a1 mapping.
#

import sys
import re
import collections

cols = 8

if len(sys.argv) >= 2:
    keysymdef = sys.argv[1]
else:
    keysymdef = "/usr/include/X11/keysymdef.h"

keysymMap = {}

f = open(keysymdef, "r")
for line in f:
    match = re.search(r'0x([0-9a-fA-F]+)\s+/\* U\+([0-9a-fA-F]+)', line)
    if match:
        keysym = int(match.group(1), 16)
        unicodeVal = int(match.group(2), 16)

        # ignore 1:1 mappings
        if keysym >= 0x0020 and keysym <= 0x007e:
            continue
        if keysym >= 0x00a0 and keysym <= 0x00ff:
            continue
        # ignore unicode | 0x01000000 mappings
        if keysym >= 0x1000000:
            continue

        keysymMap[unicodeVal] = keysym

keysymMap = collections.OrderedDict(sorted(keysymMap.items(), key=lambda t: t[0]))

print("""/*
 *  Automatically generated by keysymmap.py from parsing keysymdef.h.
 */
""")

print("const int AutoTypePlatformX11::m_unicodeToKeysymLen = " + str(len(keysymMap)) + ";")

print()

print("const uint AutoTypePlatformX11::m_unicodeToKeysymKeys[] = {")
keys = keysymMap.keys()
keyLen = len(keys)
i = 1
for val in keys:
    hexVal = "{0:#0{1}x}".format(val, 6)

    if i == keyLen:
        print(hexVal)
    elif (i % cols) == 0:
        print(hexVal + ",")
    elif ((i - 1) % cols) == 0:
        print("    " + hexVal + ", ", end="")
    else:
        print(hexVal + ", ", end="")
    i += 1
print("};")

print()

print("const uint AutoTypePlatformX11::m_unicodeToKeysymValues[] = {")
values = keysymMap.values()
valuesLen = len(values)
i = 1
for val in values:
    hexVal = "{0:#0{1}x}".format(val, 6)

    if i == valuesLen:
        print(hexVal)
    elif (i % cols) == 0:
        print(hexVal + ",")
    elif ((i - 1) % cols) == 0:
        print("    " + hexVal + ", ", end="")
    else:
        print(hexVal + ", ", end="")
    i += 1
print("};")
