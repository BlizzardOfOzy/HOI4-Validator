from codecs import open
import sys
from os import listdir
import time
import os
import re



def check_triggered(line_number, lines):
    if line_number == len(lines) or line_number == len(lines)-1 or line_number == len(lines)-2 :
        return True
    if '}' in lines[line_number+2] or 'days' in lines[line_number+2]:
        #print("1: Found Triggered Event at line: " + line_number.__str__())
        return True
    if '}' in lines[line_number+1] or 'days' in lines[line_number+1]:
        #print("1: Found Triggered Event at line: " + line_number.__str__())
        return True
    if '}' in lines[line_number] or 'days' in lines[line_number]:
        #print("1: Found Triggered Event at line: " + line_number.__str__())
        return True
    for i in range(line_number, len(lines)):
        string = lines[i].strip()
        if string.startswith('#') is True:
            continue
        if string.startswith('}') is True or 'days' in string:
            #print("2: Found Triggered Event at line: " + i.__str__())
            return True
        elif string != "":
            #print("3: Found normal Event at line: " + i.__str__())
            return False
    return False


def focus(cpath):
    ttime = 0
    #immediate = {log = "Focus id: "+ id + "\n"}  # autolog
    for filename in listdir(cpath + "\\common\\national_focus"):
        if ".txt" in filename:
            file = open(cpath + "\\common\\national_focus\\" + filename, 'r', 'utf-8')
            size = os.path.getsize(cpath + "\\common\\national_focus\\" + filename)
            if size < 100:
                continue
            lines = file.readlines()
            line_number = 0
            ids = []
            idss = []
            new_focus = False
            find_coml = False
            timestart = time.time()
            for line in lines:
                line_number += 1
                if line.strip().startswith('#'):
                    continue
                if '#' in line:
                    line = line.split('#')[0]
                if 'focus = {' in line:  # New Event
                    new_focus = True
                    if find_coml is True:
                        find_coml = False
                        ids.pop()
                if line.strip().startswith('id') and new_focus is True:
                        new_focus = False
                        find_coml = True
                        focus_id = line.split('=')[1].strip()
                        if '#' in focus_id:
                            focus_id = focus_id.split('#')[0].strip()
                        ids.append(focus_id)
                if 'completion_reward' in line and find_coml is True:
                        find_coml = False
                        idss.append(line_number)
                if 'log = "[GetDateText]:' in line:
                    if  idss != [] or ids != []:
                        idss.pop()
                        ids.pop()
            time1 = time.time() - timestart
            line_number = 0

            outputfile = open(cpath + "\\common\\national_focus\\" + filename, 'w', 'utf-8')
            outputfile.truncate()
            for line in lines:
                line_number += 1
                if line_number in idss:
                    focus_id = ids[idss.index(line_number)]
                    if focus_id in ["{", "}"]:
                        focus_id = "Error, focus name not found"
                    if '}' in line:
                        temp = line.split("{")
                        replacement_text = temp[0] + "{\n\n\t\t\tlog = \"[GetDateText]: [Root.GetName]: Focus " + focus_id + "\"\n" + "{".join(temp)[len(temp[0])+1:] + "\n"
                    else:
                        replacement_text = "\t\tcompletion_reward = {\n\t\t\tlog = \"[GetDateText]: [Root.GetName]: Focus " + focus_id + "\"\n"
                    outputfile.write(replacement_text)
                    #print("Inserted loc at {0} in file {1}".format(line_number.__str__(), filename))
                else:
                    outputfile.write(line)
            time2 = time.time() - timestart - time1

            #print(filename + " 1: %.3f ms  2: %.3f ms" % (time1*1000, time2*1000))
            ttime += time1 + time2
    return ttime


