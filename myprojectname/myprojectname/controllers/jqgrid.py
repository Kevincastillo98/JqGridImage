# -*- coding: utf-8 -*-
"""Controllers for the python.mercury application."""
from tg.configuration import config
from sqlalchemy import asc, desc, text
import math
from sqlalchemy import create_engine
engine = create_engine(config['sqlalchemy.url'])
from myprojectname.model import DBSession
import json
import regex

class URLunicode():
    def __init___(self):
        pass

    def decode(self,payload):
        self.ec = {"%u00b4":"´","%u00c0": "À", "%u00c1": "Á", "%u00c2": "Â", "%u00c3": "Ã", "%u00c4": "Ä", "%u00c5": "Å",
                   "%u00c6": "Æ", "%u00c7": "Ç", "%u00c8": "È", "%u00c9": "É", "%u00ca": "Ê", "%u00cb": "Ë",
                   "%u00cc": "Ì", "%u00cd": "Í", "%u00ce": "Î", "%u00cf": "Ï", "%u00d1": "Ñ", "%u00d2": "Ò",
                   "%u00d3": "Ó", "%u00d4": "Ô", "%u00d5": "Õ", "%u00d6": "Ö", "%u00d8": "Ø", "%u00d9": "Ù",
                   "%u00da": "Ú", "%u00db": "Û", "%u00dc": "Ü", "%u00dd": "Ý", "%u00df": "ß", "%u00e0": "à",
                   "%u00e1": "á", "%u00e2": "â", "%u00e3": "ã", "%u00e4": "ä", "%u00e5": "å", "%u00e6": "æ",
                   "%u00e7": "ç", "%u00e8": "è", "%u00e9": "é", "%u00ea": "ê", "%u00eb": "ë", "%u00ec": "ì",
                   "%u00ed": "í", "%u00ee": "î", "%u00ef": "ï", "%u00f0": "ð", "%u00f1": "ñ", "%u00f2": "ò",
                   "%u00f3": "ó", "%u00f4": "ô", "%u00f5": "õ", "%u00f6": "ö", "%u00f8": "ø", "%u00f9": "ù",
                   "%u00fa": "ú", "%u00fb": "û", "%u00fc": "ü", "%u00fd": "ý", "%u00ff": "ÿ"}
        nv=payload
        keyword_number = regex.search("%u00", payload)
        if keyword_number is not None:
            keywords_found = regex.finditer("%u00", payload)
            for element in keywords_found:
                ini = element.start()
                key=payload[ini:ini+6]
                if key in self.ec:
                    value=self.ec[key]
                else:
                    value=""
                nv=nv.replace(key,value)
        return nv
class DynamicFilter(object):

    def __init__(self, sord=None,sidx=None,query=None, model_class=None, filter_condition=None):
        self.query = query
        self.model_class = model_class
        self.filter_condition = filter_condition
        self.sord=sord
        self.sidx=sidx

    def get_query(self):
        '''
        Returns query with all the objects
        :return:
        '''
        if not self.query:
            if self.sord == "asc":
                self.query = DBSession.query(self.model_class).order_by(asc(self.sidx))
            else:
                self.query = DBSession.query(self.model_class).order_by(desc(self.sidx))

        #self.query = self.session.query(self.model_class)
        return self.query


    def filter_query(self, query, filter_condition):
        '''
        Return filtered queryset based on condition.
        :param query: takes query
        :param filter_condition: Its a list, ie: [(key,operator,value)]
        operator list:
            eq for ==
            lt for <
            ge for >=
            in for in_
            like for like
            value could be list or a string
        :return: queryset
        '''

        if query is None:
            query = self.get_query()
        model_class =  self.model_class  # returns the query's Model
        for raw in filter_condition:
            try:
                key, op, value = raw
            except ValueError:
                raise Exception('Invalid filter: %s' % raw)
            column = getattr(model_class, key, None)
            if not column:
                raise Exception('Invalid filter column: %s' % key)
            if op == 'in':
                if isinstance(value, list):
                    filt = column.in_(value)
                else:
                    filt = column.in_(value.split(','))
            else:
                try:
                    attr = list(filter(
                        lambda e: hasattr(column, e % op),
                        ['%s', '%s_', '__%s__']
                    ))[0] % op
                except IndexError:
                    raise Exception('Invalid filter operator: %s' % op)
                if value == 'null':
                    value = None
                filt = getattr(column, attr)(value)
            query = query.filter(filt)
        return query


    def return_query(self):
        return self.filter_query(self.get_query(), self.filter_condition)

