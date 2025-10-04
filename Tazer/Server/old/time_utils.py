from datetime import datetime, time as dtime, date

def parse_hhmm(s:str)->dtime:
    h,m = s.split(":"); return dtime(int(h), int(m))
def now_time()->dtime: return datetime.now().time()
def passed(target:str, now=None)->bool:
    return (now or now_time()) >= parse_hhmm(target)
def today_id()->str: return date.today().isoformat()
