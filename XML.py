import xml.etree.ElementTree as xml
import time

class XML:

    fileName:str

    def __init__(self, fileName):
        self.fileName = fileName + ".xml"
        self.openFile()

    def openFile(self):
        try:
            file = open(self.fileName, "r")
        except FileNotFoundError:
            self.createFile()

    def createFile(self):
        rootXML = xml.Element("settings")

        text = xml.Element("text")
        text.text = "Text"
        rootXML.append(text)

        file = open(self.fileName, "w")
        file.write(xml.tostring(rootXML, encoding="utf-8", method="xml").decode(encoding="utf-8"))
        file.close()

    def editFile(self, element, attribute):
        tree = xml.ElementTree(file=self.fileName)
        rootXML = tree.getroot()
        for elem in rootXML.iter(element):
            elem.text = str(attribute)

        tree = xml.ElementTree(rootXML)
        tree.write(self.fileName)

    def parsingFile(self, elements, text = True):
        tree = xml.ElementTree(file=self.fileName)
        rootXML = tree.getroot()
        for element in rootXML.iter(elements):
            if (text):
                return element.text
            return element