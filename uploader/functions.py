import pprint
pp = pprint.PrettyPrinter(indent=4)
from PIL import Image
from .s3_uploader import upload_file_to_S3
from django.conf import settings

def create_thumb(filePath, largeSideMax = 500):
    print('INSIDE FUNCTION  create_thumb(filePath, largeSideMax)')
    # configure vars
    mediaUplaodFolder = '/media/'
    bucketSubDir = settings.S3_BUCKET_SUB_DIR
    bucket = settings.S3_BUCKET
    
    extraArgs = {'ACL': 'public-read', 'ContentType': 'image'}
    data={}
    filePathFragments = filePath.split("/")
    uploadedfilename = filePathFragments[len(filePathFragments)-1]
    uploadedfilename = uploadedfilename.replace(' ','_')
    filename = uploadedfilename.replace(mediaUplaodFolder, '')
    filenameFragments = filename.split(".")
    uploadedFileSuffix = filenameFragments[len(filenameFragments)-1]


    filePathCleansed = filePath.replace(' ','_')
    tempImageFolder = filePathCleansed.replace(filename, '')
    # set up pillow object
    print('pillowImageObj = Image.open(filePath) ', filePath)
    pillowImageObj = Image.open(filePath)
    # create jpg object
    # Max pixels for width or height from param largeSideMax = 500
    # Get the size dims of the tiff
    width, height = pillowImageObj.size
    # Determine which size is bigest & calc ratio
    if width > height:
        sizingRatio = largeSideMax/width
    else:
        sizingRatio = largeSideMax/height
    #Apply that ratio to both sides
    resizedWidth = width * sizingRatio
    resizedHeight = height * sizingRatio
    reNameToPng = filename + "_thumb.png"
    reNamedImagePathPng = tempImageFolder+reNameToPng
    rgb_image = pillowImageObj.convert('RGB')
    resized_image = rgb_image.resize((round(resizedWidth),round(resizedHeight)))

    try:
        resized_image.save(reNamedImagePathPng, 'PNG')

    except:
        data['create_thumbnail_msg'] = 'FAILED to RESIZE IMAGE for THUMBNAIL'
        print(data['create_thumbnail_msg'])
    
    # Store the png representation of the TIFF
    try:
        print('Attempting Thumnail upload for tiff')
        print('reNamedImagePathPng: '+reNamedImagePathPng)
        print('bucketSubDir+reName: '+bucketSubDir+reNameToPng)
        S3UploadResult = upload_file_to_S3(tempImageFolder+reNameToPng, bucket, bucketSubDir+reNameToPng, extraArgs)
        data['create_thumbnail_msg'] = 'Thumbnail uploaded to S3  : ) '  
        data['create_thumbnail_success'] = True

    except:
        data['create_thumbnail_msg'] = 'FAILED THUMBNAIL UPLOAD to S3! Check the media path is valid.'          

    return data


