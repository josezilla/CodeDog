#/////////////////  Use this pattern to write to_string() or drawData() to display each member of the model for a struct.

import progSpec
import codeDogParser
from progSpec import cdlog, cdErr

import pattern_GenSymbols

classesToProcess=[]
classesEncoded={}

class structProcessor:

    def addGlobalCode(self, classes):
        pass

    def resetVars(self, modelRef):
        pass

    def processField(self, fieldName, field, fldCat):
        pass

    def addOrAmendClasses(self, classes, className, modelRef):
        pass

    def processStruct(self, classes, className):
        global classesEncoded
        classesEncoded[className]=1
        self.currentClassName = className
        modelRef = progSpec.findSpecOf(classes[0], className, 'model')
        self.resetVars(modelRef)
        self.currentModelSpec = modelRef
        if modelRef==None:
            cdErr('To write a processing function for class "'+className+'" a model is needed but is not found.')
        ### Write code for each field
        for field in modelRef['fields']:
            fldCat=progSpec.fieldsTypeCategory(field['typeSpec'])
            fieldName=field['fieldName']
            self.processField(fieldName, field, fldCat)
        self.addOrAmendClasses(classes, className, modelRef)

#---------------------------------------------------------------  WRITE: .asProteus()
class structAsProteusWriter(structProcessor):

    asProteusGlobalsWritten=False

    def addGlobalCode(self, classes):
        if structAsProteusWriter.asProteusGlobalsWritten: return
        else: structAsProteusWriter.asProteusGlobalsWritten=True
        pass

    def resetVars(self, modelRef):
        self.textFuncBody=''

    def toProteusTextFieldAction(self, label, fieldName, field, fldCat):
        global classesToProcess
        global classesEncoded
        valStr=''
        if(fldCat=='int' or fldCat=='double'):
            valStr='toString('+fieldName+')'
        elif(fldCat=='string' or fldCat=='char'):
            valStr= fieldName
        elif(fldCat=='flag' or fldCat=='bool'):
            valStr='dispBool(('+fieldName+')!=0)'
        elif(fldCat=='mode'):
            valStr='toString('+fieldName+')'  #fieldName+'Strings['+fieldName+'] '
        elif(fldCat=='struct'):
            valStr=fieldName+'.to_string(indent+"|   ")\n'

            structTypeName=progSpec.getFieldType(field['typeSpec'])[0]
            if not(structTypeName in classesEncoded):
                #print "TO ENDODE:", structTypeName
                classesEncoded[structTypeName]=1
                classesToProcess.append(structTypeName)
        if(fldCat=='struct'):
            S='S <- S + indent + dispFieldAsText("'+label+'", 15) + "\\n"\n    '+valStr+' + "\\n"\n'
        else:
            S='S <- S + indent + dispFieldAsText("'+label+'", 15) + '+valStr+' + "\\n"\n'
        return S

    def processField(self, fieldName, field, fldCat):
        S=""
        if fldCat=='func': return ''
        typeSpec=field['typeSpec']
        if progSpec.isAContainer(typeSpec):
            innerFieldType=progSpec.getFieldType(typeSpec)
            #print "ARRAYSPEC:",innerFieldType, field
            fldCatInner=progSpec.innerTypeCategory(innerFieldType)
            calcdName=fieldName+'["+toString(_item_key)+"]'
            S+="    withEach _item in "+fieldName+"{\n"
            S+="        "+self.toProteusTextFieldAction(calcdName, '_item', field, fldCatInner)+"    }\n"
        else: S+="        "+self.toProteusTextFieldAction(fieldName, fieldName, field, fldCat)
        if progSpec.typeIsPointer(typeSpec):
            T ="    if("+fieldName+' == NULL){S <- S + '+'indent, dispFieldAsText("'+fieldName+'", 15)+"NULL\\n")}\n'
            T+="    else{\n    "+S+"    }\n"
            S=T
        self.textFuncBody += S

    def addOrAmendClasses(self, classes, className, modelRef):
        self.textFuncBody = '        me string: S <- "{\\n"\n' + '        indent <- indent + "    "\n' +self.textFuncBody + '        S <- S + "}\\n"\n'
        Code='    me string: asProteus(me string:indent <- "") <- {\n'+self.textFuncBody+"        return(S)\n    }"
        Code=progSpec.wrapFieldListInObjectDef(className, Code)
        codeDogParser.AddToObjectFromText(classes[0], classes[1], Code, className+'.asProteus()')

#---------------------------------------------------------------  WRITE: .toString()