def event(cpath):
    ttime = 0
    # immediate = {log = "[Root.GetName]: event "+ id + "\n"}  # autolog
    for filename in listdir(cpath + "\\events"):
        if ".txt" in filename:
            file = open(cpath + "\\events\\" + filename, 'r', 'utf-8-sig')
            lines = file.readlines()
            size = os.path.getsize(cpath + "\\events\\" + filename)
            if size < 100:
                continue
            event_id = None
            line_number = 0
            triggered = False
            ids = []
            idss = []

            timestart = time.time()
            for line in lines:
                line_number += 1
                if line.strip().startswith('#') or 'immediate = {log = ' in line:
                    continue
                if '#' in line:
                    line = line.split('#')[0]
                if 'country_event' in line or 'news_event' in line: #New Event
                    if check_triggered(line_number, lines) is False:
                        if "}" not in line or "days" not in line:
                            new_event = True
                            if event_id is not None:
                                triggered = False
                        else:
                            triggered = True
                            new_event = False
                            #print("1: Found Triggered Event at line: " + line_number.__str__())
                    else:
                        triggered = True
                        new_event = False
                if line.strip().startswith('id') and new_event is True and 'immediate = {log =' not in lines[line_number+1]:
                    if 'log = ' not in lines[line_number+1]:
                        if triggered is False:
                            new_event = False
                            event_id = line.split('=')[1].strip()
                            idss.append(event_id)
                            ids.append(line_number)
                        else:
                            triggered = False
            time1 = time.time() - timestart
            line_number = 0
            outputfile = open(cpath + "\\events\\" + filename, 'w', 'utf-8-sig')
            outputfile.truncate()
            for line in lines:
                line_number += 1
                if line_number in ids:
                    event_id = idss[ids.index(line_number)]
                    if '#' in event_id:
                        event_id = event_id.split('#')[0].strip()
                    if '.' not in event_id:
                        outputfile.write(line)
                        continue
                    replacement_text = "\tid = " + event_id + "\n\timmediate = {log = \"[GetDateText]: [Root.GetName]: event " + event_id + "\"}\n"
                    outputfile.write(replacement_text)
                    #print("Inserted loc at {0} in file {1}".format(line_number.__str__(), filename))
                else:
                    outputfile.write(line)
            time2 = time.time() - timestart - time1

            #print(filename + " 1: %.3f ms  2: %.3f ms" % (time1*1000, time2*1000))
            ttime += time1 + time2
    return ttime


def idea(cpath):
    ttime = 0
    timestart = time.time()
    #First bit
    # 			on_add = {log = "[GetDateText]: [Root.GetName]: add idea "}
    for filename in listdir(cpath + "\\common\\ideas"):
        if ".txt" in filename and filename.startswith('_') is False:
            file = open(cpath + "\\common\\ideas\\" + filename, 'r', 'utf-8')
            size = os.path.getsize(cpath + "\\common\\ideas\\" + filename)
            if size < 100:
                continue
            level = 0
            line_number = 0
            ids = []
            lines = file.readlines()
            for line in lines:
                line_number += 1
                if '#' in line:
                    if line.strip().startswith("#") is True:
                        continue
                    else:
                        line = line.split('#')[0]
                re.sub(r'".+?"', '', line)
                if '= {' in line:
                    if level == 2:
                        if 'on_add = {log = ' not in lines[line_number]:
                            #print(line.split('=')[0].strip())
                            ids.append(line_number)
                if '{' in line:
                    level += line.count('{')
                if '}' in line:
                    level -= line.count('}')

            line_number = 0
            outputfile = open(cpath + "\\common\\ideas\\" + filename, 'w', 'utf-8')
            outputfile.truncate()
            for line in lines:
                line_number += 1
                if line_number in ids:
                    idea_id = line.split('=')[0].strip()
                    replacement_text = "\t\t" + idea_id + " = {\n\t\t\ton_add = {log = \"[GetDateText]: [Root.GetName]: add idea " + idea_id + "\"}\n"
                    outputfile.write(replacement_text)
                    #print("Inserted loc at {0} in file {1}".format(line_number.__str__(), filename))
                else:
                    outputfile.write(line)




    time1 = time.time() - timestart
    #Second Bit

    time2 = time.time() - timestart - time1
    ttime += time1 + time2
    return ttime


