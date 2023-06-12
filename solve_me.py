from http.server import BaseHTTPRequestHandler, HTTPServer


class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            self.completed_items = file.readlines()
            file.close()
        except Exception:
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def sort_current_items(self):
        temp_keys = list(self.current_items.keys())
        temp_keys.sort()
        self.current_items = {i: self.current_items[i] for i in temp_keys}

    def rearrage_priority(self, priority):
        temp_task = self.current_items[priority]
        del self.current_items[priority]
        if priority + 1 in self.current_items:
            self.rearrage_priority(priority + 1)
        self.current_items[priority + 1] = temp_task

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def add(self, args):
        if len(args) < 2:
            print('Sorry, Enter task in format: python tasks.py add 2 "task"')
            return
        if int(args[0]) in self.current_items:
            self.rearrage_priority(int(args[0]))

        self.current_items[int(args[0])] = args[1]
        self.write_current()
        print(f'Added task: "{args[1]}" with priority {args[0]}')

    def done(self, args):
        if len(args) < 1:
            print("Sorry, Enter task in format: python tasks.py done 2")
            return
        if int(args[0]) not in self.current_items:
            print(f"Error: no incomplete item with priority {args[0]} exists.")
            return
        self.completed_items.append(self.current_items[int(args[0])])
        del self.current_items[int(args[0])]
        self.write_current()
        self.write_completed()
        print(f"Marked item as done.")

    def delete(self, args):
        if len(args) < 1:
            print("Sorry, Enter task in format: python tasks.py delete 2")
            return
        if int(args[0]) not in self.current_items:
            print(
                f"Error: item with priority {args[0]} does not exist. Nothing deleted."
            )
            return
        del self.current_items[int(args[0])]
        self.write_current()
        print(f"Deleted item with priority {args[0]}")

    def ls(self):
        if len(self.current_items) == 0:
            print("No tasks")
            return

        self.sort_current_items()
        for index, key in enumerate(self.current_items):
            print(f"{index+1}. {self.current_items[key]} [{key}]")

    def report(self):
        self.sort_current_items()
        print(f"Pending : {len(self.current_items)}")
        for index, key in enumerate(self.current_items):
            print(f"{index+1}. {self.current_items[key]} [{key}]")

        print(f"\nCompleted : {len(self.completed_items)}")
        for index, item in enumerate(self.completed_items):
            print(f"{index+1}. {item}")

    def render_pending_tasks(self):
        # Complete this method to return all incomplete tasks as HTML
        taks = ""
        for key in self.current_items:
            taks += f"<li> {self.current_items[key]} - {key}</li>"
        return f"""
        <ul>
        {taks}
        </ul>
        """

    def render_completed_tasks(self):
        # Complete this method to return all completed tasks as HTML
        taks = ""
        for task in self.completed_items:
            taks += f"<li> {task}</li>"
        return f"""
        <ul>
        {taks}
        </ul>
        """


class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()

        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        if self.path.split("/")[0] == "delete":
            print(self)
            content = self
        elif self.path == "/":
            list_items = ""
            for key in task_command_object.current_items:
                list_items += list_component(
                    task_command_object.current_items[key], key
                )
            completed_items = ""
            for key in task_command_object.completed_items:
                completed_items += """
                <li>task_command_object.completed_items[key]</li>
                """
            content = home_page.replace("***LIST***", list_items).replace(
                "***COMPLETED_LIST***", completed_items
            )

        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())


def list_component(task, priority):
    return f"""
    <li >
    <div style='margin-top:8px;display:flex;flex-direction:row;gap:10px'>
         {task}
         <form action='/delete/{priority}' method='GET'>
          <button 
           style='background-color:green;color:white;border:none;border-radius: 0.2rem;padding-left:10px;padding-right:10px;padding-top:3px;padding-bottom:3px;cursor: pointer;' >
           Completed
           </button>
           <button 
           style='background-color:red;color:white;border:none;border-radius: 0.2rem;padding-left:10px;padding-right:10px;padding-top:3px;padding-bottom:3px;cursor: pointer;' >
           Delete
           </button>
        </div>
          </li>"""


home_page = """
<html>

<head>
    <title>Home</title>
</head>

<div style='min-height:100%;width:100%; display: flex;'>
<div style='box-shadow: 0px 0px 20px 3px lightGray;background-color:white;max-width:24rem;margin: auto;padding:20px;border-radius: 0.375rem;'>


 <h2>To do task list</h2>

    <ul>
        ***LIST***
    </ul>
    
    <h2>Completed task list</h2>

    <ul>
        ***COMPLETED_LIST***
    </ul>
    </div>
</div>

</html>"""
