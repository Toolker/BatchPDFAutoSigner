from datetime import datetime


def log_text(text):
    file_error = open("log.txt","a+")

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    text=str(text)
    file_error.writelines(dt_string+" - "+text + '\r\n')
    file_error.close()

