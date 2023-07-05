from django.shortcuts import render, HttpResponse
from home.models import Contact
import pytesseract
import io
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import cv2
import numpy
import base64
from home.models import CarPlate
import tempfile
from wsgiref.util import FileWrapper
import os
import re
import requests
from home.models import Invoice



# Create your views here.

def home(request):
    return render(request, 'index.html')

def contact(request):

    if request.method == "POST":
        #handle the form
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        contact = Contact(name = name, email = email, subject = subject, message = message )
        contact.save()

    #return HttpResponse('Message Sent Successfully')
        return render(request, 'index.html', {'submitted': True})

    return render(request, 'index.html')

def text_extract(request):

     if request.method == 'POST' and request.FILES['image']:
        # Get the uploaded image
        image_file = request.FILES['image']
        image_data = image_file.read()
        image = Image.open(io.BytesIO(image_data))

        _, jpeg_data = cv2.imencode('.jpg', cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR))
        image_base64 = base64.b64encode(jpeg_data).decode()

        # Preprocess the image for better OCR accuracy
        image = image.convert('L')  # Convert to grayscale
        image = image.filter(ImageFilter.SHARPEN)  # Sharpen the image
        image = ImageOps.autocontrast(image)  # Increase contrast
        image = ImageOps.invert(image)  # Invert the colors

        image = image.filter(ImageFilter.SMOOTH)  # Remove noise
        threshold = 100  # Binarization threshold
        # Binarize the image
        image = image.point(lambda x: 255 if x > threshold else 0)

        # Use pytesseract to extract text from the image
        text = pytesseract.image_to_string(image, lang='eng', config='--psm 11')
        extracted_text = text.replace('\n', '<br>')

        # Save the extracted text to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(text.encode())
            temp_file_path = temp_file.name

        # Return the extracted text in the response
        context = {'text': extracted_text, 'image': image_base64, 'file_name': os.path.basename(temp_file_path)}
 
        return render(request, 'Text_Extract.html', context)
        
     return render(request, 'Text_Extract.html')

