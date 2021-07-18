from PIL import ImageFile
from PIL import Image
ImageFile.LOAD_TRUNCATED_IMAGES = True
def combineImage(full_width,full_height,image_key,image_list,index,toon_title_folder):
    canvas = Image.new('RGB', (full_width, full_height), 'white')
    output_height = 0
    for im in image_list:
        width, height = im.size
        if width<0.9*full_width:
            wpercent = (full_width/float(width))
            hsize = int((float(height)*float(wpercent)))
            im = im.resize((full_width,hsize), Image.ANTIALIAS)
        width, height = im.size
        canvas.paste(im, (0, output_height))
        output_height += height
    canvas.save(toon_title_folder+'/out/'+image_key+"_combined_"+str(index)+'.jpg')
def listImage(image_key,image_value,q,toon_title_folder):
    full_width, full_height,index = 0, 0, 1
    image_list = []
    for i in image_value:
        im = Image.open('./'+toon_title_folder+'/out/'+image_key+"_"+str(i)+'.jpg')
        width, height = im.size
        if full_height+height > 65000:
            combineImage(full_width,full_height,image_key,image_list,index,toon_title_folder)
            index = index + 1
            image_list = []
            full_width, full_height = 0, 0
        image_list.append(im)
        full_width = max(full_width, width)
        full_height += height
    combineImage(full_width,full_height,image_key,image_list,index,toon_title_folder)
    #for i in image_value:
        #os.remove(os.path.join(toon_title_folder+'/out/'+image_key+"_"+str(i)+'.jpg'))
    #self.log(image_key+' is being deleted permanently')