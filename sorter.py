import re
import shutil
import sys
from pathlib import Path
from threading import Thread
from time import time

image = ['JPEG', 'PNG', 'JPG', 'SVG']
video = ['AVI', 'MP4', 'MOV', 'MKV']
documents = ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX']
music = ['MP3', 'OGG', 'WAV', 'AMR']
archives = ['ZIP', 'GZ', 'TAR'] 

folder_list = ['image', 'video', 'documents', 'audio', 'archives', 'others']

others = list()
Registered_extention = set()
Unknown_extention = set()

my_dict = {}

for img in image:
    my_dict.setdefault(img, 'image')
for vid in video:
    my_dict.setdefault(vid, 'video')
for doc in documents:
    my_dict.setdefault(doc, 'documents')
for mus in music:
    my_dict.setdefault(mus, 'audio')
for arc in archives:
    my_dict.setdefault(arc, 'archives')

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

TRANS = {}
for c, t in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = t
    TRANS[ord(c.upper())] = t.upper()

def normalize(name: str) -> str:
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', '_', new_name)

    if not extension:
        return new_name
    
    return f"{new_name}.{'.'.join(extension)}"

def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()

def move_files(root_path, path):
    new_name = normalize(path.name)
    file_type = get_extensions(path)

    new_dir = root_path/my_dict.get(file_type, 'others')
    new_dir.mkdir(exist_ok=True)
    path.replace(new_dir/new_name)

def move_archives(root_path, path):
    file_type = get_extensions(path)
    new_dir = root_path/my_dict.get(file_type, 'others')
    new_dir.mkdir(exist_ok=True)


    new_name = normalize(path.name.replace(file_type, ''))
    new_name, *extention = new_name.split('.')
    archive_folder = new_dir/new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path.resolve()), str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
        path.unlink()
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        path.unlink()
        return
    path.unlink()

def scan_folder(root_path, path):
    threads = []
    for item in path.iterdir():
        if item.is_dir():
            if item.name not in folder_list:
                th = Thread(target=scan_folder, args=(root_path, item))
                threads.append(th)

        if item.is_file():
            file_type = item.suffix.replace('.', '').upper()
            if file_type not in archives:
                th = Thread(target=move_files, args=(root_path, item))
                threads.append(th)
            else:
                th = Thread(target=move_archives, args=(root_path, item))
                threads.append(th)

        extension = get_extensions(file_name=item.name)
        try:
            container = my_dict[extension]
            Registered_extention.add(extension)
        except KeyError:
            Unknown_extention.add(extension)
    

    [th.start() for th in threads]
    [th.join() for th in threads]

            
def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass 

def result(path):
    for item in path.iterdir():
        if item.is_dir():
            print(item)
            print('----------------------------------------------------------------')
            result(item)
        if item.is_file():
            print(normalize(item.name))


def main():
    start_time = time()
    path = Path(sys.argv[1]) 
    scan_folder(path, path)
    remove_empty_folders(path)
    result(path)

    if len(Registered_extention) > 0:
        print(f'Registered extention: {Registered_extention}')

    if len(Unknown_extention) > 0:
        print(f'Unknown extention: {Unknown_extention}')
    end_time = time()
    print(end_time - start_time)

if __name__ == '__main__':
  
    main()
