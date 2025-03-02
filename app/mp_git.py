import urequests
import hashlib
import binascii
import os
import json
import time
from configs.git_config import *
from configs.sys_config import *
from phew import logging
import machine
import _thread

logging.enable_logging_types(logging.LOG_INFO)
#logging.enable_logging_types(logging.LOG_ALL)

app_trees_url_sha = None
REBUILD_FILE_FLAG = "/rebuild_file_flag"
ROOT_PATH = "/"
# Static URLS
# GitHub uses 'main' instead of master for python repository trees
GITHUB_URL = f'https://github.com/{GITHUB_OWNER}/{GITHUB_REPOSITORY}'
GITHUB_TREES_API_URL = f'https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPOSITORY}/git/trees/'
RAW_URL = f'https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPOSITORY}/master/'

def pull(f_path ):
   # print(f'pulling {f_path} from github')
   # logging.info(f'pulling {f_path} from github')
    os.chdir(ROOT_PATH)
    headers = {'User-Agent': 'mp_ota_from_git'}
    # ^^^ Github Requires user-agent header otherwise 403
    if GITHUB_TOKEN != "":
      headers['authorization'] = "bearer %s" % GITHUB_TOKEN
    raw_url = f"{RAW_URL}{GITHUB_APP_FOLDER}/{f_path}"
    logging.debug(f'pulling {f_path} from {raw_url}')
    r = urequests.get(raw_url, headers=headers)
   # print(f"status http:    {r.status_code}")
  #  logging.debug(f'status http: {r.status_code} {r.headers}')
    f_path = ROOT_PATH + f_path
    #r_content = r.text
    #logging.info(f'content: {r_content}')
    try:
        file_type = r.headers['Content-Type']
       # print(file_type)
        logging.debug(f'file type: {file_type}')
        if file_type.find("text") >= 0:
            r_content = r.content.decode('utf-8')
            new_file = open(f_path, 'w')
        else:
            r_content = r.content
            new_file = open(f_path, 'wb')

        new_file.write(r_content)
        new_file.close()
       # print(f"saved file {f_path}")
        logging.debug(f'saved file {f_path}')
    except:
       # print('decode fail ')
        logging.info(f'decode fail')
        try:
            new_file.close()
        except:
            logging.error('tried to close new_file to save memory durring raw file decode')
        return False
    return True

def pull_git_tree(git_folder, recursive=False):
    headers = {'User-Agent': 'mp_ota_from_git'}
    # ^^^ Github Requires user-agent header otherwise 403
    if GITHUB_TOKEN != "":
        headers['authorization'] = "bearer %s" % GITHUB_TOKEN
    if recursive:
        giturl=f"{GITHUB_TREES_API_URL}{git_folder}?recursive=1"
    else:
        giturl=f"{GITHUB_TREES_API_URL}{git_folder}"
    payload = urequests.get(giturl, headers=headers)
    return_code = payload.status_code
    if return_code == 200:
        git_tree = json.loads(payload.content.decode('utf-8'))
        if 'tree' in git_tree:
            return git_tree
    else:
        logging.error(f'\nGit url {giturl} \n')
        logging.error(f'\nGit payload {payload} \n')
        logging.error(f'\nGit return_code {return_code} \n')
        logging.error(f'\nGit branch and folder {git_folder} not found.\n')
        #raise Exception(f'Default branch {GITHUB_BRANCH} not found.')
        return None

def get_app_tree(tree=None):
    if tree is None:
        tree = pull_git_tree(GITHUB_BRANCH, recursive=False)
    try:
        for elem in tree['tree']:
            print(elem['path'])
            if elem['type'] != 'tree':
                continue
            if elem['path'] == GITHUB_APP_FOLDER:
                app_trees_url_sha = elem['sha']
                app_tree = pull_git_tree(app_trees_url_sha, recursive=True)
                return app_tree
    except Exception as e:
        print(e)
    return None

def is_directory(file_name):
    try:
        if os.stat(file_name)[0] & 0x4000:
            logging.debug(f"filename {file_name} is tree")
            return True
        else:
            logging.debug(f"{file_name} not is tree ")
            return False
    except OSError:
        logging.error(f"{file_name} check tree error ")
        return False

def build_internal_tree(rebuild=False):
    SHA1_INTERNAL_SAVE_FILE = "/sha1_internal_save_file.json"
    internal_tree = {}
    os.chdir(ROOT_PATH)
    try:
        print("Testing saved sha1...")
        os.stat(SHA1_INTERNAL_SAVE_FILE)
        # File was found, attempt read sha1...
        with open(SHA1_INTERNAL_SAVE_FILE, "r") as sha_file:
            internal_tree = json.load(sha_file)
            logging.info(internal_tree)
    except:
        rebuild = True

    if rebuild:
        logging.info("rebuild internal sha1 file")
        for item in os.listdir():
            if EXCLUDE_CONFIG_FILES:
                if item.endswith("_config.py"):
                    continue
            if item in EXCLUDE_LIST:
                continue
            add_to_tree(item, internal_tree)

        with open(SHA1_INTERNAL_SAVE_FILE, "w") as sha_file:
            json.dump(internal_tree, sha_file)
           # sha_file.close()
    logging.info(internal_tree)
    return internal_tree

