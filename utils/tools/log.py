import datetime

class Log:
    def print(msg: str, _type: str, category: str, logging: bool = True):
        if category!=None:
            if len(category)>0:
                category = f"<{category}>"
        else:
            category = ""
        
        if _type=="info":
            _type="INFO"
        elif _type=="warn":
            _type="WARN"
        elif _type == "error":
            _type="ERROR"
        else:
            _type = "UNKNOWN"

        if type(msg)==type(""):
            if logging:
                with open("log.txt", "a", encoding="utf-8") as fp:
                    fp.write(f'[{datetime.datetime.now()}][{_type}]{category} {msg}\n')

                
                print(f'[{datetime.datetime.now()}][{_type}]{category} {msg}')
    
    def append(msg: str):
        if type(msg)==type(""):
            with open("log.txt", "a", encoding="utf-8") as fp:
                fp.write(f'[{datetime.datetime.now()}] {msg}\n')

    def exception(e: Exception, msg: str = None, category: str = None):
        if type(msg)!=type(""):
            msg = "Unknown exception has occured."
        if category!=None:
            if len(category)>0:
                category = f"<{category}>"
        else:
            category = ""
        
        Log.append(f'[{datetime.datetime.now()}][ERROR]{category} {msg}\n\tdetail: {e}')
        Log.print(msg, "error", category, False)
  