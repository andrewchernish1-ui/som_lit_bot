#!/usr/bin/expect -f

set timeout 30
spawn ssh root@95.215.8.138
expect "password:"
send "sq8Iff0x3eXYL5\r"
interact