class jqgridDataGrabber(object):
    def __init__(self, currentmodel,key,filter,kwargs):
        self.model = currentmodel
        self.indexkey = key
        self.filter = filter
        self.kw=kwargs

    def loadGridTraffic(self):
        if self.kw['_search']=='false':
            selectedpage = int(self.kw['page'])
            dynamic_filtered_query_class = DynamicFilter(self.kw['sord'],self.kw['sidx'],query=None, model_class=self.model,filter_condition=self.filter)
            themodel = dynamic_filtered_query_class.return_query()
            pageIndex = int(self.kw['page']) - 1
            pageSize = int(self.kw['rows'])
            totalRecords = themodel.count()
            #print("Total Records:{}".format(totalRecords))
            totalPages = int(math.ceil(totalRecords / float(pageSize)))
            offset = (pageIndex) * pageSize
            window = themodel.offset(offset).limit(pageSize)
            records=[]
            fields=[]
            co = 0
            for rw in window:
                fields = []
                go = 0
                if go == 0:
                    records.append({self.indexkey:  str(getattr(rw, self.indexkey)), 'cell': fields})
                else:
                    co += 1
            #print(records)
        else:
            selectedpage = int(self.kw['page']) # 0; # get the requested page
            limit =  int(self.kw['rows']) # 50; #get how many rows we want to have into the grid
            sidx = self.kw['sidx'] #1; #get index row - i.e. user click to sort
            sord = self.kw['sord'] #"asc"; #// get the direction
            #print ("page:{} limit:{} sidx:{} sord:{}".format(selectedpage,limit,sidx,sord))
            operations={}
            operations['eq']="= '{}'"  # Equal
            operations['ne'] = "<> '{}'"  # Not Equal
            operations['lt'] = "< '{}'"  # Less Than
            operations['le'] = "<= '{}'"  # Less than or equal
            operations['gt'] = "> '{}'"  # Greater than
            operations['ge'] = ">= '{}'"  # Greater or equal
            operations['bw'] = "like '{}%'"  # Begins With
            operations['bn'] = "not like '{}%'"  # Does not begin with
            operations['in'] = "in ('{}')" # In
            operations['ni'] = "not in ('{}')"  # Not in
            operations['ew'] = "like '%{}'"  # Ends with
            operations['en'] = "not like '%{}'"  # Does not end with
            operations['cn'] = "like '%{}%'"  # Contains
            operations['nc'] = "not like '%{}%'"  # Does not contain
            operations['nu'] = "is null"  # is Null
            operations['nn'] = "is not null" # is not Null
            value=self.kw['searchString']
            where="WHERE {} {}".format(self.kw['searchField'],operations[self.kw['searchOper']].format(value))
            if len(self.filter)>0:
                where = where + " and " + self.filter[0][0] + operations[self.filter[0][1]].format(self.filter[0][2])
                #print("WHERE: {}".format(where))

            fields=self.model.__table__.columns
            myfields=""
            ndx=0
            pointer=0
            for item in fields:
                if item==self.indexkey:
                   ndx=pointer
                pointer=pointer+1
                myfields=myfields+item.name+","
            myfields=myfields[:-1]
            sql = "SELECT "+myfields+ " FROM "+self.model.__tablename__+" "+ where +" ORDER BY " + sidx + " "+ sord
            #print(sql)
            #print(ndx)
            query = text(sql)
            result = engine.execute(query)
            data = result.fetchall()
            if limit<0:
                limit=0
            start=(limit*selectedpage)-limit
            if start < 0:
                start=0
            totalRecords=0
            records = []
            pos=0
            for row in data:
                fields=[]
                for item in row:
                    fields.append(str(item))
                key=str(fields[ndx])
                if pos>=start and pos<=start+limit-1:
                    records.append({self.indexkey: key, 'cell': fields})
                totalRecords=totalRecords+1
                pos=pos+1

            if totalRecords>0:
                totalPages=int(math.ceil(totalRecords / float(limit)))
            else:
                totalPages=0

            if selectedpage>totalPages:
                selectedpage=totalPages
            #print("len records{}".format(len(records)))
            #print("Total pages:{} Start:{} Records:{}".format(totalPages,start,totalRecords))
            #print(records)
        return dict(total=totalPages, page=selectedpage, records=totalRecords, rows=records)

    def loadGrid(self):
        # for k,v in self.kw.items():
        #     print("{} : {} ".format(k,v))
        if self.kw['_search']=='false':
            selectedpage = int(self.kw['page'])
            dynamic_filtered_query_class = DynamicFilter(self.kw['sord'],self.kw['sidx'],query=None, model_class=self.model,filter_condition=self.filter)
            themodel = dynamic_filtered_query_class.return_query()
            pageIndex = int(self.kw['page']) - 1
            pageSize = int(self.kw['rows'])
            totalRecords = themodel.count()
            #print("Total Records:{}".format(totalRecords))
            totalPages = int(math.ceil(totalRecords / float(pageSize)))
            offset = (pageIndex) * pageSize
            window = themodel.offset(offset).limit(pageSize)
            records=[]
            fields=[]
            for rw in window:
                for columnlist in rw.__table__.columns:
                    column = getattr(rw, columnlist.name)
                    toc = str(type(column))
                    #print("Column name={} toc={}".format(column,toc))
                    if column is not None:
                        value=column
                        if toc == "<class 'bool'>":
                            if column is False:
                                value="0"
                            else:
                                value="1"
                        if toc == "<class 'datetime.datetime'>":
                            #print("DATE TIME!!")
                            value = column.strftime("%Y-%m-%d %H:%M:%S")
                            #print(value)
                        if toc == "<type 'str'>" or toc=="<class 'str'>":
                            utf8 = URLunicode()
                            value = utf8.decode(value)
                            value = value.replace('\r\n',' ')
                            value = value.replace('\n',' ')
                    else:
                        if toc == "<type 'str'>" or toc=="<class 'str'>":
                            value = u""
                        if toc == "<type 'unicode'>" or  toc == "<class 'unicode'>":
                            value=u""
                        if toc == "<type 'datetime.datetime'>" or toc == "<class 'datetime.datetime'>":
                            value=""
                        else:
                            value="0"
                            #print("loading: {} to {} type:{}".format(str(column), value, str(type(column))))
                    fields.append(value)
                records.append({self.indexkey:  str(getattr(rw, self.indexkey)), 'cell': fields})
                fields=[]
            #print(records)
        else:
            selectedpage = int(self.kw['page']) # 0; # get the requested page
            limit =  int(self.kw['rows']) # 50; #get how many rows we want to have into the grid
            sidx = self.kw['sidx'] #1; #get index row - i.e. user click to sort
            sord = self.kw['sord'] #"asc"; #// get the direction
            #print ("page:{} limit:{} sidx:{} sord:{}".format(selectedpage,limit,sidx,sord))
            operations={}
            operations['eq']="= '{}'"  # Equal
            operations['ne'] = "<> '{}'"  # Not Equal
            operations['lt'] = "< '{}'"  # Less Than
            operations['le'] = "<= '{}'"  # Less than or equal
            operations['gt'] = "> '{}'"  # Greater than
            operations['ge'] = ">= '{}'"  # Greater or equal
            operations['bw'] = "like '{}%'"  # Begins With
            operations['bn'] = "not like '{}%'"  # Does not begin with
            operations['in'] = "in ('{}')" # In
            operations['ni'] = "not in ('{}')"  # Not in
            operations['ew'] = "like '%{}'"  # Ends with
            operations['en'] = "not like '%{}'"  # Does not end with
            operations['cn'] = "like '%{}%'"  # Contains
            operations['nc'] = "not like '%{}%'"  # Does not contain
            operations['nu'] = "is null"  # is Null
            operations['nn'] = "is not null" # is not Null
            value=self.kw['searchString']
            where="WHERE {} {}".format(self.kw['searchField'],operations[self.kw['searchOper']].format(value))
            if len(self.filter)>0:
                where = where + " and " + self.filter[0][0] + operations[self.filter[0][1]].format(self.filter[0][2])
                #print("WHERE: {}".format(where))

            fields=self.model.__table__.columns
            myfields=""
            ndx=0
            pointer=0
            for item in fields:
                if item==self.indexkey:
                   ndx=pointer
                pointer=pointer+1
                myfields=myfields+item.name+","
            myfields=myfields[:-1]
            sql = "SELECT "+myfields+ " FROM "+self.model.__tablename__+" "+ where +" ORDER BY " + sidx + " "+ sord
            #print(sql)
            #print(ndx)
            query = text(sql)
            result = engine.execute(query)
            data = result.fetchall()
            if limit<0:
                limit=0
            start=(limit*selectedpage)-limit
            if start < 0:
                start=0
            totalRecords=0
            records = []
            pos=0
            for row in data:
                fields=[]
                for item in row:
                    #############print()
                    #print("loading: {} to {} type:{}".format(str(item), type(type(item))))
                    fields.append(item)
                key=str(fields[ndx])
                if pos>=start and pos<=start+limit-1:
                    records.append({self.indexkey: key, 'cell': fields})
                totalRecords=totalRecords+1
                pos=pos+1

            if totalRecords>0:
                totalPages=int(math.ceil(totalRecords / float(limit)))
            else:
                totalPages=0

            if selectedpage>totalPages:
                selectedpage=totalPages
            #print("len records{}".format(len(records)))
            #print("Total pages:{} Start:{} Records:{}".format(totalPages,start,totalRecords))
            #print(records)
        return dict(total=totalPages, page=selectedpage, records=totalRecords, rows=records)

    def loadDetail(self):
        my_filters = {self.indexkey: self.kw['id']}
        query = DBSession.query(self.model)
        for attr, value in my_filters.items():
            query = query.filter(getattr(self.model, attr) == value)
        window = query.all()
        records = []
        fields = []
        for rw in window:
            for column in rw.__table__.columns:
                #print(column.name)
                fields.append(getattr(rw, column.name))
            records.append({self.indexkey: str(getattr(rw, self.indexkey)), 'cell': fields})
            fields = []
        #print(records)
        return dict(rows=records)

    def updateGrid(self):
        if "oper" in self.kw:
            if self.kw['oper'] == "edit":
                print("edit")
                # print("id:{}".format(self.kw['id']))
                # for key, value in self.kw.iteritems():
                #     print "%s = %s" % (key, value)

                my_filters = {self.indexkey: self.kw['id']}
                query = DBSession.query(self.model)

                for attr, value in my_filters.items():
                    query = query.filter(getattr(self.model, attr) == value)
                item=query.first()
                if item is not None:
                    #print("None Edit")
                    for column in item.__table__.columns:
                        if column.name!=self.indexkey:
                            if column.name in self.kw:
                                if str(column.type) == "BOOLEAN":
                                    newvalue = True if self.kw[column.name]=="True" else False
                                else:
                                    newvalue =self.kw[column.name]
                                #print("updating: {} to {} type:{}".format(column.name, self.kw[column.name],str(column.type)))
                                setattr(item,column.name,newvalue)
                    DBSession.flush()
            if self.kw['oper'] == "add":
                item = self.model()
                #print("add")
                for column in item.__table__.columns:
                    if column.name in self.kw:
                        #print("{}={}".format(str(column.name),str(self.kw[column.name])))
                        if (self.indexkey==column.name):
                            pass
                        else:
                            setattr(item, column.name, self.kw[column.name])

                DBSession.add(item)
                DBSession.flush()

            if self.kw['oper'] == "del":
                my_filters = {self.indexkey: self.kw['id']}
                query = DBSession.query(self.model)
                for attr, value in my_filters.items():
                    query = query.filter(getattr(self.model, attr) == value)
                item=query.first()
                if item is not None:
                    DBSession.delete(item)
                    DBSession.flush()
            return dict(error="")

    def loadFilterGrid(self):
        if self.kw['_search'] == 'true':
            if self.kw['filters']!="":
                filters = json.loads(self.kw['filters'])
                rules=filters['rules']
                groupOperation=filters['groupOp']+" "
                fieldOperation=""
                size=len(rules)
                counter=0
                for item in rules:
                    counter=counter+1
                    fieldName=item['field']
                    fieldData=item['data']
                    if not (size > 1 and counter < size):
                        groupOperation=""
                    if item['op']=="cn":
                        fieldOperation = fieldOperation + fieldName+ " LIKE '%"+fieldData+"%' " +groupOperation
                selectedpage = int(self.kw['page'])  # 0; # get the requested page
                limit = int(self.kw['rows'])  # 50; #get how many rows we want to have into the grid
                sidx = self.kw['sidx']  # 1; #get index row - i.e. user click to sort
                sord = self.kw['sord']  # "asc"; #// get the direction
                where = "WHERE "+fieldOperation
                fields = self.model.__table__.columns
                myfields = ""
                ndx = 0
                pointer = 0
                for item in fields:
                    if item == self.indexkey:
                        ndx = pointer
                    pointer = pointer + 1
                    myfields = myfields + item.name + ","
                myfields = myfields[:-1]
                sql = "SELECT " + myfields + " FROM " + self.model.__tablename__ + " " + where + " ORDER BY " + sidx + " " + sord
                #print(sql)
                #print(ndx)
                query = text(sql)
                result = engine.execute(query)
                data = result.fetchall()
                if limit < 0:
                    limit = 0
                start = (limit * selectedpage) - limit
                if start < 0:
                    start = 0
                totalRecords = 0
                records = []
                pos = 0
                for row in data:
                    fields = []
                    for item in row:
                        fields.append(item)
                    key = str(fields[ndx])
                    if pos >= start and pos <= start + limit - 1:
                        records.append({self.indexkey: key, 'cell': fields})
                    totalRecords = totalRecords + 1
                    pos = pos + 1

                if totalRecords > 0:
                    totalPages = int(math.ceil(totalRecords / float(limit)))
                else:
                    totalPages = 0

                if selectedpage > totalPages:
                    selectedpage = totalPages
                    # print("len records{}".format(len(records)))
                    # print("Total pages:{} Start:{} Records:{}".format(totalPages,start,totalRecords))
                    # print(records)
                return dict(total=totalPages, page=selectedpage, records=totalRecords, rows=records)
        else:
            selectedpage = int(self.kw['page'])
            dynamic_filtered_query_class = DynamicFilter(self.kw['sord'],self.kw['sidx'],query=None, model_class=self.model,filter_condition=self.filter)
            themodel = dynamic_filtered_query_class.return_query()
            pageIndex = int(self.kw['page']) - 1
            pageSize = int(self.kw['rows'])
            totalRecords = themodel.count()
            #print("Total Records:{}".format(totalRecords))
            totalPages = int(math.ceil(totalRecords / float(pageSize)))
            offset = (pageIndex) * pageSize
            window = themodel.offset(offset).limit(pageSize)
            records=[]
            fields=[]
            return dict(total=totalPages, page=selectedpage, records=totalRecords, rows=records)