class structToStringWriter(structProcessor):

    toStringGlobalsWritten=False

    def addGlobalCode(self, classes):
        if structToStringWriter.toStringGlobalsWritten: return
        else: structToStringWriter.toStringGlobalsWritten=True
        pass

    def resetVars(self, modelRef):
        self.textFuncBody=''

    def displayTextFieldAction(self, label, fieldName, field, fldCat):
        global classesToProcess
        global classesEncoded
        valStr=''
        if(fldCat=='int' or fldCat=='double'):
            valStr='toString('+fieldName+')'
        elif(fldCat=='string' or fldCat=='char'):
            valStr= ' '+fieldName+' '
        elif(fldCat=='flag' or fldCat=='bool'):
            valStr='dispBool(('+fieldName+')!=0)'
        elif(fldCat=='mode'):
            valStr=fieldName+'Strings['+fieldName+'] ' #'toString('+fieldName+')'  #fieldName+'Strings['+fieldName+'] '
        elif(fldCat=='struct'):
            valStr=fieldName+'.to_string(indent+"|   ")\n'

            structTypeName=progSpec.getFieldType(field['typeSpec'])[0]
            if not(structTypeName in classesEncoded):
                classesToProcess.append(structTypeName)
        if(fldCat=='struct'):
            S="    "+'SRet_ <- SRet_ + indent + dispFieldAsText("'+label+'", 15) + "\\n"\n    SRet_ <- SRet_ + '+valStr+'+ "\\n"\n'
        else:
            ender=''
            starter=''
            if(fldCat=='flag' or fldCat=='bool'):
                starter = 'if('+fieldName+'){'
                ender = '}'
            elif(fldCat=='int' or fldCat=='double'):
                starter = 'if('+fieldName+'!=0){'
                ender = '}'
            S="    "+starter+'SRet_ <- SRet_ + indent + dispFieldAsText("'+label+'", 15) + '+valStr+' + "\\n"\n'+ender
        return S

    def processField(self, fieldName, field, fldCat):
        S=""
        if fldCat=='func': return ''
        typeSpec=field['typeSpec']
        if progSpec.isAContainer(typeSpec):
            innerFieldType=progSpec.getFieldType(typeSpec)
            #print "ARRAYSPEC:",innerFieldType, field
            fldCatInner=progSpec.innerTypeCategory(innerFieldType)
            calcdName=fieldName+'["+toString(_item_key)+"]'
            S+="    withEach _item in "+fieldName+"{\n"
            S+="        "+self.displayTextFieldAction(calcdName, '_item', field, fldCatInner)+"    }\n"
        else: S+=self.displayTextFieldAction(fieldName, fieldName, field, fldCat)
        if progSpec.typeIsPointer(typeSpec):
            T ="    if("+fieldName+' == NULL){SRet_ <- SRet_ + '+'indent + dispFieldAsText("'+fieldName+'", 15)+"NULL\\n"}\n'
            T+="    else{\n    "+S+"    }\n"
            S=T
        self.textFuncBody += S

    def addOrAmendClasses(self, classes, className, modelRef):
        Code='me string: to_string(me string:indent) <- {\n    me string: SRet_ <- ""\n'+self.textFuncBody+"        return(SRet_)\n    }\n"
        Code=progSpec.wrapFieldListInObjectDef(className, Code)
        codeDogParser.AddToObjectFromText(classes[0], classes[1], Code, className+'.toString()')

#---------------------------------------------------------------  WRITE CODE TO DRAW STRUCTS

