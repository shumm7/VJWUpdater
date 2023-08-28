import os
import zipfile
import shutil
import subprocess
from utils.tools.fetch import Fetch

class Conversion():
    ww2ogg_link: str = "https://github.com/hcs64/ww2ogg/releases/download/0.24/ww2ogg024.zip"
    revorb_link: str = "https://github.com/ItsBranK/ReVorb/releases/download/v1.0/ReVorb.exe"
    vgmstream_link: str = "https://github.com/vgmstream/vgmstream/releases/download/r1810/vgmstream-win.zip"

    def __init__(self) -> None:
        self.check_encoder()

    def check_encoder(self):
        if not os.path.exists(f"tools/ww2ogg/ww2ogg.exe"):
            os.makedirs("tools/ww2ogg", exist_ok=True)
            Fetch.download(self.ww2ogg_link, f"tools/ww2ogg/ww2ogg.zip")
            with zipfile.ZipFile('tools/ww2ogg/ww2ogg.zip') as zf:
                zf.extractall('tools/ww2ogg')
            os.remove("tools/ww2ogg/ww2ogg.zip")

        if not os.path.exists(f"tools/ww2ogg/ReVorb.exe"):
            os.makedirs("tools/ww2ogg", exist_ok=True)
            Fetch.download(self.revorb_link, f"tools/ww2ogg/ReVorb.exe")
        
        if not os.path.exists(f"tools/vgmstream/test.exe"):
            os.makedirs("tools/vgmstream", exist_ok=True)
            Fetch.download(self.vgmstream_link, f"tools/vgmstream/vgmstream.zip")
            with zipfile.ZipFile('tools/vgmstream/vgmstream.zip') as zf:
                zf.extractall('tools/vgmstream')
            os.remove("tools/vgmstream/vgmstream.zip")

        os.makedirs("tools/ww2ogg/temp", exist_ok=True)
        os.makedirs("tools/vgmstream/temp", exist_ok=True)
    
    def wem_to_ogg(self, input, output):
        try:
            basename = os.path.basename(input)
            shutil.copyfile(input, f"tools/ww2ogg/temp/{basename}")
            name, ext = os.path.splitext(basename)
            subprocess.run(f"./tools/ww2ogg/ww2ogg.exe ./tools/ww2ogg/temp/{name}.wem --pcb ./tools/ww2ogg/packed_codebooks_aoTuV_603.bin")
            subprocess.run(f"./tools/ww2ogg/ReVorb.exe ./tools/ww2ogg/temp/{name}.ogg")
            shutil.move(f"tools/ww2ogg/temp/{name}.ogg", output)
        finally:
            if os.path.exists(f"tools/vgmstream/temp/{name}.ogg"):
                os.remove(f"tools/vgmstream/temp/{name}.ogg")
            if os.path.exists(f"tools/vgmstream/temp/{name}.wem"):
                os.remove(f"tools/vgmstream/temp/{name}.wem")

    def wem_to_wav(self, input, output):
        try:
            basename = os.path.basename(input)
            shutil.copyfile(input, f"tools/vgmstream/temp/{basename}")
            name, ext = os.path.splitext(basename)
            subprocess.run(f"./tools/vgmstream/test.exe -o ./tools/vgmstream/temp/{name}.wav ./tools/vgmstream/temp/{name}.wem")
            shutil.move(f"tools/vgmstream/temp/{name}.wav", f"{output}/{name}.wav")
        finally:
            if os.path.exists(f"tools/vgmstream/temp/{name}.wav"):
                os.remove(f"tools/vgmstream/temp/{name}.wav")
            if os.path.exists(f"tools/vgmstream/temp/{name}.wem"):
                os.remove(f"tools/vgmstream/temp/{name}.wem")