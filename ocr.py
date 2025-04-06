import easyocr

class OCR:
    def __init__(self, gpu=True):
        self.reader = easyocr.Reader(['en'], gpu=gpu)

    def read_text(self, image):
        text = self.reader.readtext(image, detail=0)
        return text
    
    # def read_percentage(self, image):
    #     text = self.reader.readtext(image, detail=0)
    #     print('percentage text:', text)
    #     if '%' == text[-1]:
    #         text = int(text[:-1])
    #         return text
    #     return None
    

def main():
    pass

if __name__ == "__main__":
    main()