def add_to_tree(dir_item, internal_tree):
   # print(dir_item)
    curent_path = os.getcwd()
    logging.debug(f"current path is {curent_path}")
    if curent_path != ROOT_PATH:
        file_path = curent_path + '/' + dir_item
    else:
        file_path = curent_path + dir_item
    #print(f'sub_path: {file_path}')
    if is_directory(file_path) and len(os.listdir(file_path)) >= 1:
        os.chdir(file_path)
        for i in os.listdir():
            add_to_tree(i, internal_tree)
        os.chdir('..')
    else:
        try:
            subfile_path = file_path[1:]
          #  subfile_path = file_path.replace(ROOT_PATH, "")
            internal_tree[subfile_path] = get_hash(file_path)
        except OSError: # type: ignore # for removing the type error indicator :)
           # print(f'{dir_item} could not be added to tree')
            logging.error(f'{dir_item} could not be added to tree')

def update(rebuild=False):
    update_list = []
    os.chdir(ROOT_PATH)
    git_app_tree = get_app_tree()
   # print(git_app_tree)
    logging.debug(git_app_tree)
    if git_app_tree is None:
        return None
    git_app_tree_list = git_app_tree.get('tree',[])
    logging.info(git_app_tree_list)
    if git_app_tree_list is None:
        return None
    internal_tree = build_internal_tree(rebuild=rebuild)
    logging.debug(internal_tree)
    for git_file_dict in git_app_tree_list:
        if git_file_dict.get('type') == 'blob':
            file_path = git_file_dict.get('path')
            internal_sha1 = internal_tree.pop(file_path, None)
            if EXCLUDE_CONFIG_FILES:
                if file_path.endswith("_config.py"):
                    logging.debug(f"exclude config file {file_path}")
                    continue
            if file_path in EXCLUDE_LIST:
                logging.debug(f"exclude file {file_path}")
                continue
            file_sha1 = git_file_dict.get('sha')
            logging.debug(f"file {file_path} has git sha {file_sha1} internal sha {internal_sha1}")
            if internal_sha1 is None:
                update_list.append(file_path)
                logging.info(f'updated {file_path}')
                continue
            if file_sha1 != internal_sha1:
                update_list.append(file_path)
                logging.info(f'updated {file_path}')
                #internal_tree.pop(file_path)
        elif git_file_dict.get('type') == 'tree':
            dir_path = git_file_dict.get('path')
            try:
                os.mkdir(dir_path)
                log_str = f'{dir_path} dir add to int mem'
                logging.info(log_str)
            except:
                logging.error(f'failed dir to {dir_path} dir may already exist')

    logging.info("-------------------------delete -------------------------------")
    logging.info(f"internal_tree delete list  {internal_tree}")
    for file_name in internal_tree:
        if EXCLUDE_CONFIG_FILES:
            if file_name.endswith("_config.py"):
                continue
        if file_name in EXCLUDE_LIST:
            continue
        if is_directory(file_name):
            continue
        try:
            os.remove(file_name)
            logging.info(f'{file_name} file removed from int mem')
        except:
            logging.error(f'{file_name} failed to delete old file')
    logging.info("-------------------------update -------------------------------")
    logging.info(f"update list  {update_list}")
    for file_name in update_list:
        if EXCLUDE_CONFIG_FILES:
            if file_name.endswith("_config.py"):
                continue
        if file_name in EXCLUDE_LIST:
            continue
        try:
            pull(file_name)
            logging.info(file_name + ' updated')
        except:
            logging.info(file_name + ' failed to pull')

    if len(update_list) > 0:
        return True
    return False


def get_hash(file_name):
   # print(file_name)
    #file_stats = os.stat(file_name)
    #file_size = file_stats.st_size
   # try:
    with   open(file_name, mode='rb') as o_file:
        content = o_file.read()
        header = f"blob {len(content)}\0".encode('utf-8')
        logging.debug(f"file {file_name} header {header}")
        data = header + content
        # Calculate SHA-1 hash
        s_hash =  hashlib.sha1(data)
        s_hash = s_hash.digest()
        sha1_hash = binascii.hexlify(s_hash)
        decoded_string = sha1_hash.decode("utf-8")
      #  print(sha1_hash)
        logging.debug(f"sha1 {file_name}  {decoded_string}")
        return decoded_string
    # except:
    #     logging.error(f"cannot get sha1 {file_name}")
    #     return None

def get_rebuild_flag():
    try:
        os.stat(REBUILD_FILE_FLAG)
        return True
    except:
        return False

def set_rebuild_file_flag():
    ff = open(REBUILD_FILE_FLAG, "w")
    ff.write("1")
    ff.close()

def machine_reset():
    time.sleep(5)
    print("Resetting...")
    machine.reset()

def read_reboot_counter():
    reboot_counter = 0
    with open("reboot_counter.txt", "r") as reboot_counter_file:
        reboot_counter = reboot_counter_file.read(1)
        logging.info(f"reboot counter is {reboot_counter}")
        try:
            reboot_counter = int(reboot_counter)
        except:
            reboot_counter = 0
        return reboot_counter

def add_reboot_counter(reboot_counter):
    reboot_counter += 1
    with open("reboot_counter.txt", "w") as reboot_counter_file:
        reboot_counter_file.write(str(reboot_counter))

def main():
    app_update = False
    if AUTO_UPDATE_FROM_GIT:
        rebuild = False
        if REBUILD_SHA1_INTERNAL_FILE or get_rebuild_flag():
            rebuild = True
        app_update = update(rebuild)
    if app_update:
        set_rebuild_file_flag()
        if AUTO_RESTART_AFTER_UPDATE:
            reboot_counter = read_reboot_counter()
            if reboot_counter <= 3:
                add_reboot_counter(reboot_counter)
                print("Updated to the latest version! Rebooting...")
                _thread.start_new_thread(machine_reset, ())
            #machine_reset()

if __name__ == '__main__':
    main()

   #file_n = "text-16.pf"
   #file_n = "main.py"
   #pull(file_n)