def decision(cpath):
    ttime = 0
    # log = "[GetDateText] [Root.GetName]: decision (remove) name"
    #common\decisions
    #for filename in listdir(cpath + "\\common\\decisions"):
    for filename in listdir(cpath + "\\common\\decisions"):
        if 'categories' in filename:
            continue
        if ".txt" in filename:
            file = open(cpath + "\\common\\decisions\\" + filename, 'r', 'utf-8')
            size = os.path.getsize(cpath + "\\common\\decisions\\" + filename)
            if size < 100:
                continue
            lines = file.readlines()
            line_number = 0
            level = 0
            ids = [] #array of the names
            idss = [] #line numbers of completion effect
            idsss = [] #line numbers of remove effect
            idssss = [] #line numbers of imteout_effect
            timestart = time.time()
            for line in lines:
                line_number += 1
                if '#' in line:
                    if line.strip().startswith("#") is True:
                        continue
                    else:
                        line = line.split('#')[0]
                if '= {' in line or '={' in line:
                    if level == 1:
                        ids.append(line.split('=')[0].strip())
                if 'complete_effect' in line:
                    if 'log = \"[GetDateText]:' not in lines[line_number]:
                        idss.append(line_number)
                    else:
                        ids.pop()
                if 'remove_effect' in line:
                    if 'log = \"[GetDateText]' not in lines[line_number]:
                        idsss.append(line_number)
                if 'timeout_effect' in line:
                    if 'log = \"[GetDateText]' not in lines[line_number]:
                        idssss.append(line_number)
                if '{' in line:
                    level += line.count('{')
                if '}' in line:
                    level -= line.count('}')

            time1 = time.time() - timestart
            line_number = 0
            backup_index = 0
            outputfile = open(cpath + "\\common\\decisions\\" + filename, 'w', 'utf-8')
            outputfile.truncate()
            dec_id = ""
            dec_bu = ""
            for line in lines:
                line_number += 1
                if line_number in idss:
                    dec_id = ids[idss.index(line_number)]
                    backup_index = ids.index(dec_id)
                    if dec_id in ["{", "}"]:
                        dec_id = "Error, focus name not found"
                    if '}' in line:
                        temp = line.split("{")
                        replacement_text = temp[0] + "{\n\n\t\t\tlog = \"[GetDateText]: [Root.GetName]: Decision " + dec_id + "\"\n" + "{".join(temp)[len(temp[0])+1:] + "\n"
                    else:
                        replacement_text = "\t\tcomplete_effect = { \n\t\t\tlog = \"[GetDateText]: [Root.GetName]: Decision " + dec_id + "\"\n"
                    outputfile.write(replacement_text)
                    #print("Inserted loc at {0} in file {1}".format(line_number.__str__(), filename))
                elif line_number in idsss:
                    if '}' in line:
                        temp = line.split("{")
                        replacement_text = temp[0] + "{\n\n\t\t\tlog = \"[GetDateText]: [Root.GetName]: Decision remove " + dec_id + "\"\n" + "{".join(temp)[len(temp[0])+1:] + "\n"
                    else:
                        replacement_text = "\t\tremove_effect = {\n\t\t\tlog = \"[GetDateText]: [Root.GetName]: Decision remove " + dec_id + "\"\n"
                    outputfile.write(replacement_text)
                    #print("Inserted remove loc at {0} in file {1}".format(line_number.__str__(), filename))
                elif line_number in idssss:
                    if dec_id is "":
                        dec_id = ids[backup_index]
                    elif dec_id == dec_bu:
                        dec_id = ids[backup_index+1]
                    dec_bu = dec_id
                    if '}' in line:
                        temp = line.split("{")
                        replacement_text = temp[0] + "{\n\n\t\t\tlog = \"[GetDateText]: [Root.GetName]: Decision timeout " + dec_id + "\"\n" + "{".join(temp)[len(temp[0])+1:] + "\n"
                    else:
                        replacement_text = "\t\ttimeout_effect = {\n\t\t\tlog = \"[GetDateText]: [Root.GetName]: Decision timeout " + dec_id + "\"\n"
                    outputfile.write(replacement_text)
                    #print("Inserted remove loc at {0} in file {1}".format(line_number.__str__(), filename))
                else:
                    outputfile.write(line)
            time2 = time.time() - timestart - time1

            #print(filename + " 1: %.3f ms  2: %.3f ms" % (time1*1000, time2*1000))
            ttime += time1 + time2
    return ttime



def main():
    cpath = sys.argv[1]
    ok = 0
    for string in sys.argv:
        if ok < 2:
            ok += 1
        else:
            cpath += ' ' + string


    ttime = 0
    ttime += event(cpath)
    ttime += focus(cpath)
    ttime += idea(cpath)
    ttime += decision(cpath)
    print("Total Time: %.3f ms" % (ttime * 1000))

if __name__ == "__main__":
    main()