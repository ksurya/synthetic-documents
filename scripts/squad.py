import os
import json
import image_utils
import document_utils


class Documents(object):
    
    def __init__(self, filename):
        self.ds = {}
        self.keys = []
        with open(filename) as fp:
            data = json.load(fp)
        for idx, item in enumerate(data["data"]):
            title = item["title"]
            for idy, para in enumerate(item["paragraphs"]):
                context = para["context"]
                key = f"{title}__{idx}__{idy}"
                self.ds[key] = context
                self.keys.append(key)

    def __len__(self):
        return len(self.ds)
    
    def __getitem__(self, idx):
        key = self.keys[idx]
        return {"id": key, "doc": self.ds[key]}

    
    
def factory(config):
    
    def worker(doc):
        img, ann = image_utils.doc_to_image(
            doc=doc, 
            font_file=config["font_file"],
            font_size=config["font_size"],
            bg_color=config["bg_color"],
            fg_color=config["fg_color"],
            margin=config["margin"],
            line_space=config["line_space"],
            word_space=config["word_space"]
        )
        filename = os.path.join(kw["path"], item["id"])
        img.save(filename + ".png")
        with open(filename + ".json", "w", encoding="utf8") as fp:
            json.dump(ann, fp, indent=2, ensure_ascii=False)
        return filename