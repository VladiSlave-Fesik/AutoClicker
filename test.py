def format_milliseconds(milliseconds):
    if len(milliseconds) > 3:
        milliseconds = milliseconds[:3] + '.' + milliseconds[3:]
    elif len(milliseconds) < 3:
        milliseconds = f'{milliseconds:03d}'
    return milliseconds


def time_to_seconds(time_: str):
    h, m, s = map(int, time_.split(':')[:-1])
    ms = float(time_.split(':')[-1])
    seconds = (h * 3600) + (m * 60) + s + (ms / 1000)
    return seconds


hour = 0
minute = 0
second = 0
s = '001'
millisecond = format_milliseconds(s)
time = f'{hour}:{minute}:{second}:{millisecond}'
print(time)

print(time_to_seconds(time))
