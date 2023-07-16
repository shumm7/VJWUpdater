import os, json

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
