from PyQt4 import QtCore, QtGui
from Generic.Kernel.document     import *
from Generic.Kernel.exception    import *
from Generic.Kernel.Entity.point    import Point
from Generic.Kernel.Command.basecommand import BaseCommand

class testCmdLine(object):
    def __init__(self, dialog, scene):
        self.dialog=dialog
        self.scene=scene
        self._addCustomEvent()
        self._inizializeCommand()
        self.activeCommand=None

    def _inizializeCommand(self):    
        """
            inizialize all the command class
        """
        self.__command={}
        self.__applicationCommand={}
        self.__pyCadApplication=self.scene.getApplication()
        # Application Command
        self.__applicationCommand['Documents']=GetDocuments(self.__pyCadApplication.getDocuments(), self.outputMsg)
        self.__applicationCommand['CreateStyle']=CreateStyle(self.__pyCadApplication.getActiveDocument())
        #self.__applicationCommand['SetActiveDoc']=SetActiveDoc(self.__pyCadApplication)
        self.__applicationCommand['GetActiveDoc']=GetActiveDoc(self.__pyCadApplication, self.outputMsg)
        self.__applicationCommand['GetEnts']=GetEnts(self.__pyCadApplication.getActiveDocument(), self.outputMsg)
        self.__applicationCommand['EntExsist']=EntityExsist(self.__pyCadApplication.getActiveDocument(),self.outputMsg )
        self.__applicationCommand['Delete']=DeleteEntity(self.__pyCadApplication.getActiveDocument(),self.outputMsg )
        self.__applicationCommand['UnDo']=UnDo(self.__pyCadApplication, self.outputMsg)
        self.__applicationCommand['ReDo']=ReDo(self.__pyCadApplication, self.outputMsg)
        self.__applicationCommand['T']=TestKernel(self.__pyCadApplication, self.outputMsg)
        self.__applicationCommand['ET']=EasyTest(self.__pyCadApplication, self.outputMsg)
        # Document Commandf
        for command in self.__pyCadApplication.getCommandList():
            self.__applicationCommand[command]=self.__pyCadApplication.getCommand(command)
        self.__applicationCommand['?']=PrintHelp(self.__applicationCommand, self.outputMsg)    
        
    def _addCustomEvent(self):
        """
            add custom event at the user interface
        """
        QtCore.QObject.connect(self.dialog.ImputCmd, QtCore.SIGNAL("returnPressed()"),self.imputCommand)
        #QtCore.QObject.connect(self.dialog.uiTextEditor, QtCore.SIGNAL("textChanged()"),self.imputCommand)
        #QtCore.QObject.connect(self.uiTextEditor, QtCore.SIGNAL("textChanged()"), self.uiTextEditor.update)
        
    def imputCommand(self):
        """
            imput dialog
        """
        text=self.dialog.ImputCmd.text()
        if self.activeCommand:
            try:
                if not self.performCommand(self.activeCommand, text):
                    self.activeCommand=None
                    #self.scene.populateScene(self.__pyCadApplication.getActiveDocument())
                else:
                    self.outputMsg(self.activeCommand.getActiveMessage())
            except:
                self.outputMsg("Unable to perfor the command")
                self.activeCommand=None
        else:
            cmdObject=None
            if text in self.__applicationCommand:
                cmdObject=self.__applicationCommand[text]
                cmdObject.reset()
                self.outputMsg(cmdObject.getActiveMessage())
            else:
                self.outputMsg('Command not avaiable write ? for command list')
            self.activeCommand=cmdObject
        self.dialog.ImputCmd.setText("")
    
    def performCommand(self,cObject, text):
        """
            Perform a Command
            cObject is the command object
        """
        try:
            iv=cObject.next()
            exception,message=iv
            try:
                raise exception(None)
            except ExcPoint:
                cObject[iv]=self.convertToPoint(text)  
                return cObject
            except (ExcLenght, ExcAngle, ExcInt):
                cObject[iv]=self.convertToFloat(text)
                return cObject
            except (ExcBool):
                cObject[iv]=self.convertToBool(text)
                return cObject
            except (ExcText):
                cObject[iv]=text
                return cObject
            except (ExEntity):
                cObject[iv]=self.convertToInt(text)
                return cObject
            except:
                msg="Error on command imput"
                self.outputMsg(msg)
                raise CommandImputError, msg
            
        except (StopIteration):
            cObject.applyCommand()
            return None
        except PyCadWrongCommand:
            self.outputMsg("Wrong Command")
    
    def convertToBool(self, msg):   
        """
            return an int from user
        """        
        if msg=="Yes":
            return True
        else:
            return False

    def convertToInt(self, msg):   
        """
            return an int from user
        """        
        if msg:
            return int(msg)
        return None
        
    def convertToFloat(self, msg):
        """
            return a float number
        """
        if msg:
            return float(msg)
        return None
        
    def convertToPoint(self, msg):
        """
            ask at the user to imput a point 
        """
        if msg:
            coords=msg.split(',')
            x=float(coords[0])
            y=float(coords[1])
            return Point(x, y)
        return None

            
    def outputMsg(self, msg):   
        """
            print a message in to the self.dialog.uiTextEditor 
        """ 
        #self.dialog.uiTextEditor.moveCursor(QtGui.QTextCursor.Down)
        msg=u"\r<PythonCAD> : "+msg
        self.dialog.uiTextEditor.insertPlainText(msg)

