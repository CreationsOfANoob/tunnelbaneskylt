from PIL import Image, ImageFont, ImageDraw
import argparse
import json

parser = argparse.ArgumentParser(description="Konverterar TrueType-fil till texttypsnitt.")
parser.add_argument("-f", help="Sökväg till TrueType-fil", type=str, required=True)
parser.add_argument("-n", help="Namn på ny fil", type=str, required=True)
parser.add_argument("-s", help="Storlek", type=int, default=10)
args = parser.parse_args()

chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖabcdefghijklmnopqrstuvwxyzåäö1234567890.,:-*@ "
textchardict = {"characters":{}}
imsize = args.s
font = ImageFont.truetype(args.f, imsize)

for char in chars:
    charpixellength = int(font.getlength(char))
    image = Image.new("1", (charpixellength, int(imsize * 1)))
    draw = ImageDraw.Draw(image)
    draw.text((1, 0), char, 1, font = font)
    imagedata = list(image.getdata())
    rows = [imagedata[y * charpixellength:(y+1) * charpixellength] for y in range(imsize)]
    character_data = "|".join(["".join([str(c) for c in row]) for row in rows]).replace("0",".").replace("1","#")
    textchardict["characters"][char] = character_data

with open(args.n + ".json", "w") as file:
    file.write(json.dumps(textchardict, indent = 4))