class structDrawingWriter(structProcessor):

    structDrawGlobalsWritten=False

    def addGlobalCode(self, classes):
        if structDrawingWriter.structDrawGlobalsWritten: return
        else: structDrawingWriter.structDrawGlobalsWritten=True
        CODE='''
struct GLOBAL{
    const int: fontSize <- 10

    me bool: isNull(me string: value) <- {
        if(value=="0" or value=="''" or value=="Size:0" or value=="NULL" or value=="false"){return(true)}
        else{return(false)}
    }
}
    '''
        codeDogParser.AddToObjectFromText(classes[0], classes[1], CODE, 'Global functions to draw structs')

    def resetVars(self, modelRef):
        [self.structTextAcc, self.updateFuncTextAcc, self.drawFuncTextAcc, self.setPosFuncTextAcc, self.handleClicksFuncTextAcc, self.handleClicksFuncTxtAcc2] = ['', '', '', '', '', '']
        self.updateFuncTextPart2Acc=''; self.drawFuncTextPart2Acc=''

    def processField(self, fieldName, field, fldCat):
        [structText, updateFuncText, drawFuncText, setPosFuncText, handleClicksFuncText] = self.getDashDeclAndUpdateCode(
            'me', '"'+fieldName+'"', 'data.'+fieldName, fieldName, field, 'skipNone', '    ')
        self.structTextAcc     += structText
        self.updateFuncTextAcc += updateFuncText
        self.drawFuncTextAcc   += drawFuncText
        self.setPosFuncTextAcc += setPosFuncText
        self.handleClicksFuncTextAcc += handleClicksFuncText

    def addOrAmendClasses(self, classes, className, modelRef):
        self.setPosFuncTextAcc += '\n        y <- y+5'+'\n        height <- y-posY'+'\n        me int:depX <- posX+width+40\n'
        countOfRefs=0
        for field in modelRef['fields']:
            typeSpec=field['typeSpec']
            typeName=progSpec.getFieldType(field['typeSpec'])[0]
            fldCat=progSpec.fieldsTypeCategory(typeSpec)
            if fldCat=='func': continue
   #         if typeName=='DblLinkedListNode': continue
            if progSpec.typeIsPointer(typeSpec):  # Draw dereferenced POINTER
                fieldName=field['fieldName']
                dispStructTypeName = "display_"+typeName
                declSymbolStr='    '
                if(countOfRefs==0):declSymbolStr+='me string: '
                countOfRefs+=1
                [structText, updateFuncText, drawFuncText, setPosFuncText, handleClicksFuncText] = self.getDashDeclAndUpdateCode(
                    'their', '"'+fieldName+'"', 'data.'+fieldName, fieldName, field, 'skipPtr', '    ')
                self.structTextAcc += structText
                tempFuncText = updateFuncText
                updateFuncText = declSymbolStr+'mySymbol <- data.'+fieldName+'.mySymbol(data.'+fieldName+')\n'
                updateFuncText += ( '    if(data.'+fieldName+' != NULL){\n'+
                                    '        '+fieldName+' <- asClass('+dispStructTypeName+', dependentIsRegistered(mySymbol))\n'
                                    '        if(!'+fieldName+'){'
                                    '\n            Allocate('+fieldName+')'+
                                    '\n            '+fieldName+'.dashParent <- self'+
                                    '\n            addDependent(mySymbol, '+fieldName+')'+
                                    '\n'+tempFuncText+
                                    '\n        }\n    } else {'+fieldName+' <- NULL}\n')
                self.updateFuncTextPart2Acc += updateFuncText
                self.setPosFuncTextAcc      += '''
    if(<fieldName> != NULL and !<fieldName>Ptr.refHidden){
        if(!<fieldName>.posIsSet){
            <fieldName>.setPos(depX, extC, extC)
            extC <- <fieldName>.extY + 40
            extX <- max(extX, <fieldName>.extX)
            extY <- max(extY, <fieldName>.extY)
        }
        addRelation("arrow", <fieldName>Ptr, <fieldName>)
    }
'''.replace('<fieldName>', fieldName)
                self.handleClicksFuncTxtAcc2+= '    if('+fieldName+' != NULL and !'+fieldName+'Ptr.refHidden){\n'+fieldName+'.isHidden<-false\n    }\n'

        Code='''
struct display_'''+className+": inherits=dash"+'''{
    me bool: isChanged
    me dataField: header
    me mode[headerOnly, fullDisplay, noZeros]: displayMode
    their '''+className+''': data
'''+self.structTextAcc+'''

    void: update(me string: _label, me string: textValue, their '''+className+''': _Data) <- {
        isChanged <- !(data === _Data)
        data <- _Data
        if(data==NULL){
            header.update(100, 180, _label, "NULL", false)
            return()
        }
        header.update(100, 180, _label, textValue, false)
        if(isChanged){displayMode<-headerOnly}
'''+self.updateFuncTextAcc+'''

'''+self.updateFuncTextPart2Acc+'''
    }

    void: setPos(me int:x, me int:y, me int: extCursor) <- {
        posIsSet <- true
        posX <- x;
        posY <- y;
        extC <- extCursor
        isHidden<-false
        header.setPos(x,y,extC)
        y <- y+header.height
        width <- header.width
        height <- y-posY
        extX <- header.extX
        extY <- max(y, extC)
        if(displayMode!=headerOnly){
            x <- x+10    /- Indent fields in a struct
'''+self.setPosFuncTextAcc+'''
            width <- width+10
        }
    }


    me bool: primaryClick(their GUI_ButtonEvent: event) <- {
        if(isHidden){return(false)}
        me GUI_scalar: eventX <- event.x
        me GUI_scalar: eventY <- event.y
        if( header.isTouchingMe(eventX, eventY)){
            if(displayMode==headerOnly){displayMode <- noZeros}
            else if(displayMode==noZeros){displayMode <- fullDisplay}
            else if(displayMode==fullDisplay){displayMode <- headerOnly}
        } else {
'''+self.handleClicksFuncTextAcc+'''
        }

'''+self.handleClicksFuncTxtAcc2+'''

        return(true)
    }

    void: draw(me GUI_ctxt: cr) <- {
        header.isHidden <- false
        me cdColor: hedrColor <- styler.frGndColor
        cr.setColor(hedrColor)
        header.draw(cr)
        cr.strokeNow()
        hedrColor <- styler.frGndColor
        cr.setColor(hedrColor)
        if(displayMode!=headerOnly){
'''+self.drawFuncTextAcc+'''
            me cdColor: rectColor <- styler.frGndColor
            cr.setColor(rectColor)
            cr.rectangle(posX, posY, width, height)
            cr.strokeNow()
            rectColor <- styler.frGndColor
            cr.setColor(rectColor)
'''+self.drawFuncTextPart2Acc+'''
        }
    }
}\n'''
        #if className == 'pureInfon': print Code
        codeDogParser.AddToObjectFromText(classes[0], classes[1], Code, 'display_'+className)

    def getDashDeclAndUpdateCode(self, owner, fieldLabel, fieldRef, fieldName, field, skipFlags, indent):
        global classesToProcess
        global classesEncoded
        [structText, updateFuncText, setPosFuncText, drawFuncText, handleClicksFuncText]=['', '', '', '', '']
        typeSpec=field['typeSpec']
        fldCat=progSpec.fieldsTypeCategory(typeSpec)
        if fldCat=='func': return ['', '', '', '', '']
        if progSpec.typeIsPointer(typeSpec) and skipFlags != 'skipPtr':  # Header for a POINTER
            fieldName+='Ptr'
            if fieldRef=='data.itmItr': innerUpdateFuncStr = '"ItmItr"' # TODO: unhard code this reference to itmItr
            else: innerUpdateFuncStr = fieldRef+'.mySymbol('+fieldRef+')'
            updateFuncText+="        "+fieldName+'.dashParent <- self\n'
            updateFuncText+="        "+fieldName+'.update('+fieldLabel+', '+innerUpdateFuncStr+', isNull('+innerUpdateFuncStr+'))\n'
            structText += "    "+owner+" ptrToItem: "+fieldName+"\n"

        elif progSpec.isAContainer(typeSpec) and skipFlags != 'skipLists': # Header and items for LIST
            dispStructTypeName= "display_"+progSpec.getFieldType(field['typeSpec'])[0]
            innerUpdateFuncStr = '"Size:"+toString(data.'+fieldName+'.size())'
            updateFuncText+="        "+fieldName+'.dashParent <- self\n'
            updateFuncText+="        "+ "our dash[our list]: oldElements <- "+fieldName+".elements\n"
            updateFuncText+="        "+fieldName+'.update('+fieldLabel+', '+innerUpdateFuncStr+', isNull('+innerUpdateFuncStr+'), true)\n'
             ## Now push each item
            innerFieldType = progSpec.getFieldType(typeSpec)
            #print "ARRAYSPEC:",innerFieldType, field
            fldCatInner=progSpec.innerTypeCategory(innerFieldType)
            if fieldRef=='data.itmItr' or fieldRef=='data.items': newFieldRef='_item' # TODO: unhard code this reference to itmItr
            else: newFieldRef='data.'+fieldName+'[_item_key]'
            newFieldLabel='"["+toString(_item_key)+"]  "+ _item.mySymbol(_item)'
            updateFuncText+="\n        "+"me int64: dash_key <- 0"
            updateFuncText+="\n        withEach _item in data."+fieldName+"{\n"
            [innerStructText, innerUpdateFuncText, innerDrawFuncText, innerSetPosFuncText, innerHandleClicksFuncText] = self.getDashDeclAndUpdateCode('our', newFieldLabel, newFieldRef, 'newItem', field, 'skipLists', '        ')
            updateFuncText+="            "+innerStructText
            updateFuncText+="            "+"if(oldElements==NULL or (oldElements!=NULL and !(asClass("+dispStructTypeName+", oldElements[dash_key]).data === _item))){\n"
            updateFuncText+='                Allocate(newItem)\n'
            updateFuncText+='                newItem.dashParent <- self\n'
            updateFuncText+='               '+'addDependent(_item.mySymbol(_item), newItem)'
            updateFuncText+='\n            } else {\n               newItem <- asClass('+dispStructTypeName+', oldElements[dash_key])\n            dash_key <- dash_key + 1'
            updateFuncText+='\n            }'
            updateFuncText+='\n            '+innerUpdateFuncText
            updateFuncText+='            '+fieldName+'.updatePush(newItem)'
            updateFuncText+='\n        }\n'
            structText += "    "+owner+" listOfItems: "+fieldName+"\n"
        elif(fldCat=='struct'):  # Header for a STRUCT
            updateFuncText+="        "+fieldName+'.dashParent <- self\n'
            updateFuncText+="        "+fieldName+'.update('+fieldLabel+', ">", '+fieldRef+')\n'
            if 'fieldType' in typeSpec and not(isinstance(typeSpec['fieldType'], basestring)) and typeSpec['fieldType'][0]=='DblLinkedList':structTypeName = 'infon'
            else: structTypeName = progSpec.getFieldType(typeSpec)[0]
            structText += "    "+owner+" display_"+structTypeName+': '+fieldName+"\n"


            # Add new classname to a list so it can be encoded.
            if not(structTypeName in classesToProcess):
                classesToProcess.append(structTypeName)

        else:   # Display field for a BASIC TYPES
            valStr=''
            if(fldCat=='int' or fldCat=='double'):
                valStr='toString(data.'+fieldName+')'
            elif(fldCat=='string' or fldCat=='char'):
                valStr= '"\'"+'+'data.'+fieldName+'+"\'"'
            elif(fldCat=='flag' or fldCat=='bool'):
                valStr='dispBool((data.'+fieldName+')!=0)'
            elif(fldCat=='mode'):
                valStr= fieldRef+'Strings[data.'+fieldName+'] '

            updateFuncText="        "+fieldName+'.update(100, 180, '+fieldLabel+', '+valStr+', isNull('+valStr+'))\n'
            structText += "    "+owner+" dataField: "+fieldName+"\n"

        drawFuncText  ="        "+fieldName+'.draw(cr)\n'
        setPosFuncText += '''        if(!<fieldName>.isNullLike or displayMode==fullDisplay){
                <fieldName>.setPos(x,y,extC)
                extC <- <fieldName>.extC
                y <- y + <fieldName>.height
                extX <- max(extX, <fieldName>.extX)
                extY <- max(extY, <fieldName>.extY)
                width<- max(width, <fieldName>.width)
                <fieldName>.isHidden<-false
            } else {<fieldName>.isHidden<-true}
    '''.replace('<fieldName>', fieldName)
      #  updateFuncText+='        if(crntWidth<'+fieldName+'.width){crntWidth <- '+fieldName+'.width}'
        handleClicksFuncText = '            '+fieldName+'.primaryClick(event)'
        return [structText, updateFuncText, drawFuncText, setPosFuncText, handleClicksFuncText]

#---------------------------------------------------------------------  MAIN APPLY CODE

def apply(classes, tags, className, dispMode):
    if dispMode[:4]=='TAG_':
        dispModeTagName=dispMode[4:]
        dispMode=progSpec.fetchTagValue(tags, dispModeTagName)
    if(dispMode!='none' and dispMode!='text' and dispMode!='draw' and dispMode!='Proteus' and dispMode!='toGUI'):
        cdErr('Invalid parameter for display mode in Code Data Display pattern: '+str(dispMode))
    if dispMode=='none': return

    global classesToProcess
    classesToProcess=[className]
    global classesEncoded
    #classesEncoded={}

    if(dispMode=='Proteus'):   processor = structAsProteusWriter()
    elif(dispMode=='text'):    processor = structToStringWriter()
    elif(dispMode=='draw'):    processor = structDrawingWriter()
    processor.addGlobalCode(classes)

    for classToEncode in classesToProcess:
        if (classToEncode in classesEncoded): continue
        cdlog(1, "  ENCODING "+dispMode+": "+ classToEncode)
        classesEncoded[classToEncode]=1
        pattern_GenSymbols.apply(classes, {}, [classToEncode])      # Invoke the GenSymbols pattern
        processor.processStruct(classes, classToEncode)
    return
