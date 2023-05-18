def time_to_seconds(time_: str):
    h, m, s, ms = map(int, time_.split(':'))
    seconds = (h * 3600) + (m * 60) + s + (ms / 1000)
    return seconds


print(time_to_seconds('12:34:56:789'))