def download_file(request, file_name):
    file_path = os.path.join(tempfile.gettempdir(), file_name)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            file_wrapper = FileWrapper(file)
            response = HttpResponse(file_wrapper, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=' + file_name
            response['Content-Length'] = os.path.getsize(file_path)
            return response

    return HttpResponse("File not found.")

def licence_plate(request):

     if request.method == 'POST' and request.FILES['image']:
        # Get the uploaded image
        image_file = request.FILES['image']
        
        image_bytes = image_file.read()
        image_array = numpy.frombuffer(image_bytes, dtype=numpy.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        _, jpeg_data = cv2.imencode('.jpg', cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR))
        image_base64 = base64.b64encode(jpeg_data).decode()

        # Preprocess the image for better OCR accuracy

        # Convert the color image to grayscale using OpenCV's cvtColor function
        gray_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

        # Apply bilateral filtering to the grayscale image to reduce noise while preserving edges
        gray_image = cv2.bilateralFilter(gray_image,11,17,17)

        # Apply the Canny edge detection algorithm to the grayscale image to detect edges
        edged = cv2.Canny(gray_image,30,200)
        cnts, new = cv2.findContours(edged.copy(),cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        image1 = image.copy()
        cv2.drawContours(image1,cnts,-1,(0,255,0),3)

        cnts = sorted(cnts, key = cv2.contourArea, reverse = True) [:30]
        screenCnt = None
        image2 = image.copy()
        cv2.drawContours(image2,cnts,-1,(0,255,0),3)

        i = 7
        for c in cnts:
            perimeter = cv2.arcLength(c,True)
            approx = cv2.approxPolyDP(c,0.018 * perimeter, True)
            if len(approx) == 4:
                screenCnt = approx
                x,y,w,h = cv2.boundingRect(c)
                new_img = image[y:y+h,x:x+w]
                cv2.imwrite('./'+str(i)+'.png',new_img)
                i+=1
                break

        cv2.drawContours(image,[screenCnt],-1,(0,255,0),3)

        Cropped_loc = './7.png'

        # Use pytesseract to extract text from the image
        plate = pytesseract.image_to_string(Cropped_loc,lang='eng')

        # Return the extracted text in the response
        context = {'text': plate, 'image': image_base64}

        # Create a new CarPlate object with the extracted text
        car_plate = CarPlate(text=plate)

        # Save the CarPlate object to the database
        car_plate.save()

        return render(request, 'Licence_Plate.html', context)

     return render(request, 'Licence_Plate.html')

def extract_aadhaar_number(text):
    pattern = r"\d{4}\s\d{4}\s\d{4}"
    match = re.search(pattern, text)
    if match:
        aadhaar_number = match.group().replace(" ", "")
        return aadhaar_number
    else:
        return None
    
def id(request):

     if request.method == 'POST' and request.FILES['image']:
        # Get the uploaded image
        image_file = request.FILES['image']
        
        image_bytes = image_file.read()
        image_array = numpy.frombuffer(image_bytes, dtype=numpy.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        _, jpeg_data = cv2.imencode('.jpg', cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR))
        image_base64 = base64.b64encode(jpeg_data).decode()

        # Preprocess the image for better OCR accuracy

        def thick_font(image):
            image =cv2.bitwise_not(image)
            kernel=numpy.ones((2,2),numpy.uint8)
            image = cv2.dilate(image,kernel,iterations=1)
            image = cv2.bitwise_not(image)
            return(image)
        
        dilated_image = thick_font(image)

        inverted_image = cv2.bitwise_not(dilated_image)
    
        # Use pytesseract to extract text from the image
        result = pytesseract.image_to_string((inverted_image), lang="eng+mar")
        extracted_text = result.replace('\n', '<br>')

        aadhaar_number = extract_aadhaar_number(extracted_text)
        if aadhaar_number:
            aadhaar_number = aadhaar_number.replace(" ", "")

        if aadhaar_number:
            # Validate Aadhaar number using Rapid API
            validation_result = validate_aadhaar_number(aadhaar_number)

            if 'Succeeded' in validation_result:
                success_data = validation_result['Succeeded']
                status_message = success_data['Verify_status']

                context = {
                    'text': extracted_text,
                    'image': image_base64,
                    'aadhaar_number': aadhaar_number,
                    'status_message': status_message,
                }

                return render(request, 'id.html', context)
            elif 'Failed' in validation_result:
                error_data = validation_result['Failed']
                error_message = error_data['ErrorMessage']
                error_code = error_data['ErrorCode']

                context = {
                    'text': extracted_text,
                    'image': image_base64,
                    'aadhaar_number': aadhaar_number,
                    'error_message': error_message,
                    'error_code': error_code
                }
                return render(request, 'id.html', context)

        # Return the extracted text without validation result if Aadhaar number is not found
        context = {'text': extracted_text, 'image': image_base64}
        return render(request, 'id.html', context)

     return render(request, 'id.html')


def validate_aadhaar_number(aadhaar_number):
    url = "https://verifyaadhaarnumber.p.rapidapi.com/Uidverifywebsvcv1/VerifyAadhaarNumber"

    payload = {
        "txn_id": "17c6fa41-778f-49c1-a80a-cfaf7fae2fb8",
        "consent": "Y",
        "uidnumber": aadhaar_number,
        "clientid": "222",
        "method": "uidvalidatev2"
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": "KEY",
        "X-RapidAPI-Host": "verifyaadhaarnumber.p.rapidapi.com"
    }

    response = requests.post(url, data=payload, headers=headers)
    return response.json()


def Invoice_Reader(request):

    if request.method == 'POST' and request.FILES['image']:
        # Get the uploaded image
        image_file = request.FILES['image']
        image_data = image_file.read()
        image = Image.open(io.BytesIO(image_data))

        _, jpeg_data = cv2.imencode('.jpg', cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR))
        image_base64 = base64.b64encode(jpeg_data).decode()

        # Preprocess the image for better OCR accuracy
        image = image.convert('L')  # Convert to grayscale
        image = image.filter(ImageFilter.SHARPEN)  # Sharpen the image
        image = ImageOps.autocontrast(image)  # Increase contrast
        image = ImageOps.invert(image)  # Invert the colors
        image = image.filter(ImageFilter.SMOOTH)  # Remove noise
        threshold = 100  # Binarization threshold
        # Binarize the image
        image = image.point(lambda x: 255 if x > threshold else 0)

        # Use pytesseract to extract text from the image
        text = pytesseract.image_to_string(image, lang='eng', config='--psm 11')

        # Extract specific details from the text
        tel = re.search(r'Tel:\s*([\+\d\-]+)', text)
        invoice_no = re.search(r'Invoice No:\s*([\d]+)', text)
        date = re.search(r'Date\s*([\d\s\w,]+)', text)
        bill_to = re.search(r'Bill to:\s*(.+)', text)
        bank_name = re.search(r'Bank Name:\s*(.+)', text)
        bank_account = re.search(r'Bank Account:\s*(.+)', text)
        contact_email = re.search(r'contact\s*:\s*([\w\.\@]+)', text)
        total_amount = re.search(r'Total\s*([\$\d]+)', text)

        invoice = Invoice(
            tel=tel.group(1) if tel else None,
            invoice_no=invoice_no.group(1) if invoice_no else None,
            date=date.group(1) if date else None,
            bill_to=bill_to.group(1) if bill_to else None,
            bank_name=bank_name.group(1) if bank_name else None,
            bank_account=bank_account.group(1) if bank_account else None,
            contact_email=contact_email.group(1) if contact_email else None,
            total_amount=total_amount.group(1) if total_amount else None,
        )
        invoice.save()  # Save the invoice object to the database

        # Prepare the data for rendering in the template
        context = {
            'tel': tel.group(1) if tel else None,
            'invoice_no': invoice_no.group(1) if invoice_no else None,
            'date': date.group(1) if date else None,
            'bill_to': bill_to.group(1) if bill_to else None,
            'bank_name': bank_name.group(1) if bank_name else None,
            'bank_account': bank_account.group(1) if bank_account else None,
            'contact_email': contact_email.group(1) if contact_email else None,
            'total_amount': total_amount.group(1) if total_amount else None,
            'image': image_base64,
        }

        return render(request, 'Invoice_Reader.html', context)

    return render(request, 'Invoice_Reader.html')

def Handwritten_Text(request):
    if request.method == 'POST' and request.FILES['image']:
        # Get the uploaded image
        image_file = request.FILES['image']
        image_data = image_file.read()
        image = Image.open(io.BytesIO(image_data))

        # Convert image to JPEG and encode as base64 for display purposes
        _, jpeg_data = cv2.imencode('.jpg', cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR))
        image_base64 = base64.b64encode(jpeg_data).decode()


        # Preprocess the image for better OCR accuracy
        image = image.convert('L')  # Convert to grayscale
        image = image.filter(ImageFilter.SHARPEN)  # Sharpen the image
        image = ImageOps.autocontrast(image)  # Increase contrast
        image = ImageOps.invert(image)  # Invert the colors

        # Apply additional image preprocessing techniques (e.g., denoising, adaptive thresholding, etc.)
        image = image.filter(ImageFilter.SMOOTH)  # Remove noise
        image = image.filter(ImageFilter.GaussianBlur(radius=2))  # Gaussian blur for denoising

        threshold = 127  # Binarization threshold
        # Binarize the image
        image = image.point(lambda x: 255 if x > threshold else 0)

        # Use pytesseract to extract text from the image
        text = pytesseract.image_to_string(image, lang='eng', config='--psm 6')
        extracted_text = text.replace('\n', '<br>')

        # Save the extracted text to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(text.encode())
            temp_file_path = temp_file.name

        # Return the extracted text in the response
        context = {'text': extracted_text, 'image': image_base64, 'file_name': os.path.basename(temp_file_path)}
        return render(request, 'Handwritten_Text.html', context)

    return render(request, 'Handwritten_Text.html')


