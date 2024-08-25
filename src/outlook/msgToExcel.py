import csv
import glob

import extract_msg

f = glob.glob(r'.\toImport\*.msg')
msg = []

for filename in f:
    msg.append(extract_msg.Message(filename))
    # msg_sender = msg.sender
    # msg_date = msg.date
    # msg_subj = msg.subject
    # msg_message = msg.body
with open("export.csv", "w+") as w_file:
    file_writer = csv.writer(w_file, delimiter="\t")
    file_writer.writerow(["Дата", "Отправитель", "Тема", "Текст"])
    for message in msg:
        messagee = " ".join(message.body.splitlines())
        file_writer.writerow(
            [message.date, message.sender, message.subject, messagee])
        if message.attachments:
            for attachment in message.attachments:
                attachment.save(customPath=f'./attachments/')
