from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage,HumanMessage
import prompt
import utils
import json
import os
from dotenv import load_dotenv

load_dotenv()


class CatfyPipeline():
    def __init__(self):
        self.chat_history = [SystemMessage(content=prompt.system_prompt)]
        self.model = ChatOpenAI(model='gpt-3.5-turbo')
    
    def forward(self,vid_path,output_path="cat_vid"):
        print("Extracting Audio")
        audio_path = utils.get_audio(video_path=vid_path)
        print("Preparing Trnscript")
        transcripts = utils.get_transcript(audio_path)
        user_call = prompt.user_prompt.format(tags=utils.get_tags(),transcript=transcripts)
        self.chat_history.append(HumanMessage(content=user_call))
        print("running model")
        catfy_results = self.model.invoke(self.chat_history)
        datas = json.loads(catfy_results.content)
        print("Loading images")
        os.makedirs(output_path,exist_ok=True)
        for i, segment in enumerate(datas):
            utils.get_image(segment['tag'],segment['caption'],f"{output_path}/{i+1}")
        print("preparing video")
        utils.make_vid(frames_path=output_path,audio=audio_path,datas=datas,output=f"{output_path}/catify_vid.mp4")

cat_vid = CatfyPipeline()

cat_vid.forward("assets/vid3.mp4",output_path="cat_vid3")
        