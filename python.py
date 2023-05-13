import os
import datetime
import time

result = os.popen("wg show wg0 dump | tail -n +2").readlines()

for line in result:
    result_line_list = line.split("\t")
    print(result_line_list[5])
    now = datetime.datetime.now()
    last_seen = datetime.datetime.fromtimestamp(int(result_line_list[4]))
    d1_ts = time.mktime(now.timetuple())
    d2_ts = time.mktime(last_seen.timetuple())
    minutes_diff = (d1_ts - d2_ts) / 60
    print(now, last_seen, now-last_seen, minutes_diff)
    if minutes_diff > 5:
        print("cocou")