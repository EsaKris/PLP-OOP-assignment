import os
import sys
import shutil
from datetime import datetime
import pickle

class FileManager:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.file_history = []
        self.operations_log = []
        self.undo_stack = []
        self.backup_dir = os.path.join(os.getcwd(), "file_manager_backups")
        self._ensure_backup_dir()

    def _ensure_backup_dir(self):
        """Create backup directory if it doesn't exist"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def log_operation(self, operation, details):
        """Log operations with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {operation}: {details}"
        self.operations_log.append(log_entry)

    def display_menu(self):
        """Display the main menu"""
        print("\n=== Enhanced File Manager ===")
        print(" 1. Read and display a file")
        print(" 2. Create a new file")
        print(" 3. Modify file content (add line numbers)")
        print(" 4. Append to existing file")
        print(" 5. Delete a file")
        print(" 6. Copy a file")
        print(" 7. Move/Rename a file")
        print(" 8. Search for files")
        print(" 9. View file statistics")
        print("10. View file history")
        print("11. View operation logs")
        print("12. Change working directory")
        print("13. List directory contents")
        print("14. Undo last operation")
        print(" 0. Exit")
        print("===========================")

    def run(self):
        """Main application loop"""
        while True:
            self.display_menu()
            try:
                choice = input("Enter your choice (0-14): ")
                
                if not choice.isdigit():
                    print("Please enter a number.")
                    continue
                
                choice = int(choice)
                
                if choice == 0:
                    print("Exiting application. Goodbye!")
                    break
                elif choice == 1:
                    self.read_file()
                elif choice == 2:
                    self.create_file()
                elif choice == 3:
                    self.modify_file()
                elif choice == 4:
                    self.append_file()
                elif choice == 5:
                    self.delete_file()
                elif choice == 6:
                    self.copy_file()
                elif choice == 7:
                    self.move_file()
                elif choice == 8:
                    self.search_files()
                elif choice == 9:
                    self.file_statistics()
                elif choice == 10:
                    self.view_history()
                elif choice == 11:
                    self.view_logs()
                elif choice == 12:
                    self.change_directory()
                elif choice == 13:
                    self.list_directory()
                elif choice == 14:
                    self.undo_last_operation()
                else:
                    print("Invalid choice. Please enter a number between 0-14.")
            
            except Exception as e:
                print(f"An error occurred: {e}")

    def get_valid_filename(self, prompt, check_exists=False, allow_empty=False):
        """Get a valid filename from user"""
        while True:
            filename = input(prompt).strip()
            
            if not filename and not allow_empty:
                print("Filename cannot be empty.")
                continue
            
            if check_exists and filename and not os.path.exists(filename):
                print(f"Error: File '{filename}' does not exist.")
                return None
            
            return filename

    def _create_backup(self, filename):
        """Create backup of a file for undo operations"""
        backup_path = os.path.join(self.backup_dir, os.path.basename(filename) + ".bak")
        
        if os.path.exists(filename):
            if os.path.isdir(filename):
                shutil.copytree(filename, backup_path)
            else:
                shutil.copy2(filename, backup_path)
            return backup_path
        return None

    def _push_undo_action(self, action_type, original, backup=None, new_location=None):
        """Add an action to the undo stack"""
        self.undo_stack.append({
            'type': action_type,
            'original': original,
            'backup': backup,
            'new_location': new_location
        })

    def undo_last_operation(self):
        """Undo the last file operation"""
        if not self.undo_stack:
            print("Nothing to undo!")
            return
        
        action = self.undo_stack.pop()
        
        try:
            if action['type'] == 'create':
                if os.path.exists(action['original']):
                    os.remove(action['original'])
                    print(f"Undo: Removed created file '{action['original']}'")
            
            elif action['type'] == 'delete':
                if action['backup'] and os.path.exists(action['backup']):
                    shutil.move(action['backup'], action['original'])
                    print(f"Undo: Restored deleted file '{action['original']}'")
            
            elif action['type'] == 'modify':
                if os.path.exists(action['original']) and action['backup']:
                    os.remove(action['original'])
                    shutil.move(action['backup'], action['original'])
                    print(f"Undo: Reverted changes to '{action['original']}'")
            
            elif action['type'] == 'append':
                # For append, we'd need to track the exact changes to undo them
                print("Undo for append operations is not fully implemented yet")
            
            elif action['type'] == 'copy':
                if os.path.exists(action['new_location']):
                    os.remove(action['new_location'])
                    print(f"Undo: Removed copied file '{action['new_location']}'")
            
            elif action['type'] == 'move':
                if os.path.exists(action['new_location']):
                    shutil.move(action['new_location'], action['original'])
                    print(f"Undo: Moved file back to '{action['original']}'")
            
            self.log_operation("Undo", f"{action['type']} on {action['original']}")
        
        except Exception as e:
            print(f"Error during undo: {e}")

    def read_file(self, binary_mode=False):
        """Read and display file content"""
        filename = self.get_valid_filename("Enter filename to read: ", check_exists=True)
        if not filename:
            return
        
        try:
            mode = 'rb' if binary_mode else 'r'
            encoding = None if binary_mode else 'utf-8'
            
            with open(filename, mode, encoding=encoding) as file:
                if binary_mode:
                    content = file.read()
                    print(f"\nBinary content of {filename} (first 100 bytes):")
                    print(content[:100])
                else:
                    content = file.read()
                    print(f"\n=== Content of {filename} ===")
                    print(content)
                    print("=" * (22 + len(filename)))
            
            self.file_history.append(filename)
            self.log_operation("Read", filename)
        
        except PermissionError:
            print(f"Error: No permission to read '{filename}'")
        except UnicodeDecodeError:
            print(f"Error: Cannot decode '{filename}' as text file")
            retry = input("Try reading as binary file? (y/n): ").lower()
            if retry == 'y':
                self.read_file(binary_mode=True)
        except Exception as e:
            print(f"Error reading file: {e}")

    def create_file(self):
        """Create a new file with content"""
        filename = self.get_valid_filename("Enter new filename: ")
        if not filename:
            return
        
        if os.path.exists(filename):
            print(f"Warning: '{filename}' already exists.")
            overwrite = input("Overwrite? (y/n): ").lower()
            if overwrite != 'y':
                print("File creation cancelled.")
                return
        
        binary = input("Create as binary file? (y/n): ").lower() == 'y'
        
        try:
            if binary:
                content = input("Enter hex data (e.g., '48656C6C6F' for 'Hello'): ").strip()
                try:
                    bytes_data = bytes.fromhex(content)
                except ValueError:
                    print("Invalid hex data")
                    return
                
                with open(filename, 'wb') as file:
                    file.write(bytes_data)
            else:
                content = input("Enter file content (press Enter when done):\n")
                with open(filename, 'w') as file:
                    file.write(content)
            
            print(f"File '{filename}' created successfully.")
            self.file_history.append(filename)
            self.log_operation("Create", filename)
            self._push_undo_action('create', filename)
        
        except PermissionError:
            print(f"Error: No permission to create '{filename}'")
        except Exception as e:
            print(f"Error creating file: {e}")

    def modify_file(self):
        """Modify file content by adding line numbers"""
        input_file = self.get_valid_filename("Enter input filename: ", check_exists=True)
        if not input_file:
            return
        
        output_file = self.get_valid_filename("Enter output filename: ")
        if not output_file:
            return
        
        backup = self._create_backup(input_file)
        
        try:
            binary = input("Process as binary file? (y/n): ").lower() == 'y'
            
            if binary:
                with open(input_file, 'rb') as infile:
                    data = infile.read()
                
                # Simple binary modification - add a header
                modified_data = b"BINARY_FILE:" + data
                
                with open(output_file, 'wb') as outfile:
                    outfile.write(modified_data)
            else:
                with open(input_file, 'r') as infile:
                    lines = infile.readlines()
                
                modified_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
                
                with open(output_file, 'w') as outfile:
                    outfile.writelines(modified_lines)
            
            print(f"Modified content written to '{output_file}'")
            self.file_history.extend([input_file, output_file])
            self.log_operation("Modify", f"{input_file} -> {output_file}")
            self._push_undo_action('modify', input_file, backup)
        
        except PermissionError:
            print("Error: Permission denied for file operation")
        except Exception as e:
            print(f"Error modifying file: {e}")

    def append_file(self):
        """Append content to an existing file"""
        filename = self.get_valid_filename("Enter filename to append to: ", check_exists=True)
        if not filename:
            return
        
        backup = self._create_backup(filename)
        
        try:
            binary = input("Append as binary data? (y/n): ").lower() == 'y'
            
            if binary:
                data = input("Enter hex data to append: ").strip()
                try:
                    bytes_data = bytes.fromhex(data)
                except ValueError:
                    print("Invalid hex data")
                    return
                
                with open(filename, 'ab') as file:
                    file.write(bytes_data)
            else:
                content = input("Enter content to append:\n")
                with open(filename, 'a') as file:
                    file.write(content + '\n')
            
            print(f"Content appended to '{filename}'")
            self.file_history.append(filename)
            self.log_operation("Append", filename)
            self._push_undo_action('append', filename, backup)
        
        except PermissionError:
            print(f"Error: No permission to write to '{filename}'")
        except Exception as e:
            print(f"Error appending to file: {e}")

    def delete_file(self):
        """Delete a file with confirmation"""
        filename = self.get_valid_filename("Enter filename to delete: ", check_exists=True)
        if not filename:
            return
        
        confirm = input(f"Are you sure you want to delete '{filename}'? (y/n): ").lower()
        if confirm != 'y':
            print("Deletion cancelled.")
            return
        
        backup = self._create_backup(filename)
        
        try:
            if os.path.isdir(filename):
                shutil.rmtree(filename)
            else:
                os.remove(filename)
            
            print(f"File '{filename}' deleted successfully.")
            self.log_operation("Delete", filename)
            self._push_undo_action('delete', filename, backup)
        
        except PermissionError:
            print(f"Error: No permission to delete '{filename}'")
        except Exception as e:
            print(f"Error deleting file: {e}")

    def copy_file(self):
        """Copy a file to a new location"""
        source = self.get_valid_filename("Enter source filename: ", check_exists=True)
        if not source:
            return
        
        destination = self.get_valid_filename("Enter destination filename: ")
        if not destination:
            return
        
        try:
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
            
            print(f"File copied from '{source}' to '{destination}'")
            self.file_history.extend([source, destination])
            self.log_operation("Copy", f"{source} -> {destination}")
            self._push_undo_action('copy', source, new_location=destination)
        
        except PermissionError:
            print("Error: Permission denied for file operation")
        except Exception as e:
            print(f"Error copying file: {e}")

    def move_file(self):
        """Move or rename a file"""
        source = self.get_valid_filename("Enter source filename: ", check_exists=True)
        if not source:
            return
        
        destination = self.get_valid_filename("Enter destination filename: ")
        if not destination:
            return
        
        try:
            shutil.move(source, destination)
            print(f"File moved from '{source}' to '{destination}'")
            self.file_history.extend([source, destination])
            self.log_operation("Move", f"{source} -> {destination}")
            self._push_undo_action('move', source, new_location=destination)
        
        except PermissionError:
            print("Error: Permission denied for file operation")
        except Exception as e:
            print(f"Error moving file: {e}")

    def search_files(self):
        """Search for files by name or content"""
        print("\n=== File Search Options ===")
        print("1. Search by filename pattern")
        print("2. Search by content in files")
        print("3. Search binary files for pattern")
        print("==========================")
        
        choice = input("Enter search option (1-3): ")
        
        if choice == '1':
            pattern = input("Enter filename pattern (e.g., '*.txt'): ").strip()
            if not pattern:
                print("Pattern cannot be empty")
                return
            
            start_dir = input(f"Enter directory to search (default: {self.current_dir}): ").strip()
            start_dir = start_dir if start_dir else self.current_dir
            
            try:
                print(f"\nSearching for '{pattern}' in {start_dir}...")
                found = False
                
                for root, dirs, files in os.walk(start_dir):
                    for file in files:
                        if file.lower().find(pattern.lower()) != -1:
                            full_path = os.path.join(root, file)
                            print(f"Found: {full_path}")
                            found = True
                
                if not found:
                    print("No matching files found.")
            
            except Exception as e:
                print(f"Error during search: {e}")
        
        elif choice == '2':
            search_text = input("Enter text to search for: ").strip()
            if not search_text:
                print("Search text cannot be empty")
                return
            
            file_pattern = input("Enter file pattern to search in (e.g., '*.txt', leave blank for all files): ").strip()
            start_dir = input(f"Enter directory to search (default: {self.current_dir}): ").strip()
            start_dir = start_dir if start_dir else self.current_dir
            
            try:
                print(f"\nSearching for '{search_text}' in {file_pattern if file_pattern else 'all files'}...")
                found = False
                
                for root, dirs, files in os.walk(start_dir):
                    for file in files:
                        if file_pattern and not file.lower().endswith(file_pattern.lower().lstrip('*')):
                            continue
                        
                        full_path = os.path.join(root, file)
                        
                        try:
                            with open(full_path, 'r', errors='ignore') as f:
                                for line_num, line in enumerate(f, 1):
                                    if search_text.lower() in line.lower():
                                        print(f"Found in {full_path} (line {line_num}): {line.strip()}")
                                        found = True
                        except:
                            continue
                
                if not found:
                    print("No matches found.")
            
            except Exception as e:
                print(f"Error during search: {e}")
        
        elif choice == '3':
            hex_pattern = input("Enter hex pattern to search for (e.g., '48656C6C6F' for 'Hello'): ").strip()
            if not hex_pattern:
                print("Pattern cannot be empty")
                return
            
            try:
                search_bytes = bytes.fromhex(hex_pattern)
            except ValueError:
                print("Invalid hex pattern")
                return
            
            file_pattern = input("Enter file pattern to search in (e.g., '*.bin', leave blank for all files): ").strip()
            start_dir = input(f"Enter directory to search (default: {self.current_dir}): ").strip()
            start_dir = start_dir if start_dir else self.current_dir
            
            try:
                print(f"\nSearching for binary pattern {hex_pattern}...")
                found = False
                
                for root, dirs, files in os.walk(start_dir):
                    for file in files:
                        if file_pattern and not file.lower().endswith(file_pattern.lower().lstrip('*')):
                            continue
                        
                        full_path = os.path.join(root, file)
                        
                        try:
                            with open(full_path, 'rb') as f:
                                content = f.read()
                                if search_bytes in content:
                                    pos = content.find(search_bytes)
                                    print(f"Found at position {pos} in {full_path}")
                                    found = True
                        except:
                            continue
                
                if not found:
                    print("No matches found.")
            
            except Exception as e:
                print(f"Error during search: {e}")
        
        else:
            print("Invalid search option")

    def file_statistics(self):
        """Display statistics about a file"""
        filename = self.get_valid_filename("Enter filename: ", check_exists=True)
        if not filename:
            return
        
        try:
            stats = os.stat(filename)
            print(f"\n=== Statistics for {filename} ===")
            print(f"Size: {stats.st_size} bytes")
            print(f"Last modified: {datetime.fromtimestamp(stats.st_mtime)}")
            print(f"Last accessed: {datetime.fromtimestamp(stats.st_atime)}")
            print(f"Created: {datetime.fromtimestamp(stats.st_ctime)}")
            print("Permissions:")
            print(f"  Readable: {'Yes' if os.access(filename, os.R_OK) else 'No'}")
            print(f"  Writable: {'Yes' if os.access(filename, os.W_OK) else 'No'}")
            print(f"  Executable: {'Yes' if os.access(filename, os.X_OK) else 'No'}")
            print("==============================")
            
            self.log_operation("View Stats", filename)
        
        except Exception as e:
            print(f"Error getting file statistics: {e}")

    def view_history(self):
        """Display recently accessed files"""
        print("\n=== Recently Accessed Files ===")
        unique_files = []
        [unique_files.append(f) for f in self.file_history if f not in unique_files]
        
        for i, filename in enumerate(unique_files[-10:], 1):
            print(f"{i}. {filename}")
        print("=============================")

    def view_logs(self):
        """Display operation logs"""
        print("\n=== Operation Log ===")
        for log in self.operations_log[-20:]:
            print(log)
        print("====================")

    def change_directory(self):
        """Change the current working directory"""
        new_dir = input(f"Enter new directory (current: {self.current_dir}): ").strip()
        if not new_dir:
            print("No directory specified. Using current directory.")
            return
        
        try:
            os.chdir(new_dir)
            self.current_dir = os.getcwd()
            print(f"Working directory changed to: {self.current_dir}")
            self.log_operation("Change Directory", new_dir)
        
        except FileNotFoundError:
            print(f"Error: Directory '{new_dir}' does not exist")
        except PermissionError:
            print(f"Error: No permission to access '{new_dir}'")
        except Exception as e:
            print(f"Error changing directory: {e}")

    def list_directory(self):
        """List contents of current directory with details"""
        print(f"\n=== Contents of {self.current_dir} ===")
        try:
            for item in os.listdir(self.current_dir):
                full_path = os.path.join(self.current_dir, item)
                stats = os.stat(full_path)
                item_type = 'DIR' if os.path.isdir(full_path) else 'FILE'
                size = f"{stats.st_size:>10} bytes" if item_type == 'FILE' else " " * 15
                mod_time = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")
                print(f"{item_type} {size} {mod_time} {item}")
            print("================================")
            self.log_operation("List Directory", self.current_dir)
        
        except PermissionError:
            print(f"Error: No permission to list '{self.current_dir}'")
        except Exception as e:
            print(f"Error listing directory: {e}")

if __name__ == "__main__":
    app = FileManager()
    app.run()