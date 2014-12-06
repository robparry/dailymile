# read DailyMile training data and print statistics
import csv
import sys, getopt, os.path
from datetime import date, timedelta

def main(argv):
    """ read dailymile CSV file and parse """
    csv_file = r'/home/rparry/Downloads/dailymile.training.csv'
    d = {}  # data dictionary: [date] : [activity] : [count] : distance / time / felt
    e = {}  # data dictionary: [activity] : [date] : [count] : distance / time /felt
    stats = {} # stats dictionary: [activity] : farthest / fastest
    stat_time_frame = 'all'   # valid: week / month / year / all / YYYY-MM-DD
    today = date.today()

    try:
        opts, args = getopt.getopt(argv,"hi:s:", ["ifile=", "stat="])
    except getopt.GetoptError:
        print 'training.py [-i <inputfile> -s <stat_time_frame]'
    for opt, arg in opts:
        if opt == '-h':
            print 'training.py -i <input_file> -s <stat_time_frame>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            csv_file = arg
        elif opt in ("-s", "--stat"):
            stat_time_frame = arg

    # check if file exists
    if not os.path.exists(csv_file):
        print "file [%s] does not exist" % csv_file
        sys.exit(1)
        
    # default stat time frame to all - 9999 days ago
    date2 = today - timedelta(days=9999)
    if stat_time_frame == 'week':
        date2 = today - timedelta(days=7)
    elif stat_time_frame == 'month':
        date2 = today - timedelta(days=30)
    elif stat_time_frame == 'year':
        date2 = today - timedelta(days=365)
    elif '-' in stat_time_frame:
        # see if got a date, deal with possibilities
        toto = stat_time_frame.split('-')
        if len(toto) == 3:
            try:
                date2 = date(int(toto[0]), int(toto[1]), int(toto[2]))
            except ValueError:
                print 'not a valid date. format is: YYYY-MM-DD'
                sys.exit(1)
        else:
            print 'not a valid date. format is: YYYY-MM-DD'
            sys.exit(1)

    if date2 > today:
        print 'not able to compute statistics for future events'
        sys.exit(1)
    
    print 'Input file is: %s' % csv_file
    earliest_date = today

    with open(csv_file, 'r') as csvfile:
        data = csv.reader(csvfile,delimiter=',')
        for row in data:
            # print ', '.join(row)
            # fields: date,activity_type,distance,time,felt
            if (row[0].startswith('date') == False):
                # make a datetime.date object out of current date string
                date3 = date_to_date_obj(row[0])
                # only progress if processing a date more current than time frame
                if (date3 > date2):
                    # find and save earliest date
                    if date3 < earliest_date:
                        earliest_date = date3
                    # convert meters to miles, field could be blank
                    miles = 0.0
                    if len(row[2]) > 0:
                        miles = float(row[2]) / 1609.34
                    # convert time to minutes, field could be blank
                    time_min = 0.0
                    if len(row[3]) > 0:
                        time_min = float(row[3]) / 60.0
                    pace = 0.0
                    if miles > 0.0:
                        pace = time_min / miles

                    # create nested dictionary if has not been seen before
                    if not d.has_key(row[0]): d[row[0]] = {}
                    if not e.has_key(row[1]): e[row[1]] = {}
                    # stats has key of activity
                    if not stats.has_key(row[1]):
                        stats[row[1]] = {}
                        stats[row[1]]['fastest'] = {}
                        stats[row[1]]['fastest']['pace'] = 999.0
                        stats[row[1]]['fastest']['time'] = 0.0
                        stats[row[1]]['fastest']['date'] = 'no date'
                        stats[row[1]]['fastest']['distance'] = 0.0
                        stats[row[1]]['farthest'] = {}
                        stats[row[1]]['farthest']['distance'] = 0.0
                        stats[row[1]]['farthest']['date'] = 'no date'
                        stats[row[1]]['cumm_time'] = 0.0
                        stats[row[1]]['cumm_dist'] = 0.0
                    # first dictionary d has key of activity
                    if d[row[0]].has_key(row[1]):
                        activity_count = len(d[row[0]][row[1]].keys()) + 1
                        # print 'd duplicate: ' + row[0] + ': ' + row[1] + ': activity_count: ' + str(activity_count) + ': ' + str(time_min)
                        d[row[0]][row[1]][activity_count] = {}
                        d[row[0]][row[1]][activity_count].update({'distance': miles})
                        d[row[0]][row[1]][activity_count].update({'time': time_min})
                        d[row[0]][row[1]][activity_count].update({'felt': row[4]})
                        d[row[0]][row[1]][activity_count].update({'pace': pace})
                    else:
                        # print row[0] + ': ' + row[1] + ': ' + str(miles) + ': ' + str(time_min)
                        count = 1
                        d[row[0]][row[1]] = {}
                        d[row[0]][row[1]][count] = {}
                        d[row[0]][row[1]][count].update({'distance': miles})
                        d[row[0]][row[1]][count].update({'time': time_min})
                        d[row[0]][row[1]][count].update({'felt': row[4]})
                        d[row[0]][row[1]][count].update({'pace': pace})
                    # then dictionary e has primary key activity, second key date
                    if e[row[1]].has_key(row[0]):
                        activity_count = len(e[row[1]][row[0]].keys()) + 1
                        # print 'e duplicate: ' + row[0] + ': ' + row[1] + ': activity_count: ' + str(activity_count) + ': ' + str(time_min)
                        e[row[1]][row[0]][activity_count] = {}
                        e[row[1]][row[0]][activity_count].update({'distance': miles})
                        e[row[1]][row[0]][activity_count].update({'time': time_min})
                        stats[row[1]]['cumm_time'] = stats[row[1]]['cumm_time'] + (time_min / 60.0)
                        e[row[1]][row[0]][activity_count].update({'felt': row[4]})
                        e[row[1]][row[0]][activity_count].update({'pace': pace})
                    else:
                        # print row[0] + ': ' + row[1] + ': ' + str(miles) + ': ' + str(time_min)
                        count = 1
                        e[row[1]][row[0]] = {}
                        e[row[1]][row[0]][count] = {}
                        stats[row[1]]['cumm_time'] = stats[row[1]]['cumm_time'] + (time_min / 60.0)
                        stats[row[1]]['cumm_dist'] = stats[row[1]]['cumm_dist'] + miles
                        e[row[1]][row[0]][count].update({'distance': miles})
                        e[row[1]][row[0]][count].update({'time': time_min})
                        e[row[1]][row[0]][count].update({'felt': row[4]})
                        e[row[1]][row[0]][count].update({'pace': pace})
                    if (pace > 0.0) and (pace < stats[row[1]]['fastest']['pace']):
                        stats[row[1]]['fastest']['pace'] = pace
                        stats[row[1]]['fastest']['date'] = row[0]
                        stats[row[1]]['fastest']['time'] = time_min
                        stats[row[1]]['fastest']['distance'] = miles
                    if miles >= stats[row[1]]['farthest']['distance']:
                        stats[row[1]]['farthest']['distance'] = miles
                        stats[row[1]]['farthest']['date'] = row[0]
                        stats[row[1]]['farthest']['pace'] = pace
                        stats[row[1]]['farthest']['time'] = time_min


    print 'Stats time frame [%s] from earliest date [%s] to today' % (stat_time_frame, str(earliest_date))
    print '\n>>>> activity totals for stat period [' + stat_time_frame + '] :'
    e_sum = {}
    total_workouts = 0
    total_time = 0.0
    total_distance = 0.0
    for a in e.keys():
        e_sum[a] = 0
        for k in e[a].keys():
            e_sum[a] +=  len(e[a][k].keys())
            total_workouts += len(e[a][k].keys())

    for a in stats.keys():
        total_distance += stats[a]['cumm_dist']
        total_time += stats[a]['cumm_time']
        
    for a in e_sum.keys():
        print '%10s: %d workouts, total distance %.2f miles, total time %.2f hours' % \
              (a, e_sum[a], stats[a]['cumm_dist'], stats[a]['cumm_time'])
    print '  == total: %d workouts, total distance %.2f miles, total time %.2f hours' % \
          (total_workouts, total_distance, total_time)

    print '\n>>>> stats by activity for stat period [' + stat_time_frame + '] :'
    for k in stats.keys():
        found_data = False
        if (stats[k]['fastest']['pace'] > 0.0) and (stats[k]['fastest']['pace'] < 999.0):
            print '%10s:  fastest: %s on %10s (minutes: %.2f miles: %.2f)' % \
            (k, format_pace(stats[k]['fastest']['pace']), stats[k]['fastest']['date'],
             stats[k]['fastest']['time'], stats[k]['fastest']['distance'])
            found_data = True
        if stats[k]['farthest']['distance'] > 0.0:
            print '%10s: farthest: %5.2f on %10s (minutes: %.2f pace: %s)' % \
            (k, stats[k]['farthest']['distance'], stats[k]['farthest']['date'],
             stats[k]['farthest']['time'], format_pace(stats[k]['farthest']['pace']))
            found_data = True
             
        if found_data:
            print '-' * 10

def date_to_date_obj(str_date):
    """ use date passed to function to return a date object """
    d_split = str_date.split('/')
    return date(int(d_split[2]), int(d_split[0]), int(d_split[1]))

def format_pace(pace):
    """ convert pace from fraction of minute to minute:seconds """
    minutes = int(pace)
    seconds = (pace - minutes) * 60.0
    return "%d:%2.2d" % (minutes, seconds)

if __name__ == "__main__":
   main(sys.argv[1:])
