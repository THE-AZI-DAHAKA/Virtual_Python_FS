import datetime
import os
import copy #
class FileSystem:

    def __init__(self):
        self.current_dir = {'..': None}
        self.root = self.current_dir
        self.size = {'/': 0}
        self.creation_time = {'/': datetime.datetime.now()}

    def _change_directory(self, path):
        if path == '..':
            self.current_dir = self.current_dir['..']
        else:
            self.current_dir = self.current_dir[path]

    def _ensure_file_exists(self, filename):
        if filename not in self.current_dir:
            print('File does not exist.')
            return False
        if isinstance(self.current_dir[filename], dict):
            print('File is a directory.')
            return False
        return True

    def _ensure_dir_exists(self, dirname):
        if dirname not in self.current_dir:
            print('Directory does not exist.')
            return False
        if not isinstance(self.current_dir[dirname], dict):
            print('Directory is a file.')
            return False
        return True

    def touch(self, filename):
        if filename in self.current_dir:
            print('File already exists.')
        else:
            self.current_dir[filename] = ''
            self.creation_time[self.pwd() + '/' + filename] = datetime.datetime.now()
            self.size[self.pwd() + '/' + filename] = 0

    def mkdir(self, dirname):
        if dirname in self.current_dir:
            print('Directory already exists.')
        else:
            self.current_dir[dirname] = {'..': self.current_dir}
            self.creation_time[self.pwd() + '/' + dirname] = datetime.datetime.now()

    def cd(self, dirname):
        if self._ensure_dir_exists(dirname):
            self._change_directory(dirname)

    def ls(self):
        for name, content in self.current_dir.items():
            if name == '..':
                continue
            if isinstance(content, dict):
                print(f"{name}/")
            else:
                file_path = self.pwd() + '/' + name if self.pwd() != '/' else '/' + name
                file_size = self.size.get(file_path, 0)
                file_creation_time = self.creation_time.get(file_path, datetime.datetime.now())
                print(f"{name}\t{file_size}B\t{file_creation_time}")


    def pwd(self):
        if self.current_dir == self.root:
            return '/'
        else:
            path = ''
            dir = self.current_dir
            while dir != self.root:
                for name, content in dir['..'].items():
                    if content == dir:
                        path = '/' + name + path
                        dir = dir['..']
                        break
            return path

    def rm(self, filename):
        if self._ensure_file_exists(filename):
            del self.current_dir[filename]
            del self.creation_time[self.pwd() + '/' + filename]
            del self.size[self.pwd() + '/' + filename]

    def rmdir(self, dirname):
        if self._ensure_dir_exists(dirname) and dirname != '..':
            del self.current_dir[dirname]
            del self.creation_time[self.pwd() + '/' + dirname]

    def write(self, filename, content):
        if self._ensure_file_exists(filename):
            self.current_dir[filename] = content
            self.size[self.pwd() + '/' + filename] = len(content)

    def read(self, filename):
        if self._ensure_file_exists(filename):
            print(self.current_dir[filename])

    def cp(self, src, dest):
        if self._ensure_file_exists(src) and dest not in self.current_dir:
            self.current_dir[dest] = copy.deepcopy(self.current_dir[src]) #
            self.creation_time[self.pwd() + '/' + dest] = datetime.datetime.now()
            self.size[self.pwd() + '/' + dest] = len(self.current_dir[src])
    
    def get_dir_from_path(self, path):
        dirs = path.split('/')
        current = self.root

        for d in dirs:
            if d == '':
                continue
            if d not in current:
                return None
            current = current[d]
        return current

    def mv(self, src, dest):
        # Separate paths into directories and filenames
        src_dirs, src_file = os.path.split(src)
        dest_dirs, dest_file = os.path.split(dest)

        # If dest_file is empty, it means the destination is a directory, and the file should keep its name
        if not dest_file:
            dest_file = src_file

        # Get source and destination directories
        src_dir = self.get_dir_from_path(src_dirs or self.pwd())
        dest_dir = self.get_dir_from_path(dest_dirs or self.pwd())

        if not src_dir or src_file not in src_dir:
            print(f"Source '{src}' does not exist.")
            return

        # Check if the destination is a directory, and adjust the destination path accordingly
        if dest_file in dest_dir and isinstance(dest_dir[dest_file], dict):
            dest_file = src_file

        if dest_file in dest_dir:
            print(f"Destination '{dest}' already exists.")
            return

        # Move the item
        dest_dir[dest_file] = src_dir[src_file]
        del src_dir[src_file]

        # Update the metadata
        old_path_key = (os.path.join(self.pwd(), src)).replace('//', '/')
        new_path_key = (os.path.join(self.pwd(), dest_dirs, dest_file)).replace('//', '/')

        # Update creation_time if the item is a directory (or a file without existing metadata)
        if new_path_key not in self.creation_time:
            self.creation_time[new_path_key] = datetime.datetime.now()

        # If old_path_key exists, copy its creation_time to the new_path_key
        if old_path_key in self.creation_time:
            self.creation_time[new_path_key] = self.creation_time.pop(old_path_key)

        # Update size if the item is a file
        if old_path_key in self.size:
            self.size[new_path_key] = self.size.pop(old_path_key)



fs = FileSystem()

while True:
    command = input("> ").split(" ", maxsplit=1)
    if len(command) == 1:
        command.append('')
    command_name, command_arg = command
    if command_name == 'exit':
        break
    elif command_name == 'touch':
        fs.touch(command_arg)
    elif command_name == 'mkdir':
        fs.mkdir(command_arg)
    elif command_name == 'cd':
        fs.cd(command_arg)
    elif command_name == 'ls':
        fs.ls()
    elif command_name == 'pwd':
        print(fs.pwd())
    elif command_name == 'rm':
        fs.rm(command_arg)
    elif command_name == 'rmdir':
        fs.rmdir(command_arg)
    elif command_name == 'write':
        name, content = command_arg.split(" ", maxsplit=1)
        fs.write(name, content)
    elif command_name == 'read':
        fs.read(command_arg)
    elif command_name == 'cp':
        src, dest = command_arg.split(" ", maxsplit=1)
        fs.cp(src, dest)
    elif command_name == 'mv':
        src, dest = command_arg.split(" ", maxsplit=1)
        fs.mv(src, dest)
    else:
        print('Unknown command.')