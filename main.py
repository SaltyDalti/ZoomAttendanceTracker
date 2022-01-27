import PySimpleGUI as Gui
import os


sys_name = str(os.name)
select_instructions = 'Use shift+click to select multiple'
if sys_name == 'posix':
    select_instructions = 'Use shift+click or command+click to select multiple.'
if sys_name == 'nt':
    select_instructions = 'Use shift+click or ctrl+click to select multiple.'

Gui.theme('Dark Blue 3')
size = (500, 200)
window_title = 'Zoom Attendance Grader'
layout = [  [Gui.Text('What do you want to save the file as?')],
            [Gui.InputText(key='SAVE')],
            [Gui.Text('Click "Browse" and select the .csv file(s) to convert')],
            [Gui.Input(key='_FILES_'), Gui.FilesBrowse()],
            [Gui.Text(select_instructions)],
            [Gui.OK(), Gui.Cancel()]
            ]
window = Gui.Window(window_title, layout, size=size)

cancelled = False
real_path = True
get_save_name = ''
p = ''


class Report:
    def __init__(self):
        self.cells = []  # where lines are first stored
        self.meeting_id = ''
        self.topic = ''
        self.validate = []  # used for duplicate file validation
        self.isvalid = True

    def open_file(self, file_name):
        with open(file_name, 'r') as read_file:
            lines = read_file.readlines()
            for line in lines:
                create_cells = line.split(',')
                self.cells.extend([create_cells])

    def setup(self):
        del self.cells[3]  # delete unnecessary filler rows from Zoom formatting
        del self.cells[2]
        del self.cells[0]

        self.meeting_id = self.cells[0][0]
        print(self.meeting_id)
        self.topic = self.cells[0][1]
        print(self.topic)

        stamp_tokens = self.cells[0][2].split(' ')  # validates duplicate files based on meetingID, date, and time
        date = stamp_tokens[0]
        time = stamp_tokens[1]
        self.validate = [self.meeting_id, date, time]
        if self.validate not in valid_date_list:
            valid_date_list.extend([self.validate])

            if self.meeting_id not in main_dict:
                main_dict.update({self.meeting_id: {}})  # adds the meeting ID to the dictionary with key {}
            if self.meeting_id in ID_topic_dict:
                ID_topic_dict[self.meeting_id][1] += 1  # if entry exists, add to total count
            if self.meeting_id not in ID_topic_dict:
                ID_topic_dict.update({self.meeting_id: [self.topic, 1]})
        else:
            self.isvalid = True

    def get_names(self):
        if self.isvalid:
            for index in range(0, len(self.cells)):
                name = self.cells[index][0]
                if index == 0:  # skips the header row from zoom with meetingID
                    pass
                else:
                    student_duration = int(self.cells[index][2])
                    teacher_duration = int(self.cells[1][2])
                    if student_duration >= teacher_duration - 20:
                        if name in main_dict[self.meeting_id]:
                            main_dict[self.meeting_id][name] += 1  # updates attendance count
                        else:
                            main_dict[self.meeting_id].update({name: 1})  # create entry for name with key for attendance
                    else:
                        pass
        else:
            pass


def print_format():
    with open(save_name, 'w+') as output:
        for meetingID, info in ID_topic_dict.items():
            output.write(f'{info[0]}, {meetingID}, Total classes: {info[1]}\n')
            output.write(f'{subheader[0]}, {subheader[1]}, {subheader[2]}, {subheader[3]}\n')
            for dictID, names in main_dict.items():
                if meetingID == dictID:
                    for name, atten in names.items():
                        grade = int((atten/info[1]) * 100)
                        output.write(f' ,{name}, {atten}, {grade}\n')
            output.write('\n')


while True:
    event, values = window.read()
    if event in (Gui.WIN_CLOSED, 'Cancel'):
        cancelled = True
        break
    if values['_FILES_'] == '':
        real_path = False
        break
    if event in 'OK':

        files = values['_FILES_'].split(';')  # splits file paths if multiple selected
        p = os.path.split(files[0])
        get_save_name = values['SAVE'] + '.csv'
        save_name = os.path.join(p[0], get_save_name)

        valid_date_list = []  # used to validate duplicate files
        main_dict = {}  # where most of the info is stored (nested)
        ID_topic_dict = {}  # meetingID: [meeting topic, number of occurrences]
        subheader = ['', 'Name', 'Attended', 'Grade']  # a predefined subheader for formatting

        for file in files:
            i = 0
            report = Report()
            report.open_file(file)
            report.setup()
            report.get_names()
            layout += [[Gui.one_line_progress_meter(window_title, i + 1, (len(files)), 'key', 'Grading', orientation='h')]]
        print_format()
        break
window.close()

if cancelled:
    layout = [  [Gui.Text('Grading cancelled!')],
                [Gui.OK()]
                ]
    window = Gui.Window(window_title, layout, size=size)
if not real_path:
    layout = [[Gui.Text('No input file selected!')],
              [Gui.OK()]
              ]
    window = Gui.Window(window_title, layout, size=size)
if not cancelled and real_path:
    layout = [[Gui.Text('Grading complete!')],
              [Gui.Text(f'Your file was saved as {get_save_name} in {p[0]}')],
              [Gui.OK()]
              ]
    window = Gui.Window(window_title, layout, size=size)


while True:
    event, values = window.read()
    if event in 'OK':
        break
