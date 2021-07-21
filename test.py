import datetime

def check_leaves():
    '''
    This function has basic functionalities of checking leaves
    :params: None
    :return: morning_only(dict), evening_only(dict), full_day(dict)
    '''

    start_date = input()
    end_date = input()

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    conn = sqlite3.connect('ATTENDANCE.sqlite')
    cur = conn.cursor()

    try:
        cur.execute('SELECT DATE, SHIFT, ABSENTEES FROM ATTENDANCE WHERE DATE BETWEEN ? AND ?', start_date, end_date)
        result = cur.fetchall()
    except Exception as err:
        logger.info("Something went wrong while fetching the attendance")
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
                        full_day[each_date].append(each_person) # this should be in try and catch

                        # if full day is found. removing from morning and evening
                        morning_only.remove(each_person)
                        evening_only.remove(each_person)
                except Exception as err:
                    logger.error("Something went wrong while fetching the full day attendance")

        return morning_only, evening_only, full_day

check_leaves()
