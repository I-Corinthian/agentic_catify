import os 
from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
from tqdm import tqdm

class CatifyDataPrep():
    def __init__(self, dataset_path,dest_path):
        self.dataset_folder = dataset_path 
        self.dest_path = dest_path 
        self.min_pixels = 256*28*28
        self.max_pixels = 1280*28*28
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct", torch_dtype="auto", device_map="auto")
        self.processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct", min_pixels=self.min_pixels, max_pixels=self.max_pixels)

    def mk_msg(self,img):
        message = [
                        {
                            "roal": "user",
                            "content": [
                                {"type": "image","image": img,},
                                {"type":"text","text":"Choose exactly ONE tag from this list that best describes the cat’s emotion in the meme image output only the tag:[happy,angry,sad,shocked,confused,sleepy,scared,evil,neutral]"},
                            ]
                        }
                    ]
        return message
    
    def run(self):
        import os
        import shutil
        # get all images 
        imgs = os.listdir(self.dataset_folder)

        for img in tqdm(imgs):
            # making input message 
            img = os.path.join(self.dataset_folder,img)
            message = self.mk_msg(img)
            # preparing input 
            text = self.processor.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
            image_inputs, video_inputs = process_vision_info(message)
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to("cuda")

            # Inference: Generation of the output
            generated_ids = self.model.generate(**inputs, max_new_tokens=128)
            generated_ids_trimmed = [
                out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )[0]

            # make destination folder 
            os.makedirs(self.dest_path,exist_ok=True)
            # make subfolder
            dest = os.path.join(self.dest_path,output_text)
            os.makedirs(dest,exist_ok=True)
            # copy image to subfolder 
            try:
                shutil.copy2(img, dest)
            except e:
                print(f"Error {e}")

          
        
data_prep = CatifyDataPrep("datasets/cats_from_memes","datasets/cat_memes")

data_prep.run()