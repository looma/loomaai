import os
import pathlib
import sys
import time
import pandas as pd
import pymupdf4llm

class Directory:
    def __init__(self, basedir):
        self.dirname = basedir + "/" + "files"
        self.basepath = pathlib.Path(self.dirname)

    def files(self, pattern):
        all_files = []
        for i in self.basepath.rglob(pattern):
            parent = str(i.parent).split("/")[-1]
            #name = parent + "/" + i.name
            name = i.name
            #all_files.append((name, parent, time.ctime(i.stat().st_ctime)))
            all_files.append((name, time.ctime(i.stat().st_ctime)))
        return all_files

    def df(self, filelist):
        #cols = ["File", "Parent", "Created"]
        cols = ["File", "Created"]
        df = pd.DataFrame.from_records(filelist, columns=cols)
        df["Select"]=False
        return df

    def delete_files(self, df):
        for f in df["File"]:
            filename = self.dirname + "/" + f
            if os.path.isfile(filename):
                os.remove(filename)
            if os.path.isdir(filename):
                os.rmdir(filename)

    def convert_file(self, file_path):
        file_name = os.path.basename(file_path)
        md_text = pymupdf4llm.to_markdown(file_path)
        #st.markdown(md_text)
        mdpath = file_path + "-mdown"
        if not os.path.exists(mdpath): 
            os.mkdir(mdpath)
        mdfile = os.path.join(mdpath,file_name+".md")
        with open(mdfile, "w") as f:
            f.write(md_text)

    def convert_files(self, df):
        for f in df["File"]:
            self.convert_file(self.dirname + "/" + f)
