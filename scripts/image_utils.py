from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from collections import defaultdict
from tqdm import tqdm

import json


def show_bounding_box(img, annotation, spread=0, color="red"):
    x, y, w, h = annotation
    x -= spread
    y -= spread
    w += 2 * spread
    h += 2 * spread
    new = img.copy().convert("RGB")
    draw = ImageDraw.Draw(new)
    draw.rectangle((x, y, x + w, y + h), outline=color)
    return new


def expand_image(img, new_h, new_w, bg_color="black"):
    left = (new_w - img.width) // 2
    right = (new_w - img.width) - left
    top = (new_h - img.height) // 2
    bottom = (new_h - img.height) - top
    img = add_margin(img, top, right, bottom, left, bg_color)
    return img, left, top


def equalize_images(image_items, feature_indent=2):
    # image_items = [{in_image, in_features, out_image, out_features, bg_color}]
    # get max sizes
    max_h = -float("inf")
    max_w = -float("inf")
    for item in image_items:
        im = Image.open(item["in_image"])
        max_h = max(max_h, img.height)
        max_w = max(max_w, img.width)
    
    processed = 0
    for item in tqdm(image_items):
        im = Image.open(item["in_image"])
        if im.height != max_h or im.width != max_w:
            # expand image
            im, offset_x, offset_y = expand_image(im, max_h, max_w, item["bg_color"])
            im.save(item["out_image"])
            # offset feature positions
            with open(item["in_features"], encoding="utf8") as fp:
                features = json.load(fp)
            for key, bb_list in features.items():
                for bb in bb_list:
                    bb[0] += offset_x
                    bb[1] += offset_y
            with open(item["out_features"], "w", encoding="utf8") as fp:
                json.dump(features, fp, indent=feature_indent, ensure_ascii=False)
            processed += 1
    
    return processed


def create_image(
    sentence, 
    font_file, 
    font_size=12, 
    bg_color="black", 
    fg_color="white", 
    img_width=None, 
    img_height=None
):
    font = ImageFont.truetype(font_file, font_size)
    w, h = font.getsize(sentence)
    if img_width is not None:
        w = img_width
    if img_height is not None:
        h = img_height
    img = Image.new("1", (w, h), color=bg_color)
    draw = ImageDraw.Draw(img)
    draw.text((0,0), sentence, font=font, fill=fg_color)
    return img


def stack_images(images, line_space=0, bg_color="black"):
    w = max(i.width for i in images)
    h = sum(i.height for i in images) + (line_space * (len(images)-1))
    stacked = Image.new("1", (w, h), color=bg_color)
    start = 0
    for i, img in enumerate(images):
        stacked.paste(img, (0, start))
        start += img.height + line_space
    return stacked


def append_images(images, word_space=0, bg_color="black"):
    w = sum(i.width  for i in images) + ((len(images) - 1) * word_space)
    h = max(i.height for i in images)
    appended = Image.new("1", (w, h), color=bg_color)
    start = 0
    for i, img in enumerate(images):
        appended.paste(img, (start, 0))
        start += img.width + word_space
    return appended


def add_margin(image, top=0, right=0, bottom=0, left=0, bg_color="black"):
    w = image.width + right + left
    h = image.height + top + bottom
    enlarged = Image.new(image.mode, (w, h), bg_color)
    enlarged.paste(image, (left, top))
    return enlarged


def doc_to_image(
    doc,
    sentence_iterator,
    word_iterator,
    font_file, 
    font_size=12,
    bg_color="black",
    fg_color="white",
    margin=0,
    line_space=0,
    word_space=0,
    whitespace_ann=False,
):
    annotations = defaultdict(list) # token -> [(x, y, w, h), ... ]
    images = []
    cursor_y = margin
    for sentence in sentence_iterator(doc):
        cursor_x = margin
        sentence_images = []
        for token in word_iterator(sentence):
            token_img = create_image(token, font_file, font_size, bg_color, fg_color)
            if token.strip() and whitespace_ann:
                annotations[token].append((cursor_x, cursor_y, token_img.width, token_img.height))
            sentence_images.append(token_img)
            cursor_x += token_img.width + word_space
        appended = append_images(sentence_images, word_space, bg_color)
        images.append(appended)
        cursor_y += appended.height + line_space
    x = stack_images(images, line_space, bg_color)
    x = add_margin(x, margin, margin, margin, margin, bg_color)
    return x, annotations
