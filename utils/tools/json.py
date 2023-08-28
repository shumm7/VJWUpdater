import os, json, types

class JSON:
    def __create__(filename: str, formats: dict) -> None:
        """ Create a json file """
        
        file_path = filename
        file_dir = os.path.dirname(file_path)
        os.makedirs(file_dir, exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w") as fp:
                json.dump(formats, fp, indent=2)


    def read(filename: str, force: bool = True) -> dict:
        """Read json file"""
        try:
            with open(filename, "r", encoding='utf-8') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            if force:
                JSON.__create__(filename, {})
                return JSON.read(filename, False)
        return data

    def save(filename: str, data: dict) -> None:
        """Save data to json file"""
        try:
            with open(filename, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, indent=2, ensure_ascii=False)
        except FileNotFoundError:
            JSON.__create__(filename, {})
            return JSON.save(filename, data)

class Lua:
    def ntab(count: int=1) -> str:
        return "\t" * count
    
    def to_lua(data, depth: int = 0):
        output = ""

        if type(data)==list:
            lines = []
            for v in data:
                lines.append(Lua.ntab(depth+1) + Lua.to_lua(v, depth+1))
            if len(lines)>0:
                output = "{\n" + ",\n".join(lines) + ",\n" + Lua.ntab(depth) +"}"
            else:
                output = "{\n" + Lua.ntab(depth) +"}"
        elif type(data)==dict:
            lines = []
            for k,v in data.items():
                lines.append(Lua.ntab(depth + 1) + Lua.make_key(k) + " = " + Lua.to_lua(v, depth+1))
            if len(lines)>0:
                output = "{\n" + ",\n".join(lines) + ",\n" + Lua.ntab(depth) +"}"
            else:
                output = "{\n" + Lua.ntab(depth) +"}"
        elif type(data)==str:
            return "\"" + data + "\""
        elif type(data)==int or type(data)==float:
            return str(data)
        else:
            raise TypeError
            
        return output

    def make_key(key: str):
        return f"[\"{key}\"]"