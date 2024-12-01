import json
import os, subprocess
import sys
import whisper
from whisper.utils import get_writer
import configparser

config = configparser.ConfigParser()
setting_file = os.path.dirname(os.path.abspath(__file__))+os.path.sep+"setting.ini"
print("Setting file :"+setting_file)
config.read(setting_file,encoding="UTF-8")

# file_path = config.get('input','filename')
# print(file_path)
writer_format = json.loads(config.get('output','format'))
print("output format :"+ str(writer_format))



def split_file(file, folder):
    global file_suffix
    file_suffix = os.path.basename(file).split(".")[1]
    file_name = os.path.basename(file).split(".")[0]
    # file_suffix = pathlib.Path(file).suffix
    # file_name = os.path.basename(file).split(".")[0]
    os.makedirs(folder,exist_ok=True)
    split_seconds = config.get('input','split_file_seconds')
    voice_splitter_coomand = f"ffmpeg -i {file} -f segment -segment_time {split_seconds} -c copy {folder+os.path.sep+file_name}_out%03d.{file_suffix}"
    print("Command : "+ voice_splitter_coomand)
    subprocess.call(voice_splitter_coomand)


def transcribe_file(folder):
    model_size = config.get('input','model_size')
    model = whisper.load_model(model_size)
    writers = [get_writer(format,output_folder) for format in writer_format]
    
    for item in os.listdir(folder): 
        print(os.path.join(folder,item))
        # subprocess.call(f"whisper {os.path.join(folder,item)} --language zh --model large --threads 8")
        result = model.transcribe(os.path.join(folder,item),language="zh")
        for writer in writers:
            writer(result, item)  
    print(result)


def delete_files(folder,keyword):
    for items in os.listdir(folder):
        if keyword in items:
            print(os.path.join(folder,items))
            os.remove(os.path.join(folder,items))


def combine_files(folder):
    output_folder = folder
    data = ""
    for txt_file in os.listdir(output_folder):
        if ".txt" in txt_file:
            print(txt_file)
            with open(output_folder + os.sep + txt_file,"r",encoding="UTF-8") as txt_file_content:
                data += txt_file_content.read()
    print(data)
    file_name = os.path.basename(file_path).split(".")[0]
    with open(output_folder + os.sep +f"{file_name}.txt","w",encoding="UTF-8") as file:
        file.write(data)

if __name__ == "__main__":
    file_path = sys.argv[1]
    dir_path = os.path.dirname(file_path)
    output_folder = dir_path + os.path.sep + config.get('output','output_folder_name')
    print("output folder :"+output_folder)

    split_file(file_path,output_folder)
    transcribe_file(output_folder)
    delete_files(output_folder,file_suffix)
    combine_files(output_folder)
    delete_files(output_folder,"out")