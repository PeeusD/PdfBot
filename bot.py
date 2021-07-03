import PyPDF2 as pd
import re

pattern = input("Enter string pattern to search: ")
# fileName = input("Enter file path with filename: ")
fileName = "TH.pdf"
object = pd.PdfFileReader(fileName)
numPages = object.getNumPages()
print("Searching...")
delPages = []

for i in range(0, numPages):
    pageObj = object.getPage(i)
    text = pageObj.extractText()
    
    if re.match(pattern, text):
        
        # print(f'Pattern found on Page no: {i}')
        delPages.append(i)


print(f'Pattern found in Page nos.: {delPages}')


infile = pd.PdfFileReader(fileName, 'rb')
output = pd.PdfFileWriter()

for i in range(infile.getNumPages()):
    if i not in delPages:
        p = infile.getPage(i)
        output.addPage(p)

with open(fileName, 'wb') as f:
    output.write(f)
      
    
    
