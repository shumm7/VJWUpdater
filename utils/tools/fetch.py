import urllib.error
import urllib.request
import urllib.parse

class Fetch:
    def download(url, dst_path):
        with urllib.request.urlopen(url, timeout=10) as web_file:
            data = web_file.read()
            with open(dst_path, mode='wb') as local_file:
                local_file.write(data)