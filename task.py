import datetime
import argparse
import configparser
import pickle
import pandas as pd
import numpy as np

config = configparser.ConfigParser()
config.read('config.ini')

parser = argparse.ArgumentParser(description='Task Manager')
parser.add_argument('-t', '--task', type=str, help='Task title')
parser.add_argument('-l', '--list', type=str, help='List all tasks based on #tag or keyword')
parser.add_argument('-d', '--due', type=str, help='Due day')
args = parser.parse_args()

path = config["DEFAULT"]["path"] + ".tasks"
rollover = config["DEFAULT"]["rollover"]

days_of_week = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

class Task:

    def __init__(self, task, task_list, due=None):
        self.task_list = task_list
        self.created = datetime.datetime.now()
        self.due = self.set_due(due)
        self.task = task
        self.save_task()

    def set_due(self, due):
        if due == None:
            self.due = self.created
            return self.created
        else:
            try:
                self.due = datetime_from_day(due)
                return self.due
            except:
                return self.created

    def save_task(self):
        self.task_list.append(self)
        with open(path, 'wb') as output:
            pickle.dump(self.task_list, output, pickle.HIGHEST_PROTOCOL)

def read_tasks(path):
    try:
        with open(path, 'rb') as input:
            tasks = pickle.load(input)
    except:
        tasks = []

    return tasks

def print_tasks(df):
    print(df)

def tasks_to_dataframe(task_list, by_day=True):
    task = []
    created = []
    due = []


    for item in task_list:
        task.append(item.task)
        created.append(item.created)
        due.append(item.due)

    t = pd.Series(task, name="task")
    c = pd.Series(created, name="created")
    d = pd.Series(due, name="due")

    df = pd.concat([t, c, d], axis=1)
    df = df.sort_values(by=["due"]).reset_index()# sort by due date
    if by_day:
        df.update(series_to_day(df["due"]))

    return df[["task", "due"]]

def datetime_from_day(key="dummy"):
    today = datetime.datetime.today()
    tomorrow = today + datetime.timedelta(days=1)
    if key in "tomorrow":
        return tomorrow

    for i, day in enumerate(days_of_week):
        if day in key.lower():
            delta = i - today.weekday()

            if delta <= 0:
                delta = 7 - abs(delta)

            date = today + datetime.timedelta(days=delta)
            return date
    return today

def day_from_datetime(key):

    today = datetime.datetime.now()
    delta = (key.date()-today.date()).days

    if delta == 0:
        return "Today"

    if delta < 7:
        day = today.weekday() - 7 + delta

    try:
        return days_of_week[day].capitalize()
    except:
        return key.strftime('%d %b')

def series_to_day(series):

    new_series = []

    for item in series:
        new_series.append(day_from_datetime(item))

    return pd.Series(new_series, name=series.name)

def move_tasks_due(task_list, var, due=None, key="past"):

    today = datetime.datetime.today()
    new_task_list = []

    if isinstance(due, datetime.datetime):
        key = datetime_from_day(key.lower())
        print(due)
        for task in task_list:
            if task.due.date() == key.date():
                task.due = due
            new_task_list.append(task)

        with open(path, 'wb') as output:
            pickle.dump(new_task_list, output, pickle.HIGHEST_PROTOCOL)
    else:

        if key.lower() != "past":
            key = datetime_from_day(key.lower())
            for task in task_list:
                if task.due.date() == key.date():
                    task.due = datetime_from_day(due)
                new_task_list.append(task)

        else:
            for task in task_list:
                if task.due.date() < today.date():
                    task.due = today
                new_task_list.append(task)

        with open(path, 'wb') as output:
            pickle.dump(new_task_list, output, pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":

    task_list = read_tasks(path)
    tasks_df = tasks_to_dataframe(task_list)

    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)

    if rollover:
        move_tasks_due(task_list, "due")


    if args.task:

        if args.due:
            task = Task(args.task, task_list, args.due)
        else:
            task = Task(args.task, task_list)

    if args.list:
        print_tasks(tasks_df)