def printEntity(ents, msgFucntion):
        """
            print a query result
        """
        i=0
        for e in ents:
            msgFucntion("Entity Type %s id %s "%(str(e.eType),str(e.getId())))
            if i > 100:
                msgFucntion("There are more then 100 entitys in the select so i stop printing")
                break
            i+=1
            
class GetEnts(BaseCommand):
    def __init__(self, document, msgFucntion):
        BaseCommand.__init__(self, document)
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.outputMsg=msgFucntion
        self.exception=[ExcText]
        self.message=["Give Me the Document Type Enter for All"]
    def applyCommand(self):
        if len(self.value)!=1:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        docName=self.value[0]
        startTime=time.clock()
        if not docName:
            docName="ALL"
        ents=self.document.getEntityFromType(docName)
        endTime=time.clock()-startTime       
        printEntity(ents,self.outputMsg )
        self.outputMsg("Exec query get %s ent in %s s"%(str(len(ents)), str(endTime)))
        self.outputMsg("********************************")


class UnDo(BaseCommand):
    def __init__(self, application, msgFunction):
        BaseCommand.__init__(self, None)
        self.__application=application
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[]
        self.message=["Press enter to perform the Undo command"]
        self.outputMsg=msgFunction
    def applyCommand(self):
        if len(self.value)!=0:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        doc=self.__application.getActiveDocument()
        doc.unDo()

class ReDo(BaseCommand):
    def __init__(self, application, msgFunction):
        BaseCommand.__init__(self, None)
        self.__application=application
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[]
        self.message=["Press enter to perform the ReDo command"]
        self.outputMsg=msgFunction
    def applyCommand(self):
        if len(self.value)!=0:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        doc=self.__application.getActiveDocument()
        doc.reDo()

class GetActiveDoc(BaseCommand):
    def __init__(self, application, msgFunction):
        BaseCommand.__init__(self, None)
        self.__application=application
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[]
        self.message=["Press enter to perform the command"]
        self.outputMsg=msgFunction
    def applyCommand(self):
        if len(self.value)!=0:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        docName=self.value[0]
        self.__application.setActiveDocument(docName)
        doc=self.__application.getActiveDocument()
        self.outputMsg("Active Document is %s"%str(doc.dbPath))
        
class SetActiveDoc(BaseCommand):
    def __init__(self, application):
        BaseCommand.__init__(self, None)
        self.__application=application
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[ExcText]
        self.message=["Give Me the Document Name"]
    def applyCommand(self):
        if len(self.value)!=1:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        docName=self.value[0]
        self.__application.setActiveDocument(docName)
        
class GetDocuments(BaseCommand):
    def __init__(self, documents, msgFunction):
        BaseCommand.__init__(self, None)
        self.__docuemnts=documents
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[]
        self.message=["Press enter to perform the command"]
        self.outputMsg=msgFunction
    def applyCommand(self):
        if len(self.value)!=0:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        self.showDocuments()
        
    def showDocuments(self):
        """
            show The list of documents
        """
        try:
            self.outputMsg("Documents in the curret application")
            i=0
            for key in self.__docuemnts:
                self.outputMsg("%s File %s"%(str(i), str(key)))
                i+=1
            self.outputMsg("***********************************")
        except:
            self.outputMsg("Unable To Perform the GetDocuments") 
            
class CreateStyle(BaseCommand):
    def __init__(self, document):
        BaseCommand.__init__(self, document)
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[ExcText]
        self.message=["Give Me the Style Name"]
    def applyCommand(self):
        if len(self.value)!=1:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        styleName=self.value[0]
        #self.inputMsg("Write style name")
        stl=Style(styleName)
        self.document.saveEntity(stl)
        
