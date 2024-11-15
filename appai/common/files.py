import os
import pathlib
import shutil
import time
from typing import List, Tuple
import pandas as pd
from logzero import logger
import pymupdf4llm

class Directory:
    def __init__(self, basedir: str):
        self.dirname = os.path.join(basedir, "files")
        self.basepath = pathlib.Path(self.dirname)

    def files(self, pattern: str) -> List[Tuple[str, str, str, str]]:
        all_files = []
        for i in self.basepath.rglob(pattern):
            parent = i.parent.name
            sname = str(i.relative_to(self.dirname))
            ftype = ""
            if i.is_dir():
                ftype = "📂 Directory"
            if i.is_file():
                ftype = "🗒️ File"
            if i.is_symlink():
                ftype = "🔗 Symlink"
            ctime = time.localtime(i.stat().st_ctime)
            stime = time.strftime("%Y-%m-%d %H:%M:%S", ctime)
            all_files.append((sname, ftype, parent, stime))
        return all_files
    
    def fullpath(self, file: str) -> str:
        return os.path.join(self.dirname, file)
    
    def df(self, filelist: List[Tuple[str, str, str, str]]) -> pd.DataFrame:
        cols = ["File", "Type", "Parent", "Created"]
        return pd.DataFrame(filelist, columns=cols)

    def delete_files(self, df):
        for f in df["File"]:
            fname = self.fullpath(f)
            logger.info(f"Deleting {fname}")
            if os.path.isfile(fname):
                os.remove(fname)
            if os.path.isdir(fname):
                shutil.rmtree(fname) 
                #os.rmdir(fname)

    def convert_file(self, file_path):
        file_name = os.path.basename(file_path)
        md_text = pymupdf4llm.to_markdown(file_path)
        mdpath = file_path + "-mdown"
        if not os.path.exists(mdpath): 
            os.mkdir(mdpath)
        mdfile = os.path.join(mdpath,file_name+".md")
        with open(mdfile, "w") as f:
            f.write(md_text)

    def convert_files(self, df):
        for f in df["File"]:
            fname = self.fullpath(f)
            logger.info(f"Converting {fname}")
            self.convert_file(fname)
