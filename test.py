import datetime
import sqlite3
def check_leaves():

    start_date = "2021-07-18"
    end_date = "2021-07-21"

    conn = sqlite3.connect('Attendance_DB.sqlite')
    cur = conn.cursor()

    result = None
    try:
        cur.execute("SELECT DATE, SHIFT, ABSENTEES FROM Attendance_table WHERE DATE BETWEEN ? AND ?",(str(start_date), str(end_date)))
        result = cur.fetchall()
    except Exception as err:
        print("Exception caught")
        pass

    morning_only, evening_only, full_day = {}, {}, {}
    selected_dates = []
    for each in result:
        if each[1] == "M":
            morning_only[each[0]] = each[2]
        elif each[1] == "E":
            evening_only[each[0]] = each[2]
        selected_dates.append(each[0])

    selected_dates = set(selected_dates) # For finding unique dates
    for each_date in selected_dates:
        for each_person in morning_only[each_date]:
            try:
                if each_person in evening_only[each_date]:
                    value=list(full_day[each_date])
                    value.append(each_person)
                    full_day[each_date]=str(value)
            except Exception as e:
                pass
                
    #            full_day[each_date].append(each_person) # this should be in try and catch
    print("Morning:"+ str(morning_only))
    print("Evening:" + str(evening_only))
    print("Full day:" + str(full_day))

check_leaves()