class EntityExsist(BaseCommand):
    def __init__(self, document, msgFunction ):
        BaseCommand.__init__(self, document)
        self.outputMsg=msgFunction
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[ExcText]
        self.message=["Give me the entity id"]
    def applyCommand(self):
        if len(self.value)!=1:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        entId=self.value[0]
        #self.inputMsg("Write style name")
        if self.document.entityExsist(entId):
            self.outputMsg("Entity Found in the db")
        else:
            self.outputMsg("Entity Not Found")
            
class DeleteEntity(BaseCommand):
    def __init__(self, document, msgFunction ):
        BaseCommand.__init__(self, document)
        self.outputMsg=msgFunction
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[ExcText]
        self.message=["Give me the entity id"]
    def applyCommand(self):
        if len(self.value)!=1:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        entId=self.value[0]
        #self.inputMsg("Write style name")
        if self.document.entityExsist(entId):
            self.document.deleteEntity(entId)

class PrintHelp(BaseCommand):
    def __init__(self, commandArray, msgFunction):
        BaseCommand.__init__(self, None)
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[]
        self.outputMsg=msgFunction
        self.message=["Print the help Press enter to ally the command "]
        self.commandNames=commandArray.keys()

    def next(self):    
        raise StopIteration

    def applyCommand(self):
        self.outputMsg("***********Command List******************")
        for s in   self.commandNames:
            self.outputMsg(s)
            
