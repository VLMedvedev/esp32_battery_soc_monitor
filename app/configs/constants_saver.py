import json


def is_obj_dict(dict_obj):
    is_obj = False
    for val, key_name in dict_obj.items():
        type_name = type(val).__name__
        #    print(type_name)
        if type_name in ['int', 'bool', 'float', 'str']:
            pass
        elif type_name == 'dict':
            is_obj = is_obj_dict(val)
        elif type_name == 'list':
            is_obj = is_obj_list(val)
        else:
            is_obj = True
    return is_obj

def is_obj_list(list_obj):
    is_obj = False
    for val in list_obj:
        type_name = type(val).__name__
    #    print(type_name)
        if type_name in ['int', 'bool', 'float', 'str']:
            pass
        elif type_name == 'dict':
            is_obj =  is_obj_dict(val)
        elif type_name == 'list':
            is_obj = is_obj_list(val)
        else:
            is_obj = True
    return is_obj

def is_obj(obj):
    is_obj = False
    type_name = type(obj).__name__
    #print(type_name)
    if type_name in ['int', 'bool', 'float', 'str']:
        return False
    elif  type_name == 'dict':
        return is_obj_dict(obj)
    elif  type_name == 'list':
        return is_obj_list(obj)
    else:
        return True

class ConstansReaderWriter():
    def __init__(self, module_config_name, **kwargs):
        self.file_config_name = f"configs/{module_config_name}.py"
        import sys
        mod_name = f"configs.{module_config_name}"
      #  print(mod_name)
        self.config_dict = {}
        try:
            obj = __import__(mod_name)
            #  print(obj)
            del sys.modules[mod_name]
            obj = __import__(mod_name)
            obj_m = getattr(obj, module_config_name)
            self.config_dict = self.get_constants_dict(obj_m)
        except ImportError:
            print(ImportError)

    def get_constants_dict(self, obj):
        class_atribute_dict = obj.__dict__
        class_constants_dict = {}
        for var_name, val in class_atribute_dict.items():
            if val is None:
                continue
            upper_str= str(var_name).upper()
            if str(var_name)[0:5] != upper_str[0:5]:
                continue
            if is_obj(obj=val) :
                continue
            class_constants_dict[var_name] = val
        return class_constants_dict

    # @classmethod
    # def set_cls_attribute(cls, val, var_name):
    #     str_ex = f'cls.{var_name} = {val}'
    #     exec(str_ex)

    def get_dict(self):
        return self.config_dict

    def set_constants_from_config_dict(self, config_dict):
        #print(config_dict)
        for var_name, val in config_dict.items():
            val_dict = self.config_dict.get(var_name, None)
            if val_dict is None:
                continue
            new_val = str(val)
            if isinstance(val_dict, str):
                new_val = str(new_val).replace("\r","").replace("\n","")
            elif isinstance(val_dict, list):
                new_val = json.loads(new_val)
            elif isinstance(val_dict, dict):
                new_val = new_val.replace("'",'"')
                new_val = json.loads(new_val)
            elif isinstance(val_dict, bool):
                if new_val == "True" or new_val == "true":
                    new_val = True
                else:
                    new_val = False
            elif isinstance(val_dict, float):
                new_val = float(new_val)
            elif isinstance(val_dict, int):
                new_val = int(new_val)
            self.config_dict[var_name] = new_val
        self.save_constants_to_file()


    def save_constants_to_file(self):
        with open(self.file_config_name, 'w') as f:
            for var_name, val in self.config_dict.items():
                if isinstance(val, str):
                    str_wr = f'{var_name} = "{val}"'
                else:
                    str_wr = f'{var_name} = {val}'
                str_wr += "\n"
                f.write(str_wr)
           #     print(str_wr)
            f.flush()

        print(f"Constants saved to file {self.file_config_name}")


if __name__ == "__main__":
    file_config_name = "app_config"
    cr = ConstansReader(file_config_name)
    c_dict = cr.get_dict()
    print(c_dict)
    # const_dict = {'TEST_VAR_INT': 5,
    #               'TEST_VAR_LIST': [1, 6, 3],
    #               'TEST_VAR_STR': 'test_sss',
    #               'TEST_VAR_DICT': {'var1': 222, 'var2': 'str_test_11', 'var3': [12, 34, 44, 33]}
    #               }
    # cr.set_constants_from_config_dict(const_dict)
    # cr.save_constants_to_file()