class TestKernel(BaseCommand):
    def __init__(self, application, msgFunction):
        BaseCommand.__init__(self, None)
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[]
        self.outputMsg=msgFunction
        self.message=["Press enter to start the test"]
        self.__pyCadApplication=application

    def next(self):    
        raise StopIteration

    def applyCommand(self):
        self.outputMsg("*********** Start Test ******************")
        self.featureTest()
        self.outputMsg("*********** End   Test ******************")
            
    def featureTest(self):
            """
                this function make a basic test
            """
            self.outputMsg("Create a new document 1")
            doc1=self.__pyCadApplication.newDocument()
            self.outputMsg("Create a new document 2")
            doc2=self.__pyCadApplication.newDocument()
            self.outputMsg("Set Current p1")
            self.__pyCadApplication.setActiveDocument(doc1)
            self.outputMsg("Create Point")
            self.performCommandRandomly("POINT")
            self.outputMsg("Create Segment")
            self.performCommandRandomly("SEGMENT")
            self.outputMsg("Create Arc")
            self.performCommandRandomly("ARC")
            self.__pyCadApplication.setActiveDocument(doc2)
            self.outputMsg("Create Ellipse")
            self.performCommandRandomly("ELLIPSE")
            self.outputMsg("Create Polyline")
            self.performCommandRandomly("POLYLINE")
            self.outputMsg("Create ACLine")
            self.performCommandRandomly("ACLINE")
            
            self.outputMsg("Get Entitys for doc 1")
            self.__pyCadApplication.setActiveDocument(doc1)
            activeDoc=self.__pyCadApplication.getActiveDocument()
            ents=activeDoc.getEntityFromType("ALL")
            self.printEntity(ents)
            self.outputMsg("Get Entitys for doc 2")
            self.__pyCadApplication.setActiveDocument(doc2)
            activeDoc=self.__pyCadApplication.getActiveDocument()
            ents=activeDoc.getEntityFromType("ALL")
            self.printEntity(ents)
            # Working with styles
            self.outputMsg("Create NewStyle")
            stl=Style("NewStyle")
            self.outputMsg("Save in document")
            activeDoc.saveEntity(stl)
            activeDoc.setActiveStyle(name='NewStyle')
            self.outputMsg("Create Segment")
            self.performCommandRandomly("SEGMENT")
            self.outputMsg("Create Arc")
            self.performCommandRandomly("ARC")
            
            self.outputMsg("Create NewStyle1")
            stl1=Style("NewStyle1")
            self.__pyCadApplication.setApplicationStyle(stl1)
            stl11=self.__pyCadApplication.getApplicationStyle(name='NewStyle1')
            styleDic=stl11.getConstructionElements()
            styleDic[styleDic.keys()[0]].setStyleProp('entity_color',(255,215,000))
            self.__pyCadApplication.setApplicationStyle(stl11)
            activeDoc.saveEntity(stl11)
            self.outputMsg("Create Segment")
            self.performCommandRandomly("SEGMENT")
            self.outputMsg("Create Arc")
            self.performCommandRandomly("ARC")
            
            self.outputMsg("Create NewStyle2 ")
            stl1=Style("NewStyle2")
            stl12=activeDoc.saveEntity(stl1)
            styleDic=stl11.getConstructionElements()
            styleDic[styleDic.keys()[0]].setStyleProp('entity_color',(255,215,000))
            self.outputMsg("Update NewStyle2")
            activeDoc.saveEntity(stl12)
            self.outputMsg("Done")
            # Test  Geometrical chamfer ent
            self.GeotestChamfer()
            # Test Chamfer Command 
            self.testChamferCommand()
            
    def testGeoChamfer(self):    
        self.outputMsg("Test Chamfer")
        p1=Point(0.0, 0.0)
        p2=Point(10.0, 0.0)
        p3=Point(0.0, 10.0)
        s1=Segment(p1, p2)
        s2=Segment(p1, p3)
        cmf=Chamfer(s1, s2, 2.0, 2.0)
        cl=cmf.getLength()
        self.outputMsg("Chamfer Lengh %s"%str(cl))
        s1, s2, s3=cmf.getReletedComponent()
        if s3:
            for p in s3.getEndpoints():
                x, y=p.getCoords()
                self.outputMsg("P1 Cords %s,%s"%(str(x), str(y)))
        else:
            self.outputMsg("Chamfer segment in None")

    def testChamferCommand(self):
        """
            this function is usefoul for short test
            as soon it works copy the code into featureTest
        """
        newDoc=self.__pyCadApplication.newDocument()
        intPoint=Point(0.0, 0.0)
        
        s1=Segment(intPoint, Point(10.0, 0.0))
        s2=Segment(intPoint, Point(0.0, 10.0))
        
        ent1=newDoc.saveEntity(s1)
        ent2=newDoc.saveEntity(s2)
       
        cObject=self.__pyCadApplication.getCommand("CHAMFER")
        keys=cObject.keys()
        cObject[keys[0]]=ent1
        cObject[keys[1]]=ent2
        cObject[keys[2]]=2
        cObject[keys[3]]=2
        cObject[keys[4]]=None
        cObject[keys[5]]=None
        cObject.applyCommand()

    def getRandomPoint(self):
        """
            get e random point
        """
        x=random()*1000
        y=random()*1000
        return Point(x, y)

    def performCommandRandomly(self, commandName, andLoop=10):
        """
            set some random Value at the command imput
        """
        self.outputMsg("Start Command %s"%str(commandName))
        i=0
        cObject=self.__pyCadApplication.getCommand(commandName)
        for iv in cObject:
            exception,message=iv
            try:
                raise exception(None)
            except ExcPoint:
                self.outputMsg("Add Point")
                if i>=andLoop:
                    cObject[iv]=None
                else:
                    cObject[iv]=self.getRandomPoint()
            except (ExcLenght, ExcAngle):
                self.outputMsg("Add Lengh/Angle")
                cObject[iv]=100
            except:
                self.outputMsg("Bad error !!")
                raise 
            i+=1
        else:
            self.outputMsg("Apply Command")
            cObject.applyCommand()
            
class EasyTest(BaseCommand):
    def __init__(self, application, msgFunction):
        BaseCommand.__init__(self, None)
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[]
        self.outputMsg=msgFunction
        self.message=["Press enter to start the test"]
        self.__pyCadApplication=application

    def next(self):    
        raise StopIteration

    def applyCommand(self):
        self.outputMsg("*********** Start Test ******************")
        self.easyTest()
        self.outputMsg("*********** End   Test ******************")    
    
    def easyTest(self):
        """
            this function is usefoul for short test
            as soon it works copy the code into featureTest
        """
        newDoc=self.__pyCadApplication.getActiveDocument()
        intPoint=Point(2.0, 2.0)
        args={"SEGMENT_0":intPoint, "SEGMENT_1":Point(10.0, 0.0)}
        s1=Segment(args)
        args={"SEGMENT_0":intPoint, "SEGMENT_1":Point(0.0, 10.0)}
        s2=Segment(args)
        
        ent1=newDoc.saveEntity(s1)
        ent2=newDoc.saveEntity(s2)
       
        cObject=self.__pyCadApplication.getCommand("CHAMFER")
        keys=cObject.keys()
        cObject[keys[0]]=ent1
        cObject[keys[1]]=ent2
        cObject[keys[2]]=2
        cObject[keys[3]]=2
        cObject[keys[4]]=None
        cObject[keys[5]]=None
        cObject.applyCommand()